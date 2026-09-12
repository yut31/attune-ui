# Phase 2 — React Result Transport Client

## Status
Completed within the minimal communication/debug-client scope. Retrospective
verification has an open live-test port-isolation issue, detailed below.

## Goal
The `FRONTEND-002` ledger entry and `frontend/README.md` describe a minimal
React/Vite client proving that multiple Python packet types reach a normalized
frontend state. Graphics and scientific computation were explicitly deferred.

## Implemented
- `frontend/src/rest.js`: health/state/start/stop REST requests and HTTP errors.
- `frontend/src/transport.js`: REST snapshot bootstrap, WebSocket lifecycle,
  generation tokens, fetch cancellation, 10-second connection deadline,
  reconnect backoff from 500ms to 8s, connection/stale state and epoch recovery.
- `frontend/src/protocol.js`: JSON envelope and snapshot validation.
- `frontend/src/state.js`: latest normalized source/type streams, bounded to 128;
  sequence and per-stream timestamp protection, session reset and rejected count.
- `frontend/src/decoders.js`: attention, vigilance, sync, eeg_display Map registry;
  unknown types remain opaque. Later adapter fields are also present today.
- `frontend/src/Dashboard.js` / `main.jsx`: textual ATTUNE debug page, start/stop
  controls, connection/session metadata and result JSON; unavailable values are null.
- `frontend/vite.config.js`: loopback port 5173, `/api` and `/ws` proxies to 8001.
  React 19.2.0 / Vite 7.3.1 direct versions and a package lock are present.

## Architecture Changes
Introduces a separate React app; does not replace the legacy
`neuro-attention/src/ui.html` or its `/state` contract. The new UI has no EEG/model
imports, inference, filtering or signal analysis. Same-origin development proxies
avoid a backend CORS change. Generated `node_modules/` and `dist/` are locally ignored.

## Data Flow
```text
React mount -> GET /api/state -> validate snapshot -> normalized latest state
            -> WS /ws/live -> validate envelope -> sequence/timestamp checks
                          -> decoder registry -> state -> textual React sections
Disconnect -> cached state marked stale -> backoff -> fresh REST snapshot + WS
Buttons -> REST session commands -> Python producer -> result packets
```
Snapshot sequence gaps are valid. Replayed duplicates cannot replace newer data.
Connection status is separate from the session's running/stopped/error payload.

## Tests / Verification
Commands run in this audit, from repository root:

```bash
npm test --prefix frontend
npm run build --prefix frontend
ATTUNE_PYTHON=/private/tmp/attune-backbone-venv/bin/python npm run test:live --prefix frontend
curl --max-time 5 -fsS -o /dev/null -w 'frontend HTTP %{http_code}\n' http://127.0.0.1:5173/
```
- Frontend: PASS, 25 tests (22 original client tests, 3 adapter additions).
  Covers four known types, unknown/extended registry, malformed envelopes,
  optional/unavailable values, ordering, restart/reconnect, timeouts, retired
  callbacks, Python mock fixtures and escaped React static markup.
- Build: PASS, 29 modules, production assets generated.
- Live Python/Vite smoke suite: FAIL, one test, port 5173 occupied. The previous
  ledger records a pass; this audit does not claim a fresh pass. The harness's
  intended ephemeral Vite port is not what was observed.
- Existing running frontend: PASS, HTTP 200; proxy health also returned ok.
- No automated browser interaction or visual evaluation performed in this audit.

## Known Limitations
Minimal debug graphics only. No production reverse proxy/hosting, database or
authentication. No application heartbeat/measurement-age policy: a silently
half-open connection depends on socket/network failure detection. Mock data is
not real EEG. The live test conflicts with an existing frontend on 5173.
Build/static render success is not a browser usability or real-model validation.

## Historical Uncertainty
`frontend/` is untracked at audited HEAD
`a3ee2ba21115cda4eb3d1cac469c2239892e03c4`; there is no Phase 2 Git commit/tag.
The phase goal/boundary comes from the current ledger and README. The current
decoder contains Phase 3 additions, so its entire present content cannot be
assigned to Phase 2. Legacy HTML UI commits UI-000 through UI-009 are a separate
numbering sequence and must not be relabeled as these application phases.

## Files Relevant to This Phase
- `frontend/src/rest.js`, `frontend/src/transport.js`, `frontend/src/protocol.js`
- `frontend/src/state.js`, `frontend/src/decoders.js`
- `frontend/src/Dashboard.js`, `frontend/src/main.jsx`, `frontend/src/style.css`
- `frontend/index.html`, `frontend/vite.config.js`
- `frontend/package.json`, `frontend/package-lock.json`, `frontend/.gitignore`
- `frontend/tests/client.test.js`, `frontend/tests/live.integration.js`
- `frontend/README.md`, `TESTING.md`, `tests/TEST_REGISTRY.md`, `AI_LEDGER.md`
