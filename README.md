# ATTUNE — Neuro-Adaptive Hearing

ATTUNE is a research prototype for showing which of two candidate audio sources a
listener is attending to. Its application layer is testable now using clearly
marked artificial data sent through the same backend transport as future research
results. It is not a medical device.

```text
Audio Source A + Audio Source B + listener EEG
                       |
              auditory attention decoder
                       |
                 focused source
                       |
           thin adapter → publish callback
                       |
        Python session worker / publisher
                       |
                REST / WebSocket
                       |
                   ATTUNE UI
                       |
           future adaptive audio gain
```

The two inputs can represent recordings, stream/YouTube references, microphones,
headset channels, or future adapters. The backend owns acquisition and decoding.
React displays Source A / Source B and explicit A/B/uncertain/unavailable results;
correlations remain correlations. No audio processing runs in React.

## Implemented

- Python backend with REST/WebSocket transport and start/stop session lifecycle.
- Deterministic artificial producer through the existing publisher.
- React dashboard with A/B focus visualization and two source cards.
- Shared stereo audio/video playback, observed media timeline, independent smooth
  Web Audio gains, Original Mix / ATTUNE modes and neutral failure behavior.
- Optional vigilance, synchronization, display EEG, signal quality and gain fields;
  missing measurements remain unavailable.
- Existing generic prediction/provider and development feedback infrastructure.
- [Backend handoff and publish contract](docs/BACKEND_HANDOFF.md).

## Artificial / development

Mock A/B focus alternates every four media seconds when shared media is configured
(or session seconds in the original transport-only demo). Mock predictions, synthetic
32-sample display EEG, demo vigilance and simulated gain are illustrations, not
participant measurements. Every artificial result declares `simulated: true` and
the dashboard displays an artificial-data banner. Signal quality and physical
synchronization offset remain unavailable. In ATTUNE playback mode the supplied demo gains attenuate the browser audio.
Original Mix applies neutral gains to both sources.

The existing generic development provider output remains independent of the A/B
illustration. Its default constant output produces no active development feedback.

## Future / not claimed

Arbitrary single-microphone speaker separation, solved hardware synchronization,
production hearing-device integration and a real signal-quality metric are not
provided by this demo. Correlation is not probability/confidence. Artificial data
is not evidence of real EEG accuracy. Real EEG/audio research integration requires
reviewed input, clock, model and failure contracts.

## Run locally

From the repository root, use Python 3.9+ for the isolated transport application
and Node 22.12+. The scientific projects have separate environment requirements.

```sh
python3 -m venv /tmp/attune-transport-env
/tmp/attune-transport-env/bin/python -m pip install -r backend/requirements-test.txt
npm ci --prefix frontend
/tmp/attune-transport-env/bin/python -m uvicorn backend.app.server:app --host 127.0.0.1 --port 8001
```

In a second terminal from the repository root:

```sh
npm run dev --prefix frontend
```

Open http://127.0.0.1:5173 and select **Start mock session**. Observe Source A then
Source B, correlations/gains, the artificial-data banner and unavailable physical
metrics. **Stop session** clears active focus. A known disconnect also clears focus;
reconnection uses the existing transport snapshot flow. Restart a running backend
after source changes so it loads the updated producer.

Use one backend worker: sessions and latest state are process-local. Vite's existing
proxy routes `/api` and `/ws` to port 8001. A production reverse proxy/deployment is
not included. No EEG hardware or datasets are needed for the artificial demo.
For audible playback, configure a stereo recording as below.

## Verify

```sh
PYTHONDONTWRITEBYTECODE=1 /tmp/attune-transport-env/bin/python -m unittest discover -s backend/tests -v
npm test --prefix frontend
npm run build --prefix frontend
ATTUNE_PYTHON=/tmp/attune-transport-env/bin/python npm run test:live --prefix frontend
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -q
```

The live suite starts temporary local services; its Vite setup may conflict with
an already running development server on 5173. Unit suites cover transport,
session lifecycle, provider/feedback preservation, deterministic packets, metadata,
malformed fields and focus gating. The legacy HTML regression suite is separate.

## Repository components

| Path | Purpose |
| --- | --- |
| `backend/` | Application transport, sessions, providers and result adapters |
| `frontend/` | React dashboard, decoder registry and transport client |
| `docs/BACKEND_HANDOFF.md` | Real EEG/two-audio integration boundary and checklist |
| `base/` | Existing NOVA research code; [research README](base/README.md) |
| `neuro-attention/` | Existing auditory attention research and legacy demo; [guide](neuro-attention/docs/PROJECT.md) |
| `ATTUNE_UI/` | Earlier standalone HTML UI handoff |

Scientific models and acquisition code are separate from the application demo.
Connect reviewed research results by injecting a producer through the existing
[adapter boundary](backend/adapters/README.md), preserving publisher-owned sequence
and session IDs.

## Shared stereo media demo

Place your own two-source stereo file in `demo-media/` (ignored by Git). The two
recorded signals map internally to Source A and Source B; these names imply no
identity, gender or location. Python and the browser use the **same file**, served
by the backend. No upload, file picker with a separate browser-only copy, external
URL, YouTube extraction or scientific audio processing is involved.

After the environment setup above, start the backend from the repository root:

```sh
mkdir -p demo-media
# Place your recording at demo-media/demo.wav before starting.
ATTUNE_MEDIA_FILE=demo-media/demo.wav ATTUNE_MEDIA_TITLE="Shared Conversation" \
  /tmp/attune-transport-env/bin/python -m uvicorn backend.app.server:app --host 127.0.0.1 --port 8001
```

In a second terminal run `npm run dev --prefix frontend` and open
http://127.0.0.1:5173. Stop your previous backend process before launching this one
on the same port. The file setting is runtime-only; its filesystem path is not
sent to the browser. Title defaults to **Demo Audio**. Supported extensions are
`.wav`, `.mp3`, `.m4a`, `.mp4`, `.webm`; actual codec support depends on the browser.
Use a known two-channel stereo file; channel-count validation for compressed media
is not implemented. WAV is a straightforward choice for a repeatable local demo.
Video shares the same audio graph and appears as a compact preview.

1. Click **Start mock session**, then **Play**. Grant playback by clicking again
   if your browser blocks the initial asynchronous play request.
2. Confirm **Media Time** advances, A is focused in 0–4 seconds, then B in 4–8.
3. Select **ATTUNE** and listen for the backend-supplied attenuation (currently
   0 / −6 dB). Select **Original Mix** to hear both sources at neutral gain.
4. Pause around 6.2 seconds. Wait, confirm the timer remains fixed and B stays
   focused, then resume from that position.
5. Press **Stop**: position resets, gains return to neutral, focus clears. **Stop
   session** also stops browser playback and the existing producer.
6. Disconnect the backend: playback pauses, focus clears, and gains neutralize.
   Restart the session and prepare playback again to recover.

The display-only progress bar cannot seek. Unexpected seeking/rate changes or
playback/report errors fail neutral. Gains use `10 ** (db / 20)` and smooth target
transitions (~400 ms); the player accepts attenuation from −80 to 0 dB only.
It never derives gain from correlations or implements a prediction policy.

### Timeline and limitations

Play first prepares position zero with Python using the existing session ID.
Python returns the media ID/revision and its monotonic reference timestamp. Browser
playback then reports its actual position every 250 ms and on play/pause/stop.
Python holds the last observed position; paused time never advances with wall time.
Reports expire after 1.5 seconds. Attention/gain include media identity, revision
and media position; the player checks these against its own position (within 0.75 s)
and fails neutral when stale, disconnected, uncertain, invalid or desynchronized.
These tolerances are conservative demo transport rules, not scientific thresholds.

This is **observed application timeline synchronization**, not sample-accurate
scheduling, acoustic latency calibration, EEG alignment or a measured sync-quality
metric. Network delay and the 250 ms producer/report cadence can delay focus changes
near four-second boundaries. Physical synchronization fields remain unknown.
One browser controls a prepared session; use Stop session to release an abandoned
controller. No unsynchronized seeking, background-playback guarantee, mobile codec
guarantee or compressed-file stereo validation is claimed. Keep the demo tab active.

The real backend will replace artificial attention/gain production and align EEG
windows to the shared recording timeline. It retains the existing publisher and
React audio layer; see [the practical handoff](docs/BACKEND_HANDOFF.md).
Browser listening/manual validation with your actual recording is still required.
