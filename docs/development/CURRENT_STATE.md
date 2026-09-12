# NOVA Application — Current Development State

## Last Updated
2026-09-12. Audited HEAD: `a3ee2ba21115cda4eb3d1cac469c2239892e03c4`
(`a3ee2ba`, 2026-09-11, Finalize ATTUNE UI handoff).

This is a working-tree handoff, not a description of HEAD alone. The entire new
`backend/` and `frontend/` are untracked. No commit/tag proves their exact phase
boundaries; PHASE_1.md through PHASE_3.md explicitly distinguish current code,
ledger evidence and historical uncertainty. No commit or push was performed.

## Current Phase

NOVA is the integration/application workspace. NOVA2026 and novaAAD remain
independently developed external research repositories; neither is copied into
or modified by this workspace.

Application Phase 4 adds a common `PredictionProvider` boundary and multi-output
`PredictionResult` schema. The only active end-to-end provider is the explicit
deterministic mock provider. NOVA2026 and novaAAD adapters are unavailable
placeholders until reviewed native callable boundaries are supplied.

The application does not modify either external repository. Candidate portable
files are the generic contract/provider/transport/frontend files; the two
research adapter placeholders are NOVA-local until their native boundaries are
reviewed. See `INTEGRATION_MATRIX.md` for transfer classifications.
Phase 3 completed; Phase 4 not yet started.

“Completed” means the mock transport, minimal client and result-adapter boundary
exist and pass their focused tests. It does not mean real EEG/model integration
or a scientifically validated product is complete. The current live smoke suite
has a port-isolation failure documented below.

## What Works
- FastAPI `create_app()` and deterministic mock worker; health/state/start/stop,
  session summaries and live result delivery. Backend unit/ASGI tests pass.
- Thread-safe bounded publisher; server-assigned sequence numbers, session UUIDs,
  per-stream timestamp checks and cooperative worker shutdown/error reporting.
- Minimal ATTUNE React debug client with REST bootstrap, WebSocket reconnect,
  validation, normalized latest state, known decoders and opaque unknown fallback.
- ResultAdapter and ResultProducer interfaces, plus conversions from existing
  AAD/PVT/CombinedDecision output shapes; fixture integration verified.
- Existing legacy ATTUNE HTML regression suite passes. It is a separate UI using
  legacy `/state`, not a graphical skin attached to the React transport.
- Already-running frontend responds HTTP 200; its `/api/health` proxy reaches
  the backend and reports protocol version 1. This is not model-readiness proof.

## What Is Mocked
- Default `backend/app/server.py` app uses `backend/adapters/mock.py:MockProducer`.
  Six result types: attention, vigilance, sync, eeg_display, gain, signal_quality.
- Deterministic A/B switch, cosine vigilance illustration and sinusoidal display
  traces. No acquired EEG, physical audio playback or model inference in that path.
- Sync is unknown with null offsets. Mock drift_warning=false is a simulated flag,
  not a measurement. The separate real-result adapter defaults that flag to null.
- Adapter tests use result-shaped fixtures, not a deployed checkpoint.
- Legacy HTML has its own deterministic demo mode, independent of Python mocks.

## What Is Missing
- A coordinator connecting sources → separately prepared/aligned windows → real
  algorithms → ResultAdapter → the new backend. Source protocols alone do not do this.
- A final acquisition format, timestamp-domain mapping, EEG/audio alignment,
  source-specific lifecycle wrappers and cancellation-aware reads.
- Validated task-specific model/checkpoint selection and performance evidence for
  assistive hearing. No `.pt`, `.pth` or `.ckpt` was found in `base/models/` or
  `base/datasets/`; `training-runs/` is absent. No checkpoint was loaded in this audit.
- `scripts/dataproc/streaming` and `scripts/dataproc/riemann`, including variants
  under `base/`, are absent from this checkout. No matching path history was found
  across inspected Git refs. No Riemann implementation/integration can be claimed.
- Production hosting/reverse proxy, persistent replay/storage, auth, hardware
  setup, physical synchronization and a designed React visual dashboard.
- Reliable live-test port isolation, and a scientific test environment with the
  required dependencies. No dependencies were installed during this audit.

## How To Run
Run from repository root. Use the existing transport environment if still present:

```bash
/private/tmp/attune-backbone-venv/bin/python -m uvicorn backend.app.server:app --host 127.0.0.1 --port 8001
```

In another terminal:

```bash
npm run dev --prefix frontend
```

Open http://127.0.0.1:5173 and select **Start mock session**. The development proxy
sends `/api` and `/ws` to loopback 8001. Do not start duplicate servers on occupied
ports. Stop mock sessions with the UI button; stop server processes in their own
terminals when finished. The user's already-running servers were left running.

If the temporary Python environment/dependencies are missing, these are setup
commands (documented here, not executed during this audit):

```bash
python3 -m venv /tmp/attune-transport-env
/tmp/attune-transport-env/bin/python -m pip install -r backend/requirements-test.txt
npm ci --prefix frontend --registry=https://registry.npmjs.org
/tmp/attune-transport-env/bin/python -m uvicorn backend.app.server:app --host 127.0.0.1 --port 8001
```

Use that interpreter instead of the earlier temporary path in tests. The client
README recommends Node 22.12+; this audit used Node 24.18.0. The backend transport
is tested on Python 3.9; `base/pyproject.toml` separately declares Python >=3.12
and scientific packages. Installing the transport does not install the models.

Legacy UI/source run instructions remain in `neuro-attention/README.md` and
`INTEGRATION.md`. `live_demo.py` requires a dataset even with `--no-audio`; it is
not the hardware-free mock server. Its default port is 8000. Do not substitute
its flat `/state` response for the new `/api/state` snapshot.

## How To Test
Exact commands run in this audit:

```bash
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
npm test --prefix frontend
npm run build --prefix frontend
ATTUNE_PYTHON=/private/tmp/attune-backbone-venv/bin/python npm run test:live --prefix frontend
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
curl --max-time 5 -fsS http://127.0.0.1:5173/api/health
curl --max-time 5 -fsS -o /dev/null -w 'frontend HTTP %{http_code}\n' http://127.0.0.1:5173/
```

| Check | Audit result | What it establishes |
|---|---|---|
| Backend discovery | PASS: 29 tests | 19 transport + 10 adapter tests, including real ASGI REST/WS handlers |
| Frontend unit/contract | PASS: 25 tests | 22 client + 3 adapter tests; deterministic Python fixtures and React static markup |
| Vite production build | PASS: 29 modules | Client bundles successfully |
| Live Python/Vite test | FAIL: 1 test, port 5173 already in use | Current harness cannot coexist with the running frontend; not a fresh end-to-end pass |
| Root unittest discovery | FAIL: 149 reported, 147 UI pass + 2 loader errors | `test_combined` and `test_driving_pilot` cannot import numpy; their scientific test bodies did not run |
| Existing server smoke | PASS: health ok/version 1; frontend HTTP 200 | Current page/HTTP proxy are available |

The live test requests Vite `port: 0`, but the observed effective port was 5173.
Do not rely on its “ephemeral” description when another UI is running. Its
previous ledger pass is historical evidence only. No tests were weakened, no
model training/data download or physical EEG/audio smoke was attempted. Existing
scientific tests use synthetic fixtures/checkpoints when their dependencies are
available; passing them would establish wiring, not physiological performance.

## Architecture
```text
IMPLEMENTED DEFAULT APPLICATION
REST start -> Sessions worker -> deterministic MockProducer
                                  |
                                  v
                              Publisher
                    (sequence, latest state, event ring)
                         |                     |
                    /api/state              /ws/live
                         +----------+----------+
                                    v
                           React transport client
                           validation -> decoders
                           -> normalized state -> debug UI

PREPARED, NOT CONNECTED TO DEFAULT APPLICATION
future source/model coordinator -> result records / legacy converters
                                 -> ResultAdapter.publish
                                 -> same Sessions publish callback / Publisher

EXISTING SCIENTIFIC/LEGACY PATHS (SEPARATE)
prepared broadband recording -> PVT-specific preprocessing -> LapsePredictor
                            -> AAD-specific preprocessing + audio envelopes
                               -> RealtimeDecoder -> correlations -> AttentionMixer
                            -> CombinedPipeline.decide -> CombinedDecision

legacy ReplayEEG or LSLEEG + FileSource or MicSource
 -> live_demo.engine (AAD reconstruction / mixer / optional playback)
 -> global STATE + lock -> legacy HTTP /state -> neuro-attention/src/ui.html

base offline builders -> preprocessing / labels / spectral features / training
                      -> model/checkpoint artifacts, not the new web transport
```

Tree landmarks: `base/src/nova2026/` (scientific library), `base/scripts/dataproc/`
and `base/scripts/training/` (offline preparation/training), `neuro-attention/src/`
(AAD, combined bridge and legacy server/UI), `backend/` (transport/adapters),
`frontend/` (React), `tests/` (legacy/scientific and central registry),
`ATTUNE_UI/` (legacy handoff), and `docs/development/` (this handoff).

## Prediction Status
There ARE real prediction functions for prepared windows. There is NOT a verified
incoming-EEG-to-application predictor or a validated generic “feed/lapse” product
model in this checkout. Specifically:

| Layer | Existing code | Meaning / boundary |
|---|---|---|
| Preprocessing | `base/src/nova2026/data/pipeline.py:Pipeline`, `DefaultPipe`; `base/scripts/dataproc/pipelines.py:AttUPipeline` | Transform EEG; `Pipeline.feed()` loads data into a stepwise processing chain, not a prediction function |
| Feature extraction | `base/scripts/dataproc/engagement.py:welch`, `band_power`, `engagement_index`; `spectual.py` | PSD/band-power and engagement features; not a validated lapse classifier or Riemann inference |
| Generic architecture | `base/src/nova2026/architecture/cnn.py:EEGNet`, `EEGWaveNet` | Neural-network architecture alone does not establish target labels or model performance |
| PVT-specific inference | `base/src/nova2026/inference.py:LapsePredictor.predict` | Loaded checkpoint, prepared EEG window → class-1 softmax score for `slowest_session_decile`; not demonstrated conversation-lapse calibration |
| Driving pilot inference | `base/src/nova2026/driving_inference.py:DrivingResponsePredictor.predict` | Separately labeled driving slow-response score; code explicitly says not calibrated as general lapse probability |
| Auditory attention | `neuro-attention/src/decoder.py:RealtimeDecoder.reconstruct`, `attention_mixer.py:AttentionMixer.set_decision` | EEG reconstruction is correlated with two speech envelopes; mixer chooses/holds talker using existing hysteresis |
| Combined task output | `neuro-attention/src/combined_pipeline.py:CombinedPipeline.decide` | Prepared aligned PVT/AAD windows → lapse score, attended talker and correlations; real function exists but is not called by default backend |
| Riemann inference | No matching implementation located | Cannot assert a generic Riemann classifier, feed method or its scientific meaning exists here |
| Mock output | `backend/adapters/mock.py:results` | Deterministic illustration; no participant measurements |
| UI visualization | React decoders/debug page; legacy HTML | Display and normalize provided values; do not predict physiological state |

`INTEGRATION.md` already calls for a timestamp-aware input adapter and listening-task
evaluation before lapse-driven gain changes. `DRIVING_PILOT.md` explicitly limits
the driving target. These cautions remain valid. An older sentence in
`neuro-attention/docs/PROJECT.md` mentions a team `mne-lsl` streaming scaffold;
that external claim is not corroborated by the current tree/history. Request the
actual teammate source/branch if it is intended for Phase 4; do not fabricate it.

## Important Contracts

**EEG windows / scientific behavior.** `CombinedPipeline.decide()` requires
separately preprocessed windows ending at the same instant as each other and the
two audio envelopes (tolerance 1e-6), and increasing decision end times. PVT input
is `(training_channels, 256)`, 128 Hz, microvolts, exact checkpoint channel order,
`pvt_0.5_45Hz`; checkpoint metadata is validated. AAD is `(960, aad_channels)` at
64 Hz, `aad_1_9Hz_zscore`, two envelopes `(2, 960)`, verified montage order and
matching weights. Do not upsample the AAD branch and label it valid broadband PVT
input. Positive AAD lag edges are excluded before correlation in the combined
bridge. Metadata equality does not prove physical filtering/alignment happened.

**Result boundary.** Call `ResultAdapter.publish(result)` from a worker supplied
by `ResultProducer` or existing `Producer.run(publish, stop)`. `combined_results`
requires an explicit session-relative timestamp instead of silently copying a
recording time. Legacy indices 0/1 map to A/B; uncertain/unavailable remain explicit.
Lapse score is not inverted into vigilance. Unknown sync offset/warning remain
null. `EEGDisplayResult` is caller-prepared channel-major display data, not raw
acquisition. Separate publications are not an atomic multi-result transaction.

**WebSocket / snapshot.** Version-1 envelope keys: `version`, `type`, `timestamp`,
`sequence`, `source`, `session_id`, `payload`. JSON payload object; finite numbers,
max 256 KiB packet, depth <=32; identifiers max 128 characters. Sequence is a
nonnegative safe integer assigned process-wide; timestamp is session-relative
seconds, ordered per retained source/type. `/api/state` is
`{sequence, session_id, packets}`. WS first sends individual latest packets, then
bounded new events; slow-client close 1013 requires resnapshot. There is no
durable history guarantee. Frontend rejects duplicate/older sequences and
regressing per-stream timestamps; reconnect uses a new REST snapshot.

**Run/replay.** New source protocols expose `start()`, `read(timeout)`, `stop()`
with EEG and audio separate. No concrete new source wrapper implements them yet.
Legacy `ReplayEEG.read(n)` consumes supplied samples at its configured rate;
`LSLEEG.read(n)` resamples chunks, discards returned LSL timestamps and can pad
warm-up with zeros. Legacy `FileSource.read()` returns two audio blocks and
`MicSource.read()` uses two input channels. These are incompatible with a
claimed timestamp-aware generic replay protocol without wrappers. Headset audio
is not independently implemented. Lifecycle ownership and clock mapping belong
to the integrating coordinator, never HTTP handlers. Stop is cooperative.

**Configuration.** Keep `base/pyproject.toml` scientific dependencies separate
from backend transport and frontend package files. `base/src/nova2026/config.py`
finds its own package root for datasets. Preserve `neuro-attention/src/config.py`
AAD rate/filter/lag/mixer settings. Run one backend process/worker with in-memory
state. Default dev ports are 8001 and 5173; legacy server uses 8000. Production
assets require an eventual API/WS reverse proxy; Vite dev proxy is not deployment.

## Open Work
Before Phase 4 implementation: review this handoff, identify the intended prediction
target and obtain the actual streaming/Riemann source if it exists elsewhere.
Then scope Phase 4 around a deterministic replay coordinator with verified inputs:

1. Resolve replay data/checkpoint availability and electrode, unit, preprocessing,
   sample-count, clock-domain and session-origin contracts without choosing hardware.
2. Wrap sources with bounded reads and cleanup; build separate valid PVT/AAD
   windows and aligned audio envelopes using existing scientific implementations.
3. Invoke the selected existing predictor(s), preserving task labels, and publish
   through ResultAdapter. Keep unavailable and uncertain semantics explicit.
4. Verify replay → windows → result → WS → UI with reproducible fixtures, then
   evaluate real-task performance separately from software integration.
5. Fix the live harness's port isolation in a separate authorized implementation
   task, and run scientific regressions in a suitable environment.

No Phase 4 coordinator, model change, hardware integration or graphics work was
started by this audit.

## Do Not Break
- Preserve existing NOVA2026 package-root discovery, data/training scripts and
  research outputs; do not overwrite datasets or model artifacts.
- Preserve model-specific montage, unit, sampling/preprocessing and checkpoint
  checks; PVT, driving and AAD are different tasks/contracts.
- Preserve aligned-window and increasing-time checks, AAD lag handling and mixer
  hysteresis/ramping. Do not label physical synchronization from metadata alone.
- Preserve subject-separated training/evaluation and task-specific label meaning;
  `Pipeline.feed()` and engagement features are not validated lapse predictions.
- Keep acquisition, algorithms, sync and web transport independent; no scientific
  work in React or request handlers. Keep source shutdown bounded and explicit.
- Preserve legacy `/state` and new packet/snapshot contracts as distinct APIs;
  unknown/unavailable data must not become fabricated measurements.
- Preserve current tests and teammate files. Retain the mock path as an independent
  hardware-free integration check.

## Security and Git Handoff
A filename/content-pattern check ran before Git status/diff/history inspection.
No confirmed project secret was detected in the examined text files. This is not
an exhaustive certification of binary data, archives, dependency trees or history.
No `.env` contents or credential values were printed. No matching sensitive
filenames were found in the tracked-name check or `ATTUNE_UI.zip` member names.

The untracked `.venv-backend/` is NOT covered by current ignore rules. The scan
flagged `.venv-backend/lib/python3.9/site-packages/pip/_vendor/certifi/cacert.pem`
(certificate filename; contents not read) and
`.venv-backend/lib/python3.9/site-packages/pydantic/types.py` (credential-like
assignment candidate; value suppressed). Neither is a confirmed application secret.
Keep this entire local environment out of Git; add an appropriate ignore rule in
a separately scoped cleanup or use an external environment. No ignore file was
changed here. Avoid broad staging; review `ATTUNE_UI.zip` separately as an artifact.

At audit start: modified `AI_LEDGER.md`, `TESTING.md`, `tests/TEST_REGISTRY.md`;
untracked `.venv-backend/`, `ATTUNE_UI.zip`, `backend/`, `frontend/`. This task adds
`docs/` and updates only ledger/registry beyond its four documents. Current HEAD
predates all untracked application code. Suggested documentation commit message:
`docs: reconstruct application phases 1–3 and current-state audit`.
