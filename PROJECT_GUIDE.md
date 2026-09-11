# NOVA — combined project guide

Updated from both public repositories on **September 9, 2026**.

Open `NOVA.code-workspace` in VS Code. This guide combines the two project READMEs, with links adjusted for the combined folder. The sections below retain their original project-specific instructions and claims; those claims have not been independently reproduced here.

## Workspace map

| Location | Purpose |
| --- | --- |
| `base/src/nova2026/` | Base EEG models, loaders, and preprocessing pipeline |
| `base/scripts/dataproc/` | Latest PVT/rest builders and engagement analysis |
| `base/scripts/training/` | EEGNet and EEGWaveNet training |
| `base/documents/engagement_zscoring.pdf` | New engagement and z-scoring document |
| `base/documents/typst/` | Editable source documents and figures |
| `neuro-attention/src/` | Auditory decoder, audio mixer, and demo |
| `neuro-attention/docs/` | Add-on project explanation and build-day notes |
| `neuro-attention/src/combined_pipeline.py` | Our prepared-window integration prototype |

## Current status and local changes

- Base source: `4867db7e198f26f9fa12d0d1260d3e5256eb0aeb`.
- Add-on source: `6054e496738594877d9c068db837b64d79b19dfe`, subfolder `neuro-attention-reorganized`.
- Dataset-root fix, held-out evaluation fix, checkpoint export, and integration prototype are preserved.
- Upstream replaced `labelPVT.py` with `build_pvt.py`; our patched old labeler is retained under `base/scripts/legacy/` for the previous dataset workflow and regression checks.
- The missing `data_type` field in `build_pvt.py` has been fixed, and the builder now has `--dataset-root` and `--out` options. Its output can be supplied to the trainer with `--dataset`. Both training scripts now have progress reports, configurable run budgets, and final-only held-out evaluation; see [training instructions](TRAINING.md). EEGWaveNet still needs an architecture adjustment for standard 256-sample windows.
- Real datasets and trained checkpoints are still needed. The browser demo is not yet connected to the combined model interface.

Read [the code review](REVIEW.md) and [integration guide](INTEGRATION.md) for the tested connection and its limits. The upstream instructions below can lag behind the newest source files; use the status notes above when choosing the preprocessing workflow.

## Training and evaluation

See [TRAINING.md](TRAINING.md) for short development runs, device selection, progress updates, and saved evaluation reports.

## Working in VS Code

Open the NOVA folder or its workspace file. Edit the files here; the original separate checkout is unchanged. This is a local snapshot plus our edits, not an automatic sync with GitHub. No changes have been pushed.

Each component keeps its own dependency setup. Run base commands from `base/`, and add-on commands from `neuro-attention/`. The integration tests need an environment containing the dependencies of both.

## Base project documentation

### NOVA2026

NOVA Buildathon 2026 project: EEG-based attention-lapse detection using a passive BCI approach.

#### Folder structure

```
NOVA2026/
├── datasets/     Raw datasets (git-ignored)
├── documents/    Learning material (PDFs) + typst sources
├── references/   Reference PDFs
├── models/       Saved models (git-ignored)
├── scripts/      Development scripts (scratch / experiments)
├── src/          Python code
├── refs.bib      Bibliography (BibTeX)
└── README.md
```

| Folder | Purpose |
| --- | --- |
| `src/` | **Reusable code goes here.** Organize it into subpackages. |
| `scripts/` | **Development / experimental scripts go here.** Anything still in scratch development (data exploration, prototyping, one-off runs) lives in `scripts/`, organized into subfolders per topic. |
| `datasets/` | **Put raw datasets here.** The folder already exists and is the recommended location. Keep raw data intact (`.set`/`.fdt`, `.cnt`, behavioral logs, channel locations). |
| `models/` | **Saved models / checkpoints go here.** This folder is git-ignored so large weights never get committed. |
| `documents/` | Handouts, challenge briefs, and learning notes (PDF), plus their `typst/` sources. |
| `references/` | Reference papers / device documentation (e.g. `attentivU.pdf`). |
| `refs.bib` | Bibliography — see below. |

> Note: `datasets/*` and `models/*` are git-ignored (only their `.gitkeep` is tracked), so large raw data and weights never get committed.

#### Setup the environment

> **Before running `uv sync`:** if you want the **CUDA build of PyTorch**, uncomment the
> `[tool.uv.sources]` / `[[tool.uv.index]]` `pytorch-cu132` block at the top of `pyproject.toml`.
> Leave it commented if you want a CPU-only install.

1. **Create the virtual environment** (only once):
   ```
   python -m venv .venv
   ```
2. **Activate it**:
   - Windows (cmd/PowerShell): `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
3. **Install the package** in editable mode — this also installs the runtime dependencies (`mne`, `numpy`, `scipy`, `matplotlib`, `pandas`, `torch`, `scikit-learn`, `mne-lsl`) declared in `pyproject.toml`:
   ```
   pip install uv
   uv sync
   ```

Requires Python >= 3.12. The `.venv/` folder is git-ignored, so it never gets committed.

#### Where to write code

- Put reusable Python modules under `src/` (e.g. `src/nova2026/data/`, `src/nova2026/architecture/`).
- Keep it importable: `from nova2026.data.mne_reader import ...`
- Put development / experimental scripts in `scripts/`, organized into subfolders (e.g. `scripts/dataproc/`, `scripts/training/`). Move code here into `src/nova2026/` once it stabilizes.

#### Where to put datasets

- Use `datasets/<name>/` — the folder is already set up for this, and it's excluded from git so the large files stay local.
- Don't modify or reorganize the raw files; do preprocessing/cleaning in code instead.
- Save trained models / checkpoints under `models/` (also excluded from git).

#### References (`refs.bib`)

All citations live in the BibTeX file `refs.bib` at the repo root. Whenever you read or use a source, add one entry per source and cite it in the docs via its key (e.g. `@hinss_2022_6874129`).

##### Getting a BibTeX entry online

Most sources give you a ready-made BibTeX entry via a **Cite / Citation** button, select `BibTex` option. Then just paste the entry into `refs.bib`, keeping a unique, descriptive key.


## Add-on documentation

### neuro-attention

Neuro-steered hearing: read which of two talkers a listener is attending to from
their EEG, and amplify that talker in real time.

**Start here:** [`docs/PROJECT.md`](neuro-attention/docs/PROJECT.md) — the full explanation, product pitch,
viability results, and demo architecture in one document.

**Status:** viability proven on real data (mean 82% at a 60 s window, up to 90%);
real-time demo runs today with no hardware via EEG replay.

#### Layout

```
neuro-attention/
├── README.md              # this file
├── requirements.txt
├── run_live_demo.command  # double-click launcher (macOS) for the live demo
├── render_video.command   # double-click launcher to make the MP4
│
├── docs/
│   ├── PROJECT.md         # ⭐ full write-up: pitch + method + results + demo
│   ├── NOVA_neuro_steered_hearing.pdf  # PROJECT.md, as a PDF
│   ├── START_HERE.txt     # plain-text quickstart
│   ├── BUILD_DAY.md       # exactly what's tested vs. what to integrate on the day
│   └── GIT_INSTRUCTIONS.md
│
├── src/
│   ├── config.py          # ALL settings (rates, band, lags, ridge, demo gains…)
│   │
│   │   # --- viability analysis ---
│   ├── envelopes.py       # speech envelopes from the stimulus WAVs (cached)
│   ├── dataset.py         # load_kuleuven_subject(): EEG + attended/ignored envelopes
│   ├── decoder.py         # backward decoder, LOO cross-validation, realtime decoder
│   ├── run_viability.py   # CLI: decode all subjects -> results.json / .csv / .png
│   ├── verify.py          # controls: r_attended>r_ignored, mismatched-audio null
│   │
│   │   # --- real-time demo (the "feedback" side) ---
│   ├── audio_sources.py   # FileSource (two tracks) | MicSource (two clip-ons)
│   ├── eeg_sources.py     # ReplayEEG (recorded) | LSLEEG (ANT Neuro via mne-lsl)
│   ├── attention_mixer.py # smoothed, ramping gain controller (the core feedback)
│   ├── demo_realtime.py   # headless engine: wav render or live playback
│   │
│   │   # --- the demo front-end ---
│   ├── live_demo.py       # ⭐ live browser UI + audio engine (mics / files, headphones)
│   ├── ui.html            # the live demo web page (two talker cards, meters)
│   ├── render_demo.py     # render a shareable MP4 of the demo
│   ├── pretrain_generic.py # build a zero-calibration "generic" decoder from several people
│   └── calibrate.py       # personalize a decoder for one listener (stronger, ~3 min)
│
└── results/               # accuracy curve, demo video (mp4), demo audio, lock-on plot, csv
```

All the `.py` files in `src/` are still flat siblings of each other — moving them together here
didn't require changing a single `import` statement. Run them as `python src/<name>.py` from
this folder (the launchers already do this); output still lands in the top-level `results/`.

#### The demo front-end

The showable demo is `live_demo.py`: it opens a browser page with two "Talker" cards
where the one the listener is attending to lights up and is amplified, driven live by
the decoder. Runs today on any laptop with recorded EEG — no headset needed.

```bash
### double-click run_live_demo.command, or:
python src/live_demo.py --data-dir /path/to/AAD                 # recorded EEG + two tracks
python src/live_demo.py --data-dir /path/to/AAD --audio file --files A.wav B.wav
python src/live_demo.py --data-dir /path/to/AAD --audio mic     # two clip-on mics
python src/live_demo.py --data-dir /path/to/AAD --eeg lsl --audio mic   # build day, live
python src/render_demo.py --data-dir /path/to/AAD               # -> results/demo_video.mp4
```

Live sound needs `sounddevice`; live EEG needs `mne-lsl` (both optional, in
`requirements.txt`). Add `--no-audio` to run the visual without playing sound.

##### Two ways to run it live (choose per demo)

The decoder must be tuned to a brain. You have both options ready — pick with
`live_demo.py --decoder <file>`:

```bash
### 1) INSTANT, zero calibration — a generic decoder built from several people ahead of time.
python src/pretrain_generic.py --data-dir /path/to/AAD --subjects P1 P2 P3   # once, on your rig
python src/live_demo.py --data-dir /path/to/AAD --decoder results/generic_decoder.npy

### 2) STRONGER, ~3 min personalize — calibrate on the specific listener, then run.
python src/calibrate.py  --data-dir /path/to/AAD --eeg lsl --minutes 3 --files A.wav B.wav
python src/live_demo.py  --data-dir /path/to/AAD --decoder results/personal_decoder.npy
```

Measured trade-off (`results/calibration_analysis.png`): generic ≈ 72% at a 60 s
window with **no** wait; personalized reaches ~82%+ but needs a few minutes. **1 minute
of calibration is worse than the generic decoder — don't do it.** Use generic for
walk-up judges, personalize for a hero demo.

#### Get the data (not committed — too large)

Download the subject files and `stimuli.zip` from
<https://zenodo.org/records/4004271> and arrange:

```
AAD/
├── S1.mat  S2.mat  S3.mat      # subject EEG
└── stimuli/ … *.wav            # unzip stimuli.zip here
```

#### Run

```bash
pip install -r requirements.txt

### 1) reproduce the viability result (writes results/)
python src/run_viability.py --data-dir /path/to/AAD

### 2) sanity-check controls
python src/verify.py --data-dir /path/to/AAD

### 3) the real-time demo — today, no hardware (renders demo_output.wav):
python src/demo_realtime.py --data-dir /path/to/AAD --subject S3 --trial 4 --output wav

### 3b) build day — live headset + live mics + live playback:
python src/demo_realtime.py --data-dir /path/to/AAD --eeg lsl --audio mic --output play
```

All tunables (decision window, ducking dB, gain ramp, hysteresis) live in
`src/config.py`. See `docs/PROJECT.md` for the day-of setup and the honest scope on the
audio front-end, and **[`docs/BUILD_DAY.md`](neuro-attention/docs/BUILD_DAY.md)** for exactly what's tested vs.
what to integrate with the ANT Neuro headset on the day.

> **Tested:** the analysis and the replay demo (no hardware). **Needs on-rig
> integration:** live audio out, live mics, and live EEG over LSL — including a short
> decoder **calibration on the ANT Neuro cap** (KU-Leuven-trained weights don't
> transfer channel-for-channel to a different amplifier). See `docs/BUILD_DAY.md`.
