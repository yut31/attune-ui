# NOVA UI Step-by-Step Build Plan

Each phase should be completed and tested before the next phase begins.

## UI-001 — UI shell

Goal:

Create the basic application layout without connecting to live data.

Suggested UI regions:

- app header,
- connection status,
- live attention card,
- signal quality card,
- live EEG / signal chart area,
- attention history area,
- system status/footer.

Tests:

- main screen renders,
- required sections exist,
- app does not crash with no data.

Do not touch:

- EEG pipeline,
- ML model,
- preprocessing.

---

## UI-002 — Stable frontend data type

Goal:

Define one frontend representation for predictions.

Initial conceptual contract:

```json
{
  "timestamp": 1000.0,
  "attention": 0.82,
  "confidence": 0.91,
  "signal_quality": 0.87,
  "artifact": false,
  "status": "focused"
}
```

Tests:

- valid payload accepted,
- invalid attention range rejected or normalized according to explicit design,
- missing required fields handled predictably.

---

## UI-003 — deterministic simulation mode

Goal:

Make the complete UI run without the real EEG pipeline.

Simulation should generate predictable test sequences rather than uncontrolled random data.

Example sequence:

```text
0.30 -> 0.45 -> 0.62 -> 0.78 -> 0.85 -> 0.74
```

Tests:

- stream starts,
- values update,
- stream stops,
- cleanup occurs when component unmounts.

---

## UI-004 — attention status card

Goal:

Display current attention and confidence.

Tests:

- focused state,
- unfocused state,
- boundary value,
- no-data state.

---

## UI-005 — signal quality and artifact state

Goal:

Expose whether a prediction should be trusted.

Possible states:

- GOOD
- FAIR
- POOR
- ARTIFACT
- DISCONNECTED

Tests:

- each state maps correctly,
- artifact warning appears,
- bad/missing input does not crash UI.

---

## UI-006 — history chart

Goal:

Display recent attention values over time.

Tests:

- points are appended,
- history has a defined maximum length,
- old values are removed,
- empty history renders safely.

---

## UI-007 — backend API / WebSocket adapter

Goal:

Move transport logic behind one adapter.

UI components should not open WebSockets directly.

Tests:

- connection opens,
- valid message parsed,
- malformed message handled,
- disconnect handled,
- reconnect behavior tested if implemented.

---

## UI-008 — mock backend integration

Goal:

Run:

```text
mock backend -> transport -> frontend
```

Tests:

- end-to-end mock prediction reaches UI,
- disconnection is visible,
- reconnect succeeds if supported.

---

## UI-009 — real NOVA pipeline integration

Goal:

Replace mock backend source with the real combined pipeline without changing UI behavior.

Tests:

- adapter converts real model output into UI contract,
- frontend remains unchanged,
- no hardware-independent tests are broken.

---

## UI-010 — demo hardening

Goal:

Prepare for the hackathon demo.

Include:

- demo mode fallback,
- clear connection state,
- graceful errors,
- predictable startup,
- one-command or clearly documented startup flow.

Tests:

- full smoke-test checklist,
- backend unavailable,
- real stream unavailable,
- demo mode still works.
