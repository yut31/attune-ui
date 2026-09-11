# UI Task Prompt Template

Give this together with the master prompt.

## Task ID

`UI-___`

## Goal

Implement:

`<one specific UI behavior>`

## Allowed files

- `<file or directory>`

## Do not touch

- EEG preprocessing
- model training
- inference logic
- unrelated components
- files owned by other active tasks

## Input contract

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

Change this only if the task explicitly says to.

## Acceptance criteria

- [ ] 
- [ ] 
- [ ] 

## Required tests

1. Happy path:
2. Edge case:
3. Error/no-data state:

Register them in `tests/TEST_REGISTRY.md`.

## Finish

Do not start the next task.

Finish this task, record the handoff, and stop.
