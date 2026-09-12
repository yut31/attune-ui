# NOVA Testing Strategy

The project should be developed in layers so failures are easy to locate.

## Testing pyramid for this project

### Layer 1 — Pure unit tests

Test individual functions and components without EEG hardware or networking.

Examples:

- attention percentage formatting,
- signal-quality labels,
- artifact-state logic,
- payload validation,
- smoothing helpers,
- component rendering.

These should be fast and deterministic.

### Layer 2 — UI component tests

Test UI behavior using fixed mock data.

Examples:

- attention card displays 82%,
- low signal quality shows a warning,
- disconnected state appears correctly,
- artifact state freezes or marks a prediction,
- speaker A/B state renders correctly.

### Layer 3 — API / transport tests

Test the contract between backend and frontend.

Examples:

- valid prediction payload is accepted,
- malformed payload is rejected safely,
- WebSocket reconnect behavior works,
- missing fields use defined fallbacks,
- backend status endpoint responds.

### Layer 4 — integration tests

Run multiple real application pieces together.

Examples:

```text
mock EEG -> backend -> websocket -> frontend
```

and later:

```text
real pipeline -> backend -> websocket -> frontend
```

### Layer 5 — manual demo smoke test

A short repeatable checklist before demos.

Examples:

1. Start backend.
2. Start frontend.
3. Enable demo stream.
4. Verify live chart updates.
5. Trigger low signal quality.
6. Trigger artifact state.
7. Stop backend.
8. Verify disconnected state.
9. Restart backend.
10. Verify recovery.

## Required test behavior

Each task should include at least:

- one happy-path test,
- one edge-case test,
- one failure-state test when applicable.

## Deterministic test data

Tests must not depend on random values unless the random seed is fixed.

Prefer fixtures like:

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

## Hardware independence

Most automated tests must run without:

- EEG headset,
- LSL hardware stream,
- microphone,
- internet connection.

Hardware tests should be clearly marked as optional integration tests.

## Test commands

Every new test command discovered or introduced should be documented here.

### Frontend

```bash
# Fill after inspecting package.json
# npm test
# npm run test
# npm run test:run
```

### Python

```bash
# Fill after inspecting pyproject.toml / requirements
# pytest
```

Do not invent a test command. Inspect the project configuration first.

## Single test registry

All tests must be indexed in:

`tests/TEST_REGISTRY.md`

## Phase 2 React transport client

From the repository root (Node 22.12+; tested with Node 24.18.0):

```bash
npm test --prefix frontend
npm run build --prefix frontend
ATTUNE_PYTHON=/private/tmp/attune-backbone-venv/bin/python npm run test:live --prefix frontend
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
```

`frontend/README.md` documents installation and launch. Unit tests use Node's
built-in runner, mocked transports/timers and one real Python mock fixture.
The separate live suite requires the Phase 1 Python dependencies and loopback
port permission; it creates and cleans up ephemeral backend/Vite servers.
No EEG/audio hardware, participant data, or scientific dependencies are needed.
