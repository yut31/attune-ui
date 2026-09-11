# Master Prompt for Any Coding AI

You are working inside the NOVA hackathon repository with other humans and AI agents.

Your job is to make one small, isolated change without interfering with other work.

Before writing code:

1. Read `AGENTS.md`.
2. Read `PROJECT_STATE.md`.
3. Read `AI_LEDGER.md`.
4. Read `TESTING.md`.
5. Read `tests/TEST_REGISTRY.md`.
6. Inspect the relevant existing files and project configuration.
7. State:
   - what you believe the task is,
   - files you intend to read,
   - files you intend to modify/create,
   - tests you intend to add/run.

Do not edit a file listed as ACTIVE under another task in `AI_LEDGER.md`.

Rules:

- Make the smallest possible change.
- Preserve existing architecture.
- Do not refactor unrelated code.
- Do not rename/move/delete existing files without explicit permission.
- Do not modify ML/EEG processing for a UI-only task.
- Do not modify frontend for a model-only task unless explicitly requested.
- Reuse existing libraries where possible.
- Inspect package/project configuration before choosing commands.
- Never weaken or remove a test simply to make the build pass.
- New behavior requires tests.
- Prefer deterministic mocks.
- Automated tests should not require EEG hardware unless explicitly labeled integration/hardware tests.

Before coding, create or claim a task entry in the active section of `AI_LEDGER.md`.

After coding:

1. Run the smallest relevant test set.
2. Run broader relevant tests if practical.
3. Update `tests/TEST_REGISTRY.md`.
4. Append a completion entry in `AI_LEDGER.md`.
5. Report:
   - exact files changed,
   - exact tests added,
   - commands run,
   - results,
   - anything not completed.

If you discover that completion requires touching files outside your declared scope, stop and report the dependency instead of changing them.
