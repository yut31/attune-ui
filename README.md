# ATTUNE

## Neuro-Adaptive Hearing

ATTUNE is a neuro-adaptive hearing prototype that explores a simple question:

> **Can a hearing system understand which voice a listener is trying to hear?**

ATTUNE combines EEG-based auditory attention decoding with adaptive audio control. The goal is to estimate which audio source a listener is attending to and use that result to adjust the listening experience.

---

## The Problem

In environments with multiple people speaking at once, hearing devices can amplify sound without necessarily knowing **which person the listener actually wants to hear**.

ATTUNE explores whether neural signals can provide that missing information.

---

## How ATTUNE Works

```text
Audio Source A ──────┐
                     │
Audio Source B ──────┼──→ Auditory Attention Decoder
                     │              ↑
EEG ─────────────────┘              │
                                    ↓
                         Attended Source Prediction
                                    ↓
                         Adaptive Audio Control
                                    ↓
                              ATTUNE Interface
```

The Python backend handles EEG/audio processing, predictions, synchronization, session state, and gain decisions.

The React frontend displays those results and controls playback. Scientific inference is intentionally kept out of the browser.

---

## Current Demo

The current ATTUNE application includes:

- React + Vite frontend
- FastAPI Python backend
- REST + WebSocket communication
- Source A / Source B visualization
- Correlation values
- Backend-controlled gain values
- Current-focus visualization
- Shared stereo media playback
- Original vs. ATTUNE listening comparison
- Vigilance display
- Synchronization status
- Signal-quality state
- EEG visualization
- Deterministic simulated-data mode

The simulated mode allows the interface and communication pipeline to be demonstrated before live EEG hardware is connected.

**Simulated results are not real EEG predictions.**

---

## Source A vs. Source B

ATTUNE represents the two candidate speech streams simply as:

- **Source A**
- **Source B**

These labels intentionally do not assume left/right position, gender, microphone, or speaker identity.

For the current demo, a stereo recording can be used:

```text
Stereo Recording
       │
       ├── Channel 1 ──→ Source A
       │
       └── Channel 2 ──→ Source B
```

A future backend can instead provide two separate microphones, prerecorded streams, separated speakers, or another synchronized source without redesigning the frontend.

---

## Original vs. ATTUNE

The interface provides two listening modes.

### Original

Original plays both sources without ATTUNE's adaptive gain changes.

```text
Source A ── 0 dB ──┐
                    ├──→ Output
Source B ── 0 dB ──┘
```

### ATTUNE

ATTUNE applies gain decisions supplied by the backend.

For example, if Source A is the attended source:

```text
Source A ──  0 dB ──┐
                     ├──→ Output
Source B ── -6 dB ──┘
```

This allows a direct comparison between the unmodified audio and the ATTUNE adaptive listening mode.

---

## Architecture

```text
EEG / Audio Inputs
        ↓
Scientific Processing
        ↓
Attention / Vigilance Results
        ↓
Prediction + Gain Decisions
        ↓
Python Publisher
        ↓
FastAPI Backend
   ├── REST
   └── WebSocket
        ↓
React Frontend
        ↓
Adaptive Audio + Visualization
```

Heavy EEG and machine-learning processing is separated from HTTP request handling.

The frontend does not generate scientific predictions. It displays decisions supplied by the backend.

---

## Running ATTUNE

### Backend

Create and activate a Python virtual environment and install the backend requirements.

Configure a local stereo demo file:

```bash
export ATTUNE_MEDIA_FILE="demo-media/demo.wav"
export ATTUNE_MEDIA_TITLE="Shared Conversation"
```

Start the backend:

```bash
python -m backend.app.server
```

The backend runs at:

```text
http://127.0.0.1:8001
```

### Frontend

In another terminal:

```bash
npm run dev --prefix frontend
```

Then open:

```text
http://127.0.0.1:5173
```

For the artificial demo:

1. Start a mock session.
2. Press Play.
3. Select **ATTUNE** to hear the adaptive effect.
4. Select **Original** to hear the unmodified mix.
5. Watch Source A / Source B focus and monitoring information update.

Local recordings in `demo-media/` are excluded from Git.

---

## Backend Interface

The application exposes REST endpoints and a live WebSocket connection:

```text
GET  /api/health
GET  /api/state

POST /api/session/start
POST /api/session/stop

GET  /api/sessions
GET  /api/sessions/{id}

WS   /ws/live
```

REST is used for commands and state snapshots.

WebSocket communication is used for live application updates.

---

## Real EEG Integration

The current artificial-data producer is a development and presentation tool.

For real operation, it can be replaced by a producer connected to live EEG and audio sources:

```text
Live EEG ────────────┐
                     │
Audio Source A ──────┼──→ Research Pipeline
                     │
Audio Source B ──────┘
                              ↓
                         Prediction
                              ↓
                       Existing Publisher
                              ↓
                      REST / WebSocket
                              ↓
                       ATTUNE Frontend
```

The frontend does not need to know whether a result came from simulated data, prerecorded research data, or a live EEG system.

Real integrations should report uncertain or unavailable states instead of fabricating predictions.

More detailed integration information is available in `docs/BACKEND_HANDOFF.md`.

---

## Synchronization

Auditory attention decoding requires EEG and audio to be aligned in time.

The current demo tracks the shared media timeline so backend results can be associated with the corresponding audio position.

Real hardware introduces additional timing concerns such as device clocks, acquisition latency, and physical audio delay. These must be measured and calibrated rather than assumed.

If a result is unavailable, uncertain, stale, or unsafe to apply, ATTUNE can return the audio to a neutral state instead of forcing a Source A or Source B decision.

---

## Research Components

### Auditory Attention Decoding

Estimates which candidate speech stream is more consistent with the listener's EEG response.

### Vigilance / Attention State

Provides additional information about the listener's attentional state.

These signals may eventually complement each other when making adaptive audio decisions.

---

## Project Status

ATTUNE is currently a research and hackathon prototype.

### Implemented

- React interface
- FastAPI backend
- REST + WebSocket communication
- Session lifecycle
- Simulated prediction pipeline
- Source A / Source B comparison
- Shared stereo playback
- Backend-controlled adaptive gain
- Original / ATTUNE comparison
- Media timeline reporting
- Vigilance, synchronization, signal-quality, and EEG interface components

### Integration in Progress

- Live EEG acquisition
- Real auditory-attention predictions
- Real audio-source integration
- Hardware timing calibration
- Physical EEG/audio synchronization

### Future Work

- EEG artifact handling
- Stronger uncertainty guardrails
- Improved signal-quality estimation
- Additional audio sources
- Speaker separation or microphone-array integration
- Personalized decoding
- Hearing-device hardware integration

---

## Research Limitation

ATTUNE does **not** currently claim to isolate arbitrary speakers from a single noisy-room microphone.

Auditory attention decoding requires candidate audio streams that can be compared with the EEG signal.

In a real environment, obtaining those streams may require multiple microphones, beamforming, speaker separation, or other audio-processing techniques.

The current stereo demo provides known Source A and Source B streams so the attention and adaptive-audio pipeline can be demonstrated reliably.

---

## ATTUNE

**Neuro-Adaptive Hearing**

**ATTUNE explores how a hearing system could understand what the listener is trying to hear.**
