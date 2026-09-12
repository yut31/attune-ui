# Integration Matrix

| Component | NOVA | NOVA2026 | novaAAD | Status |
|---|---|---|---|---|
| Acquisition | application source protocol only | independent streaming/replay | independent auditory/source tooling | EXTERNAL |
| Preprocessing | none | research-owned | research-owned | EXTERNAL |
| EEG windows | `PreparedInput` metadata/native boundary | `EEGWindow` and processor | native project-specific inputs | ADAPTER READY |
| Artifact handling | preserves invalid/unavailable status | research-owned validity/reasons | research-owned | EXTERNAL |
| Riemann model | generic typed-result mapping only | `RiemannPipeline` / `Prediction` | not applicable | ADAPTER READY |
| PVT/vigilance | no scientific implementation | research-owned candidates | not applicable | MISSING |
| Auditory attention | generic typed-result mapping only | not connected here | research-owned decoder/controller | ADAPTER READY |
| Audio control | no scientific control | external | research-owned | EXTERNAL |
| Prediction contract | `PredictionResult` / typed outputs | native result awaiting mapping | native output awaiting mapping | IMPLEMENTED |
| Backend | Publisher, REST, WebSocket | adapter target | adapter target | IMPLEMENTED |
| WebSocket | versioned packet transport | external source | external source | IMPLEMENTED |
| Frontend | generic provider/task/output viewer | no provider-specific code | no provider-specific code | IMPLEMENTED |
| Mock provider | deterministic, explicit development data | no dependency | no dependency | IMPLEMENTED |
| NOVA2026 adapter | unavailable placeholder | unchanged external repo | not applicable | ADAPTER READY |
| novaAAD adapter | unavailable placeholder | not applicable | unchanged external repo | ADAPTER READY |

## Transfer Notes

### Portable shared application code

- `backend/app/prediction.py`
- `backend/app/providers.py`
- `backend/app/prepared_input.py`
- `backend/adapters/results.py`
- `frontend/src/decoders.js`
- `frontend/src/Dashboard.js`
- corresponding focused tests

### NOVA2026-specific contribution candidates

- Future reviewed mapping module for NOVA2026 native `Prediction`/`EEGWindow`.
- No current file should be transferred yet because the adapter is unavailable.

### novaAAD-specific contribution candidates

- Future reviewed mapping module for novaAAD native auditory outputs.
- No current file should be transferred yet because the adapter is unavailable.

### Documentation only

- `docs/development/PHASE_4.md`
- `docs/development/CURRENT_STATE.md`
- `docs/development/INTEGRATION_MATRIX.md`

### Local development only / do not transfer

- `node_modules/`, `frontend/dist/`, virtual environments, caches, recordings,
  datasets, checkpoints, generated audio, and local configuration.