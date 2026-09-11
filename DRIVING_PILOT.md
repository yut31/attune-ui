# Public EEG training pilot

This run uses **real public EEG** from Cao, Chuang, King & Lin (2019), *Multi-channel EEG recordings during a sustained-attention driving task*.

- [Original dataset, version 5](https://doi.org/10.6084/m9.figshare.6427334.v5)
- [Dataset paper](https://doi.org/10.1038/s41597-019-0027-4)
- [NEMAR conversion and documented event metadata](https://github.com/nemarDatasets/nm000275)
- License: CC BY 4.0. This pilot samples and preprocesses the authors' original recordings; it is not an author-endorsed benchmark.

## What the model learns

It predicts whether a steering reaction belongs to the slowest 10% within that person's recording, from EEG **before** the lane-departure event. That is an experimental slow-response target. It is not a validated detector of attention lapses during conversations and does not identify which talker is attended.

COG-BCI, the dataset originally referenced by the project, was unavailable from this environment after multiple server timeouts. This accessible driving dataset provides documented reaction-time events relevant to sustained attention, but the two tasks and electrode setups are different.

## Fixed pilot protocol

- Select the first filename in alphabetical order for each of the 27 people, without looking at outcomes.
- Select up to 40 eligible trials per person using a fixed random seed, uniformly across that recording and without balancing by the target label.
- Define the slowest-decile target using each recording's paired deviation and steering-response events. Unmatched triggers are excluded.
- Fetch just the required signal windows using validated HTTP byte ranges from the uncompressed MATLAB data. Save source file identifiers and per-range SHA-256 hashes. Full original-file MD5 checksums are recorded from the source manifest but cannot be revalidated from partial downloads.
- Exclude the two mastoid reference channels and the vehicle-position channel. Train only on the 30 scalp EEG channels; verify the source channel order for every selected recording.
- Use six seconds of pre-event context ending 100 ms before deviation onset. Apply a fourth-order 0.5–45 Hz Butterworth bandpass, resample to 128 Hz, and retain the final two seconds (256 samples). No post-event response signal enters the EEG window.
- Reject nonfinite windows, flat channels, and windows with a channel peak-to-peak amplitude over 500 microvolts. Record exclusions.
- Split people, not windows: 17 training people, 5 validation people, and 5 final-test people. A person cannot appear in more than one split.
- Calculate normalization statistics only on training people. Train the existing EEGNet architecture with a 30-channel input, focal loss, and a fixed seed. Select the epoch by validation macro F1, up to 30 epochs, stopping after six epochs without improvement.
- Evaluate the test people once. Compare with always predicting the usual-response class. Save per-class metrics and the confusion matrix, not just overall accuracy.

This is a small pilot sampling of the dataset. It is not full leave-one-subject-out cross-validation, and uncertainty is large with five test people. A weak score remains a weak score; the held-out set must not be used to tune a more flattering result.

## Files

- `base/datasets/driving-attention/`: source manifest, extracted windows, sampling metadata, and range caches (Git-ignored).
- `base/scripts/dataproc/prepare_driving_pilot.py`: reproducible preparation.
- `base/scripts/training/train_driving_pilot.py`: training and held-out evaluation.
- `training-runs/driving-pilot-20260910/`: model, learning curves, reports, and predictions, produced after preparation completes.
- `base/src/nova2026/driving_inference.py`: separate inference loader for this task.

The original PVT predictor and the auditory decoder are not silently replaced. This model requires its own electrode order and preprocessing and must be evaluated on the actual headset before any live use.

## Reproduce

From the NOVA directory, using an environment with the base dependencies:

```sh
export PYTHONPATH="$PWD/base/src"
python base/scripts/dataproc/prepare_driving_pilot.py
python base/scripts/training/train_driving_pilot.py
```

The manifest and copied event tables must be present under the dataset folder. The trainer refuses to overwrite an existing run directory. The downloader reuses its window cache; it does not need the 7.9 GB full-recording download.
