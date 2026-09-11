# NOVA — combined development folder

**Start here: [combined project guide](PROJECT_GUIDE.md)** — both project READMEs and current workspace notes, updated September 9, 2026.

Open `NOVA.code-workspace` in VS Code, or open this NOVA folder.

## Where things live

| Folder | What to work on |
| --- | --- |
| `base/` | Original NOVA2026 project: attention-lapse detection, EEG data processing, and neural-network training. |
| `neuro-attention/` | Recent add-on: auditory attention decoding, two-talker audio mixing, and live/replay demos. |

Start with [the base README](base/README.md) and [the add-on project guide](neuro-attention/docs/PROJECT.md). See [hardware integration notes](neuro-attention/docs/BUILD_DAY.md) before attempting live EEG.

## Common edit locations

- Base reusable code: `base/src/nova2026/`
- Base experiments: `base/scripts/`
- Add-on decoder and demo: `neuro-attention/src/`
- Add-on demo UI: `neuro-attention/src/ui.html`
- Add-on settings: `neuro-attention/src/config.py`
- Existing add-on demo outputs: `neuro-attention/results/`

## Environments and running

Use a VS Code terminal starting in this NOVA folder. Each component keeps its own environment and working directory because its dependency specifications and entry points differ.

### Base

```sh
cd base
uv sync
```

The base requires Python 3.12 or newer. See its README for training and dataset conventions. Its original dependency specification and lockfile are preserved; installation has not been validated here.

### Add-on

In a fresh terminal from the NOVA folder:

```sh
cd neuro-attention
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/live_demo.py --data-dir /absolute/path/to/AAD --no-audio
```

Supply the actual KU Leuven AAD dataset location. The EEG/audio dataset is not included in the add-on. For audio playback, install `sounddevice` in this environment and omit `--no-audio`. Live EEG additionally needs `mne-lsl` and hardware setup; consult the add-on documentation.

Run the add-on scripts from `neuro-attention/`, and base scripts from `base/`, to retain their original relative-path behavior.

## What was combined

Both codebases are collected here. After the initial unchanged copy, the review fixed base path resolution, labeling edge cases, held-out evaluation, and checkpoint export. A first Python bridge now runs both models on separately prepared, aligned windows; live capture and browser integration remain pending. See [the review](REVIEW.md) and [integration guide](INTEGRATION.md). No virtual environments or nested Git repositories were copied. Your original base checkout remains at `/Users/yutong/Documents/git/NOVA2026`.

This folder sits inside the current Codex project repository. Nothing has been committed or pushed. Edit these copies going forward when working in this combined workspace; edits do not sync back to the original checkout automatically.

See `SOURCES.json` for source locations and revisions.
