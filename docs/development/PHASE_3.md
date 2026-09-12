# Phase 3 — Independent Scientific Result Adapter Boundary

## Status
Completed for result conversion and interface preparation. Connecting a real
acquisition/preprocessing/model runner is not implemented by this phase.

## Goal
The `ADAPTER-003` ledger entry describes separating EEG input, audio input,
attention, vigilance, synchronization and web transport while preparing the
existing NOVA/novaAAD results for the new application. No final hardware assumed.

## Implemented
- `backend/adapters/contracts.py`: `AttentionResult`, `VigilanceResult`,
  `SyncResult`, `EEGDisplayResult`; independent algorithm/sync/publish protocols.
- `backend/adapters/results.py`: `encode_result()` validates and detaches JSON;
  `ResultAdapter.publish(result)` sends it through a session-scoped callback;
  `ResultProducer` wraps `run_results(adapter, stop)` for `create_app()` injection.
- `backend/adapters/legacy.py`: `aad_result()` maps 0→A, 1→B, None→unavailable,
  explicit uncertain→uncertain. `lapse_result()` preserves the NOVA scalar.
  `combined_results()` accepts a CombinedDecision-shaped object or dictionary.
- Attention decision is explicitly A/B/uncertain/unavailable; uncertain does not
  introduce a new classifier or correlation threshold.
- Lapse output uses `metric=lapse_probability`, `lapse_score`, `score=null`.
  This names the existing slowest-session-decile class score; it does not prove
  calibrated lapse probability or turn that score into validated vigilance.
- Sync metadata supports status, offset_ms and drift_warning. Default status is
  unknown; offset/warning are null. No measured physical synchronization is invented.
- The frontend decoder recognizes these additive payload fields; transport is unchanged.

## Architecture Changes
Adapter code has no model imports or acquisition side effects. Existing
`backend/sources/base.py` EEGSource/AudioSource protocols remain independent.
The coordinator must own real sources, preprocessing, timestamp conversion,
model calls, bounded reads and finally cleanup. Scientific implementations are
neither moved into the backend nor rewritten to satisfy the interfaces.

## Data Flow
```text
Existing model result object/scalar (future coordinator must produce it)
  -> aad_result / lapse_result / combined_results or explicit Result record
  -> ResultAdapter.publish
  -> session callback -> Publisher -> REST/WS -> existing client decoders
```
This conversion path is tested with fixtures. The default server still runs
MockProducer; it does not call CombinedPipeline or LapsePredictor.

## Tests / Verification
Commands run in this audit, from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
npm test --prefix frontend
npm run build --prefix frontend
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```
- Backend: PASS, 29 tests, including 10 adapter tests for result semantics,
  unavailable sync, malformed data, explicit timestamp conversion boundary,
  unchanged display samples, session/sequence ownership and ASGI REST/WS lifecycle.
- Frontend: PASS, 25 tests, including 3 tests of explicit attention/lapse semantics
  and real Python adapter fixtures through frontend normalization.
- Build: PASS, 29 modules.
- Root discovery: FAIL, 149 reported tests: 147 legacy UI tests pass; two loader
  errors (`test_combined`, `test_driving_pilot`) because Python lacks numpy.
  Actual scientific tests did not execute. No packages installed to conceal this.

## Known Limitations
No real model/checkpoint execution verified in this audit. No final physical
source setup or window assembler, no time-domain alignment, no new algorithms.
Legacy EEG/audio readers do not directly implement the new timeout/lifecycle
protocols. Source wrappers and a coordinator are still required. Combined results
are independent publications, not a transaction. Producer and result simulation
flags must be supplied consistently. The default mock's drift_warning=false is
simulated; it differs deliberately from the adapter's unknown/null default.

## Historical Uncertainty
These adapters are untracked at HEAD
`a3ee2ba21115cda4eb3d1cac469c2239892e03c4`; exact phase edits are not recoverable
from Git. The `ADAPTER-003` ledger entry is retrospective evidence, not a commit.
`CombinedPipeline` and NOVA inference are in the earlier baseline commit
`35bd4da`; their existence must not be attributed to Phase 3. The ledger reports
no scientific rewrites, and the current tracked diff contains only coordination/
testing documents, consistent with that claim.

## Files Relevant to This Phase
- `backend/adapters/contracts.py`, `backend/adapters/results.py`
- `backend/adapters/legacy.py`, `backend/adapters/README.md`
- `backend/sources/base.py` (existing protocol boundary)
- `backend/tests/test_adapters.py`
- `frontend/src/decoders.js`, `frontend/tests/adapters.test.js`
- `neuro-attention/src/combined_pipeline.py` (pre-existing result shape)
- `base/src/nova2026/inference.py` (pre-existing predictor)
- `tests/TEST_REGISTRY.md`, `AI_LEDGER.md`
