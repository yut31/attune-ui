# NOVA Multi-Agent Working Rules

This file is the shared contract for every AI agent working in this repository.

## 1. Primary rule

**Do not change anything outside the exact task scope.**

Before editing code, every agent must:

1. Read `PROJECT_STATE.md`.
2. Read `AI_LEDGER.md`.
3. Read `TESTING.md`.
4. Read the task-specific prompt.
5. Inspect the existing implementation before proposing changes.
6. List the files it intends to modify.
7. Confirm that those files are not currently owned by another active task in `AI_LEDGER.md`.

If another task owns a file, do not edit it.

## 2. Never do these without explicit permission

- Do not rename existing files or folders.
- Do not move existing files.
- Do not delete existing code.
- Do not rewrite another teammate's implementation.
- Do not perform broad refactors.
- Do not change public APIs unless the task explicitly requires it.
- Do not replace dependencies or frameworks.
- Do not change model behavior while working on UI-only tasks.
- Do not modify EEG preprocessing while working on frontend tasks.
- Do not change test expectations merely to make tests pass.
- Do not remove failing tests.
- Do not silently update configuration, ports, environment variables, or data formats.
- Do not format unrelated files.

## 3. Small-change rule

Prefer the smallest change that completes the task.

A good task should normally affect:

- one component,
- one feature,
- one interface,
- or one testable behavior.

Large changes must be split into smaller tasks.

## 4. Interface-first rule

The UI should depend on a stable application interface rather than directly on EEG/model internals.

Example application payload:

```json
{
  "timestamp": 0,
  "attention": 0.82,
  "confidence": 0.91,
  "signal_quality": 0.87,
  "artifact": false,
  "status": "focused"
}
```

If the backend payload needs to change:

1. document the proposed change,
2. update the interface contract,
3. add tests,
4. then update consumers.

## 5. Test requirement

Every functional change must include tests.

An agent is not finished until it reports:

- tests added,
- tests run,
- commands used,
- results,
- known limitations.

All test cases must be registered in `tests/TEST_REGISTRY.md`.

## 6. Completion requirement

At the end of a task, the agent must append a handoff entry to `AI_LEDGER.md`.

The entry must contain:

- task ID,
- status,
- files changed,
- tests added,
- tests run,
- result,
- assumptions,
- remaining issues,
- recommended next task.

Do not rewrite old ledger entries.

## 7. Stop conditions

Stop and ask for human review instead of guessing if:

- required data format is unclear,
- another task is modifying the same file,
- a change would alter EEG/model behavior,
- a dependency must be upgraded,
- existing tests contradict expected behavior,
- a change would require deleting or replacing teammate code,
- secrets, credentials, hardware settings, or production configuration are involved.

## 8. Definition of done

A task is complete only when:

- requested behavior exists,
- existing behavior is preserved,
- new tests exist,
- relevant existing tests still pass,
- test registry is updated,
- ledger is updated,
- no unrelated files were changed.
