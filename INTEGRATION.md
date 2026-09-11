# Connecting the two pipelines

The first connection is `neuro-attention/src/combined_pipeline.py`.

```text
Same recording, shared clock
  ├─ PVT preprocessing → 62 × 256 window → EEGNet → lapse score
  └─ AAD preprocessing → 960 × montage-size window ─┐
      two aligned 64 Hz speech envelopes ─────────┴→ talker decision → audio mixer
                                                     │
                         joint result ←──────────────┘
```

The base window covers the last 2 seconds and the AAD window the last 15 seconds. Both end at the same timestamp as the audio envelopes. The positive AAD lags introduce an approximately 0.4-second reconstruction edge; the bridge excludes that unsupported edge from correlation.

## Use in Python

Use one environment containing the base dependencies and add-on requirements. From `NOVA/`, make both source trees importable:

```sh
export PYTHONPATH="$PWD/base/src:$PWD/neuro-attention/src"
```

The API accepts separately prepared windows, not raw headset blocks:

```python
import numpy as np
from combined_pipeline import CombinedPipeline

pipeline = CombinedPipeline(
    "training-runs/full-eegnet/fold_1.pt",
    np.load("neuro-attention/results/personal_decoder.npy", allow_pickle=False),
    aad_channels=training_aad_channel_names,
)
result = pipeline.decide(
    lapse_window=pvt_window_uv,           # (62, 256), training electrode order
    lapse_channels=pvt_channel_names,
    lapse_sample_rate=128,
    lapse_units="uV",
    lapse_preprocessing="pvt_0.5_45Hz",
    lapse_end_time_s=end_time,
    aad_window=aad_window,                # (960, number of AAD electrodes)
    aad_channels=training_aad_channel_names,
    aad_sample_rate=64,
    aad_preprocessing="aad_1_9Hz_zscore",
    envelopes=two_bandpassed_envelopes,   # (2, 960), same clock as EEG
    aad_end_time_s=end_time,
    envelope_end_time_s=end_time,
)
print(result.to_dict())
mixed_block = pipeline.mix(talker_a_block, talker_b_block)
```

The variable names above represent data supplied by an acquisition/preprocessing adapter; they are not included sample files. Metadata checks cannot prove that a caller actually filtered or synchronized its input. Existing AAD `.npy` weights contain no electrode names; obtain the verified order from the training recording. Do not invent a channel mapping or upsample the 64 Hz signal to stand in for the base's broadband EEG.

## Run the available checks

From `NOVA/`, in an environment with numpy, scipy, torch, mne, and scikit-learn:

```sh
python -m unittest discover -s tests -v
```

These tests use temporary synthetic weights and signals. They exercise base checkpoint save/load, both inference branches, correlation-driven mixer behavior, and rejection of incorrect input metadata/timing. Passing them proves software wiring, not physiological performance.

## To complete a real demo

1. Obtain the PVT dataset or a compatible trained EEGNet checkpoint. The training script now exports a checkpoint per held-out subject. Do not choose the best fold on test scores as a deployment selection strategy.
2. Obtain AAD recordings, decoder weights, and the electrode order used to train those weights.
3. Capture sufficiently broadband EEG with named electrodes and timestamps. Build separate preprocessing branches from that original recording, matching each model's training transform. The two existing datasets do not by themselves provide a shared simultaneous recording.
4. Replace the add-on's LSL reader with a timestamp-aware source, align audio and EEG, and feed completed windows into this bridge.
5. Connect the joint result to the browser UI, and evaluate the lapse model on the listening task before letting its score change audio gain.

No data or trained checkpoints were present in the copied base `datasets/` or `models/` directories. The live EEG adapter and UI connection remain future work; the current prototype is for prepared, aligned windows.
