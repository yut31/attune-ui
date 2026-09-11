# Bug Fix Agent Prompt

Follow `prompts/00_MASTER_AGENT_PROMPT.md`.

## Role

Fix exactly one reproduced bug.

## Required order

1. Reproduce the bug.
2. Add a regression test that fails for the bug.
3. Make the smallest fix.
4. Confirm the regression test passes.
5. Run nearby relevant tests.
6. Update test registry.
7. Update ledger.

Do not combine the bug fix with cleanup/refactoring.

If the bug cannot be reproduced, do not guess at a fix.
