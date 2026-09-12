# ATTUNE UI Integration Contract

## Endpoint

The UI polls the same-origin endpoint `GET /state` with `cache: "no-store"`.

## Current fields

The current payload fields are:

- `running`
- `done`
- `t`
- `attended`
- `gain_a_db`
- `gain_b_db`
- `corr_a`
- `corr_b`
- `correct_frac`
- `eeg_source`
- `audio_source`
- `mode`
- `eeg`

Optional forward-compatible field:

- `lapse_score`

Scientific numeric values must be actual finite JavaScript numbers. The frontend does not coerce numeric strings. `lapse_score` must be in the inclusive range 0..1; missing, malformed, nonfinite, or out-of-range values are unavailable. The frontend never infers a lapse score from EEG, correlations, gains, attended talker, accuracy, or elapsed time.

## Availability and demo behavior

Real Mode shows unavailable values when the backend is warming up, unreachable, malformed, or does not provide the optional lapse score. Stale responses are ignored and missing history observations are shown as gaps.

Demo Mode is deterministic and clearly labeled simulated. Its values must not be interpreted as real EEG measurements or participant data.

Real signal-quality and artifact fields do not currently exist in the runtime pipeline. Signal quality and artifact status are simulated in Demo Mode only and remain unavailable in Real Mode.

`CombinedPipeline` already produces `lapse_score` internally, but connecting that result to live `/state` is a separate integration task. Do not change model or preprocessing behavior merely to use this UI.
