# NOVA AI Coordination Pack

This pack is designed for a repository where multiple coding AIs may work at different times.

## Put these files at repository root

```text
AGENTS.md
PROJECT_STATE.md
AI_LEDGER.md
TESTING.md
UI_BUILD_PLAN.md
README_AI_WORKFLOW.md
```

Keep these directories:

```text
prompts/
templates/
tests/
```

If the repository already has a `tests/` folder, merge `TEST_REGISTRY.md` into that folder rather than creating a competing test hierarchy.

## Recommended workflow for every feature

### Step 1 — choose one small task

Example:

`UI-001: create dashboard shell`

### Step 2 — reserve files

Add the task to `AI_LEDGER.md`.

Example:

```text
| UI-001 | Codex | ACTIVE | frontend/src/App.tsx; frontend/src/components/Dashboard.tsx | 2026-09-11 |
```

### Step 3 — give the AI three things

1. `prompts/00_MASTER_AGENT_PROMPT.md`
2. the role prompt, such as `prompts/01_UI_BUILDER.md`
3. a filled copy of `prompts/06_UI_TASK_PROMPT_TEMPLATE.md`

### Step 4 — AI implements only that task

The AI must add tests before declaring completion.

### Step 5 — test agent checks it

Give another AI:

- `prompts/00_MASTER_AGENT_PROMPT.md`
- `prompts/02_TEST_AGENT.md`
- the completed task description.

The testing agent should primarily add/inspect tests, not redesign the feature.

### Step 6 — reviewer checks it

Use `prompts/03_REVIEW_AGENT.md`.

### Step 7 — update registry and ledger

Nothing is considered done until:

- tests are registered,
- commands/results are recorded,
- ledger has the handoff.

### Step 8 — start the next UI task

Proceed through `UI_BUILD_PLAN.md`.

## Why this avoids AI interference

There are four safeguards:

1. **File ownership** — active tasks reserve files.
2. **Narrow tasks** — one agent does one behavior.
3. **Stable interfaces** — UI does not depend on model internals.
4. **Central tests** — all behavior is indexed in one registry.

## Git recommendation

For maximum safety, give each substantial AI task its own Git branch or worktree.

Example names:

```text
ui/UI-001-dashboard-shell
ui/UI-002-payload-contract
test/UI-001-dashboard-tests
fix/UI-004-attention-boundary
```

Avoid having two agents edit the same working tree at the same time.

Even with the ledger, separate branches/worktrees provide the strongest protection against accidental overwrites.

## Useful human rule

Before accepting an AI's work, always inspect:

```bash
git status
git diff --stat
git diff
```

Then run the tests recorded in the ledger.

Never accept "tests pass" without a recorded command.
