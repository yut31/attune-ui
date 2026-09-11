# Training progress and evaluation feedback

Both training scripts now accept the same controls and save reports as they run.

## Why runs were long

Each script trains a new model for every held-out subject. For N subjects, EEGNet defaults to 10 × N training epochs across all folds; EEGWaveNet defaults to 30 × N. A full run is useful for evaluation but expensive for checking a code change.

Previously, the scripts selected CUDA or CPU only. Apple GPU use can now be requested with `--device mps`; it is an option to benchmark, not a guaranteed speedup. The default `auto` still selects CUDA when available, otherwise CPU.
## Preparing raw recordings

The PVT builder now saves the metadata required by the checkpoint writer and accepts the raw dataset location:

```sh
export PYTHONPATH="$PWD/base/src"
python base/scripts/dataproc/build_pvt.py \
  --dataset-root /absolute/path/to/COG-BCI \
  --out base/datasets/COG-BCI/outputs
```

Pass `base/datasets/COG-BCI/outputs/PVT_128Hz_DefaultPipe.pt` to the trainer. Recordings must follow `sub-*/ses-*/eeg/PVT.set` with their associated EEG data files.

## Quick development run in VS Code

In a terminal starting at `NOVA/`, with the base dependencies installed:

```sh
export PYTHONPATH="$PWD/base/src"
python base/scripts/training/trainEEGNet.py \
  --dataset /absolute/path/to/prepared_PVT.pt \
  --epochs 2 --max-folds 1 --device cpu \
  --out training-runs/quick-check
```

Replace the dataset path with your actual prepared checkpoint. No real training dataset is included in this workspace. The output directory must be new, to avoid overwriting a previous run.

`--max-folds 1` holds out one subject and trains on the other subjects. It does not randomly mix the test subject into training. Its score is a partial development check, not full LOSO performance. Lower epoch counts also change the training budget and must be reported.

## Full evaluation

Omit `--max-folds`, and use the intended epoch budget:

```sh
python base/scripts/training/trainEEGNet.py \
  --dataset /absolute/path/to/prepared_PVT.pt \
  --epochs 10 --out training-runs/full-eegnet
```

Other controls: `--batch-size 32`, `--seed 42`, `--threads 4`, and `--device cpu|cuda|mps|auto`. Thread count, batch size, and GPU choice should be timed on the actual machine and dataset. Larger batches can affect model quality. No hardware speedup has been measured here.

## Feedback you receive

- Current fold, epoch, and batch; elapsed time and an estimate of the remaining training time in that fold, printed about every five seconds or at a completed epoch. Estimates exclude final test evaluation and later folds.
- Training loss saved after every epoch to `fold_N.json`.
- After training: held-out class precision, recall, F1, support, and a confusion matrix. Matrix rows are true classes and columns are predictions, ordered usual response then slowest session decile.
- A checkpoint `fold_N.pt` and a running `summary.json` that explicitly records whether the requested evaluation covers all subjects.
- `settings.json` records the dataset, seed, device, and training settings.

A low training loss alone does not prove useful generalization. The positive label is a slow response relative to that session, not a verified real-world attention diagnosis. Inspect recall and precision for that class as well as macro F1.

The held-out subject is evaluated once at the end of training. EEGWaveNet previously selected its best epoch using test scores; that leakage is removed. Early stopping is deliberately not based on the test subject. A future early-stopping workflow needs a separate validation split within the training subjects.

## EEGWaveNet compatibility issue

The current upstream EEGWaveNet has convolution branches that require at least 320 input samples. The standard PVT windows contain 256. The script now catches this immediately with a clear error rather than failing inside a convolution. EEGNet supports the standard 256-sample windows. Do not stretch or pad EEG just to bypass this architectural mismatch; revise and validate the architecture separately.

The shared CLI works for EEGWaveNet with compatible inputs, but its exported checkpoint is not an EEGNet checkpoint and cannot be loaded by the combined pipeline's LapsePredictor.

## Verification

Both CLIs were exercised on synthetic multi-subject checkpoints with one training epoch and one held-out fold. Checks covered saved class metrics, confusion-matrix counts, checkpoints, and partial-run labeling. This verifies the workflow, not real-data accuracy or speed gains.
