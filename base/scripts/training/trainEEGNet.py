from nova2026.training_feedback import arguments, TrainingFeedback, write_json
from nova2026.architecture.cnn import EEGNet
from nova2026.architecture.lossfun import FocalLoss
from nova2026.config import DATA_DIR, PROJECT_ROOT
from nova2026.data.channels import EEG_CHANNELS
from nova2026.inference import save_checkpoint
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import f1_score, accuracy_score
import torch
import numpy as np

ROOT = DATA_DIR / "COG-BCI"
DATASET = ROOT / "PVT_data_2000ms_200ms.pt"

BATCH_SIZE = 32
EPOCHS = 10
LR = 1e-3
K = 90

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def max_norm_(param, max_value=1.0, eps=1e-8):
    """Applies max-norm constraint to the parameter."""
    with torch.no_grad():
        norm = param.norm(2)
        if norm > max_value:
            param.mul_(max_value / (norm + eps))


def load_data(path=DATASET):
    checkpoint = torch.load(path, weights_only=False)
    data = checkpoint["data"]
    labels = checkpoint["labels"]
    meta = checkpoint["metadata"]

    subjects = meta[:, 0]
    rt = meta[:, 2].astype(float)
    return data, labels, subjects, rt


def train_one_fold(x_train, y_train, x_val, y_val, checkpoint_path=None, report_path=None):
    x_train = torch.as_tensor(x_train, dtype=torch.float32)
    y_train = torch.as_tensor(y_train, dtype=torch.long)
    x_val = torch.as_tensor(x_val, dtype=torch.float32)
    y_val = torch.as_tensor(y_val, dtype=torch.long)
    train_dataset = TensorDataset(x_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_dataset = TensorDataset(x_val, y_val)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = EEGNet(chn=62).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = FocalLoss(gamma=3.0, alpha=[1, 3.5], reduction="mean")
    # criterion = torch.nn.CrossEntropyLoss()

    # Fixed epoch count: the held-out subject must not select an epoch.

    print(f"Train samples: {len(x_train)}, Test samples: {len(x_val)}")

    feedback = TrainingFeedback(EPOCHS, len(train_loader), report_path)

    for epoch in range(1, EPOCHS + 1):
        # ----- Training -----
        model.train()
        train_loss = 0.0
        for batch_number, (batch_data, batch_target) in enumerate(train_loader, 1):
            batch_data, batch_target = batch_data.to(DEVICE), batch_target.to(DEVICE)

            optimizer.zero_grad(set_to_none=True)
            outputs = model(batch_data)
            loss = criterion(outputs, batch_target)
            loss.backward()
            optimizer.step()

            # max-norm
            with torch.no_grad():
                max_norm_(model.depthwise_conv.weight, max_value=1.0)
                max_norm_(model.classifier.weight, max_value=0.25)

            train_loss += loss.item() * batch_data.size(0)
            feedback.batch(epoch, batch_number)

        train_loss /= len(x_train)

        print(f"Epoch {epoch:02d}/{EPOCHS} | Train Loss: {train_loss:.4f}", flush=True)
        feedback.epoch(epoch, train_loss)

    # Evaluate the held-out subject once, after the predetermined training budget.
    model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for batch_data, batch_target in test_loader:
            outputs = model(batch_data.to(DEVICE))
            all_preds.extend(outputs.argmax(dim=1).cpu().numpy())
            all_targets.extend(batch_target.numpy())
    score = feedback.finish(all_targets, all_preds)
    print(f"Held-out F1: {score:.4f} | Accuracy: {accuracy_score(all_targets, all_preds):.4f}")
    if checkpoint_path is not None:
        save_checkpoint(model, checkpoint_path, EEG_CHANNELS)
    return score


def main():
    global EPOCHS, BATCH_SIZE, DEVICE
    args = arguments(DATASET, EPOCHS, BATCH_SIZE)
    EPOCHS, BATCH_SIZE, DEVICE = args.epochs, args.batch_size, torch.device(args.device)
    print(f"Device: {DEVICE} | epochs per fold: {EPOCHS} | reports: {args.out}", flush=True)
    # Data Loading
    data, labels, sub_names, rt = load_data(args.dataset)
    n_trials = data.shape[0]
    print(f"Total trials: {n_trials}, Total subjects: {len(np.unique(sub_names))}")

    # Prepare LOSO
    unique_subs = np.unique(sub_names)
    fold_results = []
    if len(unique_subs) < 2:
        raise ValueError("At least two subjects are required for held-out evaluation")
    test_subjects = unique_subs[:args.max_folds] if args.max_folds else unique_subs
    if len(test_subjects) < len(unique_subs):
        print("DEVELOPMENT RUN: subset of folds; this is not a full LOSO result.", flush=True)

    for fold_number, test_sub in enumerate(test_subjects, 1):
        print(f"Fold {fold_number}/{len(test_subjects)}", flush=True)
        print(f"\n=== Fold: test subject = {test_sub} ===")

        # Split data based on subject
        test_trial_idx = np.where(sub_names == test_sub)[0]
        train_trial_idx = np.where(sub_names != test_sub)[0]

        selected_train_trials = []
        train_subs = np.unique(sub_names[train_trial_idx])
        # For each subject in the training set
        for sub in train_subs:
            sub_idx = np.where(sub_names == sub)[0]
            sub_labels = labels[sub_idx].numpy()
            sub_rt = rt[sub_idx]

            pos_local_all = np.where(sub_labels == 1)[0]
            neg_local_all = np.where(sub_labels == 0)[0]

            # Cap BOTH classes at K — don't let one class flood the training set
            k_pos = min(K, len(pos_local_all))
            k_neg = min(K, len(neg_local_all))

            pos_local = pos_local_all[
                np.argsort(sub_rt[pos_local_all])[-k_pos:]
            ]  # slowest RT
            neg_local = neg_local_all[
                np.argsort(sub_rt[neg_local_all])[:k_neg]
            ]  # fastest RT

            selected_local = np.concatenate([pos_local, neg_local])
            selected_train_trials.extend(sub_idx[selected_local])

        selected_train_trials = np.array(selected_train_trials)

        print(
            "Train label distribution:",
            dict(
                zip(
                    *np.unique(
                        labels[selected_train_trials].numpy(), return_counts=True
                    )
                )
            ),
        )

        # Shape data and labels into windows for training and testing
        train_data_windows = data[selected_train_trials].reshape(-1, 62, 256)
        train_labels_windows = np.repeat(labels[selected_train_trials], 1)
        test_data_windows = data[test_trial_idx].reshape(-1, 62, 256)
        test_labels_windows = np.repeat(labels[test_trial_idx], 1)

        print(
            "Test label distribution:",
            dict(zip(*np.unique(test_labels_windows, return_counts=True))),
        )

        X_train = train_data_windows
        y_train = train_labels_windows
        X_test = test_data_windows
        y_test = test_labels_windows

        score = train_one_fold(
            X_train, y_train, X_test, y_test,
            checkpoint_path=args.out / f"fold_{fold_number}.pt",
            report_path=args.out / f"fold_{fold_number}.json",
        )
        fold_results.append(score)
        write_json(args.out / "summary.json", {
            "status": "complete" if fold_number == len(test_subjects) else "running",
            "full_loso": len(test_subjects) == len(unique_subs),
            "total_subjects": len(unique_subs), "requested_folds": len(test_subjects),
            "subjects": [str(x) for x in test_subjects[:fold_number]],
            "macro_f1": fold_results, "mean_macro_f1": float(np.mean(fold_results))})

    # Outputs
    print("\n================ Completed Fold Results ================")
    for sub, f1 in zip(test_subjects, fold_results):
        print(f"Subject {sub}: F1 = {f1:.4f}")
    mean_f1 = np.mean(fold_results)
    std_f1 = np.std(fold_results)
    print(f"Mean F1: {mean_f1:.4f} ± {std_f1:.4f}")


if __name__ == "__main__":
    main()
