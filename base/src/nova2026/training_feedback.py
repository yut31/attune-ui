"""Shared CLI options and persistent feedback for the training scripts."""
import argparse
import json
from pathlib import Path
import time

import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix, f1_score


def arguments(dataset, epochs, batch_size):
    parser = argparse.ArgumentParser(description='Train with progress and saved evaluation feedback.')
    parser.add_argument('--dataset', type=Path, default=dataset)
    parser.add_argument('--epochs', type=int, default=epochs)
    parser.add_argument('--batch-size', type=int, default=batch_size)
    parser.add_argument('--max-folds', type=int, help='Development only: limit held-out subjects')
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda', 'mps'], default='auto',
                        help='auto preserves CUDA/CPU selection; try mps explicitly on Apple Silicon')
    parser.add_argument('--threads', type=int, help='CPU thread count to benchmark; unset keeps PyTorch default')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--out', type=Path, default=Path('training-runs') / time.strftime('%Y%m%d-%H%M%S'))
    args = parser.parse_args()
    for name in ('epochs', 'batch_size', 'max_folds', 'threads'):
        value = getattr(args, name)
        if value is not None and value < 1:
            parser.error(f'--{name.replace("_", "-")} must be positive')
    if not args.dataset.is_file():
        parser.error(f'Dataset not found: {args.dataset}. Supply your prepared PVT .pt file with --dataset.')
    device = args.device
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device == 'cuda' and not torch.cuda.is_available():
        parser.error('CUDA is not available on this machine')
    if device == 'mps' and not torch.backends.mps.is_available():
        parser.error('MPS is not available in this Python environment')
    args.device = device
    if args.threads:
        torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    args.out.mkdir(parents=True, exist_ok=False)
    write_json(args.out / 'settings.json', {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()})
    return args


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


class TrainingFeedback:
    def __init__(self, epochs, batches, report_path=None):
        self.epochs = epochs
        self.batches = batches
        self.report_path = Path(report_path) if report_path else None
        self.start = time.perf_counter()
        self.last_print = self.start
        self.history = []

    def batch(self, epoch, batch):
        now = time.perf_counter()
        if now - self.last_print >= 5 or batch == self.batches:
            completed = (epoch - 1) * self.batches + batch
            remaining = (now - self.start) / completed * (self.epochs * self.batches - completed)
            print(f'Epoch {epoch}/{self.epochs} | batch {batch}/{self.batches} | '
                  f'elapsed {now-self.start:.1f}s | estimated training time left {remaining:.1f}s', flush=True)
            self.last_print = now

    def epoch(self, epoch, loss):
        self.history.append({'epoch': epoch, 'train_loss': float(loss),
                             'elapsed_s': time.perf_counter() - self.start})
        if self.report_path:
            write_json(self.report_path, {'status': 'training', 'history': self.history})

    def finish(self, targets, predictions):
        result = {
            'status': 'complete', 'elapsed_s': time.perf_counter() - self.start,
            'history': self.history,
            'class_names': ['usual_response', 'slowest_session_decile'],
            'confusion_matrix': confusion_matrix(targets, predictions, labels=[0, 1]).tolist(),
            'classification_report': classification_report(
                targets, predictions, labels=[0, 1],
                target_names=['usual_response', 'slowest_session_decile'],
                output_dict=True, zero_division=0),
        }
        score = f1_score(targets, predictions, labels=[0, 1], average='macro', zero_division=0)
        print(f'Held-out macro F1: {score:.4f} | confusion matrix (rows=true, columns=predicted): '
              f'{result["confusion_matrix"]}', flush=True)
        if self.report_path:
            write_json(self.report_path, result)
        return score
