# NOVA Project State

This is the shared short-form state document for humans and AI agents.

Keep this file concise. Update it only when project-level facts change.

## Product

NOVA combines EEG processing / attention decoding with a user-facing real-time interface.

Current priority:

1. Build a reliable UI.
2. Connect the UI to a stable simulated data source.
3. Connect the same interface to the real NOVA pipeline.
4. Add clear signal-quality / artifact status.
5. Only then consider additional artifact rejection or ML improvements.

## Repository status

The previously separate NOVA2026 and novaAAD work has been combined into one VS Code workspace.

Do not assume folder names. Inspect the workspace before editing.

## Current UI strategy

Recommended separation:

```text
EEG / replay / simulation
        |
        v
processing + model
        |
        v
stable application payload
        |
        v
backend transport
        |
        v
UI
```

The UI must not depend directly on model implementation details.

## Development principle

Every UI feature should first work with deterministic mock data.

Then test:

1. component behavior,
2. frontend data handling,
3. transport/integration behavior,
4. real pipeline behavior.

This prevents UI work from being blocked by EEG hardware or ML availability.

## Shared test location

All tests may remain in framework-appropriate directories, but every test case must also be indexed in:

`tests/TEST_REGISTRY.md`

This is the single source of truth for what is tested.

## Coordination

All agents must read:

- `AGENTS.md`
- `PROJECT_STATE.md`
- `AI_LEDGER.md`
- `TESTING.md`

before editing code.
