# Phase 1 — Backend Transport Foundation

## Status
Completed within the mock transport scope, as implemented in the current working
tree. This is a retrospective audit dated 2026-09-12, not a recovered release tag.

## Goal
The `BACKEND-001` ledger entry and `backend/README.md` identify the goal as a
hardware-independent result transport, with deterministic Python results and
clean session/background-worker lifecycle. Real scientific integration was deferred.

## Implemented
- `backend/app/protocol.py`: `make_packet()` / `validate_packet()` construct and
  validate version-1 envelopes without interpreting result payloads.
- `backend/app/publisher.py`: `Publisher` owns process-wide sequences, defensive
  copies, a 256-event ring and up to 128 latest source/type streams.
- `backend/app/sessions.py`: `Sessions` serializes start/stop, runs one producer
  thread, records up to 32 sessions and publishes lifecycle/error packets.
- `backend/app/server.py`: `create_app()` provides health/state, session start/stop,
  session list/detail and `/ws/live`. The module-level app uses `MockProducer`.
- `backend/adapters/mock.py`: deterministic attention, vigilance, sync,
  eeg_display, gain and unavailable signal_quality payloads; simulated labels.
- EEG/audio source protocols exist in `backend/sources/base.py`; they have no
  acquisition implementations in the new backend.

## Architecture Changes
The new backend is separate from the pre-existing HTTP server in
`neuro-attention/src/live_demo.py`. It does not replace that module's global
`STATE`, `/state`, or scientific engine. Dependencies are scoped to
`backend/requirements.txt` and `backend/requirements-test.txt`.
Computation belongs to a producer worker; HTTP/WS handlers serve published data.

## Data Flow
```text
POST /api/session/start
  -> Sessions -> worker -> MockProducer.run(publish, stop)
  -> Publisher (sequence + latest state + bounded event ring)
  -> GET /api/state snapshot / WS /ws/live snapshot then events
```
No EEG, microphone or model feeds this default path.

## Tests / Verification
Commands actually run in this audit, from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
ATTUNE_PYTHON=/private/tmp/attune-backbone-venv/bin/python npm run test:live --prefix frontend
curl --max-time 5 -fsS http://127.0.0.1:5173/api/health
```
- Backend: PASS, 29 tests, including 19 foundation tests and 10 later adapter
  tests. Foundation coverage includes invalid packets, bounds, order, concurrency,
  idempotent commands, cancellation deadlines, worker failure, ASGI REST/WS,
  disconnect/reconnect and lag close 1013.
- Live suite: FAIL, one test, `Port 5173 is already in use`. The already-running
  user interface occupied that port. The harness requests Vite port 0, but the
  observed effective port was 5173. No implementation/test changes made to hide it.
- Existing frontend proxy health smoke: PASS, status ok, protocol_version 1.
  Health establishes transport availability, not model readiness.

## Known Limitations
Process-local, single-worker memory; no persistent replay, database, auth,
production hosting, hardware/model integration or physical clock synchronization.
Slow clients resnapshot and may miss intermediate events. Thread cancellation is
cooperative; the three-second join deadline cannot forcibly terminate a worker.
The live harness is not reliably isolated from a frontend already on port 5173.

## Historical Uncertainty
HEAD is `a3ee2ba21115cda4eb3d1cac469c2239892e03c4` (2026-09-11,
“Finalize ATTUNE UI handoff”). `backend/` and `frontend/` are untracked, and
`git log --all -- backend frontend` produces no commits. Phase assignment relies
on the current ledger and module responsibilities, not independently dated Git
changes. The ledger says source/producer interfaces existed as a prior draft;
their exact creation boundary is unprovable. Do not treat this document as a
statement that every current backend file was introduced during Phase 1.

## Files Relevant to This Phase
- `backend/app/protocol.py`
- `backend/app/publisher.py`
- `backend/app/sessions.py`
- `backend/app/server.py`
- `backend/adapters/base.py`
- `backend/adapters/mock.py`
- `backend/sources/base.py`
- `backend/tests/test_foundation.py`
- `backend/requirements.txt`, `backend/requirements-test.txt`, `backend/README.md`
- `AI_LEDGER.md`, `tests/TEST_REGISTRY.md`
