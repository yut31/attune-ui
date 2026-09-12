# Phase 4 — Common Provider Integration Boundary

## Purpose

NOVA is the application/integration workspace for independently developed
NOVA2026 and novaAAD research repositories. This phase gives both systems one
transport-safe application boundary without copying either research tree.

## Architecture

```text
NOVA2026 adapter ─┐
novaAAD adapter ───┼─> PredictionProvider -> PredictionResult -> Publisher -> WebSocket/API -> React frontend
mock provider ────┘
```

Research repositories own acquisition, preprocessing, artifact handling, native
window contracts, models, and scientific timing. NOVA owns transport and display.

## Common Provider Interface

`backend/app/providers.py` defines `PredictionProvider.predict(prepared_input)`,
and `backend/app/prepared_input.py` carries only application metadata plus an
optional native object. NOVA does not define a second scientific EEG window.

The provider registry selects `mock`, `nova2026`, or `nova_aad`. A requested real
provider never silently falls back to mock data.

### Transfer classification

- **PORTABLE SHARED APPLICATION CODE:** `backend/app/prediction.py`,
  `backend/app/providers.py`, `backend/app/prepared_input.py`, generic adapter
  serialization, frontend decoder/viewer, and focused tests.
- **NOVA2026 ADAPTER CODE:** `backend/adapters/research.py:NOVA2026Provider`
  placeholder only. Do not transfer it to NOVA2026 until a reviewed coordinator
  mapping exists.
- **novaAAD ADAPTER CODE:** `backend/adapters/research.py:NovaAADProvider`
  placeholder only. Do not transfer it to novaAAD until its callable output
  boundary is reviewed.
- **LOCAL DEVELOPMENT ONLY / DO NOT TRANSFER:** mock provider selection,
  virtual environments, `node_modules`, `frontend/dist`, caches, recordings,
  datasets, checkpoints, and generated files.
- **DOCUMENTATION ONLY:** this phase document, current state, and integration
  matrix.

## PredictionResult

`backend/app/prediction.py` supports explicit `ok`, `invalid`, `unavailable`, and
`error` states, provider identity/version, task, timestamp/window identity,
reasons, metadata, and multiple typed outputs:

```json
{
  "name": "speaker_a_correlation",
  "value": 0.18,
  "semantic_type": "correlation",
  "label": null
}
```

Supported semantic types include probability, score, correlation, distance,
class, boolean, ratio, measurement, and development. Correlations and scores are
never relabeled as confidence or probability.

## Providers and Adapters

`MockPredictionProvider` is deterministic, visibly mock/development data, and
does not claim vigilance, focus, lapse, or auditory-attention inference.

`NOVA2026Provider` currently returns `unavailable` because no reviewed native
coordinator is connected in NOVA. NOVA2026's real Riemann `Prediction` shape was
inspected read-only; its validity, timing, classes, and probabilities still need
an explicitly reviewed coordinator mapping.

`NovaAADProvider` currently returns `unavailable` because the novaAAD checkout
does not expose a reviewed live callable boundary from this application layer.
The generic `result_from_native()` helper can preserve typed native outputs once a
coordinator supplies them; it does not run or duplicate the auditory decoder.

## Backend and Frontend

`ResultAdapter` serializes `PredictionResult` as a `prediction` packet through the
existing Publisher, REST state, and WebSocket stream. The React frontend decodes
provider identity, task, status, reasons, and all typed outputs generically. It
does not assume providers share one scalar or one scientific label.

## Tests

Backend tests cover serialization, multiple outputs, semantic types, status
states, deterministic mock behavior, provider registry selection, unavailable
real providers, and publisher preservation. Frontend tests cover NOVA2026-style
probability outputs, novaAAD-style correlation/class outputs, multiple outputs,
mock identity, unavailable states, and provider substitution.

## Current Limitations

No external research provider is connected. No NOVA2026 or novaAAD code was
modified. The current end-to-end path is mock provider -> application publisher
-> WebSocket/API -> generic React viewer.

## Next Step

Define one reviewed coordinator per external repository that receives that
repository's already-prepared native result/window and maps it to typed outputs.
That work must preserve validity, timing, provider identity, and semantic types.