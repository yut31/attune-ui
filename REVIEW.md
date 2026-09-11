# Code review and first integration

Reviewed the local NOVA2026 copy and the neuro-attention add-on. Findings below are from code inspection and the regression checks in `tests/test_combined.py`; no real EEG accuracy or hardware performance was measured.

## Update on September 9, 2026

The base has been refreshed to `4867db7`. The findings below describe our earlier review and retained local fixes. The patched old labeler moved to `base/scripts/legacy/labelPVT.py`; upstream now provides `build_pvt.py`. New upstream code has not received a full review. See [the current guide](PROJECT_GUIDE.md) for known compatibility issues.

## Findings

| Priority | Mistake / consequence | Status |
| --- | --- | --- |
| High | `base/src/nova2026/config.py` found the nearest `.git` directory, so after the folder reorganization it resolved datasets relative to `New project/`, outside `NOVA/base/`. This was introduced by the combined layout. | Fixed: locate the package using its `pyproject.toml` and source directory. |
| High | `base/scripts/dataproc/labelPVT.py` used `trials[-n:]` with `n = int(count * 0.1)`. For 1–9 trials, `n` is zero and `[-0:]` selects every trial as a lapse. | Fixed: skip sessions with fewer than 10 qualified trials. Empty annotations and out-of-bounds windows are also handled. |
| High | `base/scripts/training/trainEEGNet.py` chose the best epoch on the held-out test subject and reported that maximum as LOSO performance. Test labels were being used for model selection. | Fixed: train for the preset epoch count and evaluate the held-out subject once. Any future tuning should use a separate training-subject validation split. Previous reported scores need recomputation. |
| High | The same training script created `best_model_state` but never saved or returned it. The base had no usable inference artifact for the add-on. | Fixed: export each final fold model, with channel order, rate, units, and class meaning, under `base/models/`. No real model has been trained in this session. |
| High | `neuro-attention/src/eeg_sources.py`, `LSLEEG.read`, drops LSL timestamps, resamples every small chunk independently, inserts zeros on underrun, and returns `None` on a temporary empty pull (the demo treats that as end of stream). EEG can become misaligned with audio or stop the demo. | Open: needs a timestamp-aware capture buffer and continuous resampling, followed by hardware validation. The new connection does not use this reader. |
| Medium | `neuro-attention/src/live_demo.py`, `engine`, loads subject `.mat` files and stimulus envelopes before checking live mode or a supplied decoder. A live headset + microphones + trained decoder still requires the replay dataset. | Open: separate live initialization from replay initialization. |
| High for integration | Base input is ordered 62-channel, 128 Hz, 0.5–45 Hz EEG in microvolts; AAD input is typically 64-channel, 64 Hz, 1–9 Hz EEG with per-channel standardization. Passing one model's input/output straight into the other is incompatible. | Added an explicit, checked interface for separate aligned windows. Raw acquisition and preprocessing are still caller responsibilities. |

## Meaning of the base output

The positive training label is the slowest 10% of reaction times within a session. The exported score refers to that label. It is not a calibrated probability of a general attention lapse during conversation. Applying it to auditory listening requires evaluation on appropriate recordings.

## What is connected now

`neuro-attention/src/combined_pipeline.py` loads the base EEGNet checkpoint and the add-on's backward decoder. It checks the two input contracts and shared end timestamp, runs both, returns a joint decision, and exposes the existing audio mixer. The lapse score is reported alongside the talker choice; it does not change the gain policy.

This is a tested Python integration prototype. The existing browser demo is not yet wired to it. See `INTEGRATION.md` for how to call it and what is needed to connect real inputs.
