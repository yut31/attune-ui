# NOVA Test Registry

This is the single index for all project test cases.

Actual test files can remain next to the code or in framework-specific test folders.

Every test added by any human or AI must be registered here.

## Status legend

- `PLANNED`
- `IMPLEMENTED`
- `PASS`
- `FAIL`
- `SKIPPED`

## Test registry

| Test ID | Feature | Type | Test file | Test case | Expected behavior | Status |
|---|---|---|---|---|---|---|
| UI-000-T01 | Existing UI | unit/static | tests/test_ui.py | test_ui_000_t01_html_exists_and_is_readable | ui.html exists and is readable UTF-8, with content | PASS |
| UI-000-T02 | Existing UI | unit/static | tests/test_ui.py | test_ui_000_t02_required_dom_ids | all 12 required IDs exist on HTML elements | PASS |
| UI-000-T03 | Existing UI | unit/static | tests/test_ui.py | test_ui_000_t03_state_endpoint_request | frontend script fetches /state | PASS |
| UI-000-T04 | Existing UI | unit/static | tests/test_ui.py | test_ui_000_t04_frontend_state_fields | frontend script references all 13 current state fields | PASS |
| UI-000-T05 | Demo state | unit | tests/test_ui.py | test_ui_000_t05_backend_state_fields | safely imported real STATE contains all 13 required keys | PASS |
| UI-000-T06 | Demo state | unit | tests/test_ui.py | test_ui_000_t06_set_updates_and_restores_state | real _set updates values, preserves other fields, accepts empty/falsy updates; original STATE restored | PASS |
| UI-001-T01 | UI shell | component | TBD | renders main application | required dashboard sections render | PLANNED |
| UI-001-T02 | UI shell | component | TBD | renders without prediction data | no crash; no-data state visible | PLANNED |
| UI-002-T01 | payload contract | unit | TBD | accepts valid payload | parsed successfully | PLANNED |
| UI-002-T02 | payload contract | unit | TBD | malformed payload | handled safely | PLANNED |
| UI-003-T01 | demo stream | unit | TBD | deterministic stream starts | expected sequence emitted | PLANNED |
| UI-003-T02 | demo stream | unit | TBD | stream cleanup | timer/subscription cleaned up | PLANNED |
| UI-004-T01 | attention card | component | TBD | focused prediction | correct value and state | PLANNED |
| UI-004-T02 | attention card | component | TBD | no data | placeholder state | PLANNED |
| UI-005-T01 | signal quality | unit/component | TBD | good quality | GOOD state | PLANNED |
| UI-005-T02 | artifact state | unit/component | TBD | artifact true | warning shown | PLANNED |
| UI-006-T01 | history | unit | TBD | append values | values remain ordered | PLANNED |
| UI-006-T02 | history | unit | TBD | maximum history size | oldest values removed | PLANNED |
| UI-007-T01 | transport | integration | TBD | valid WebSocket message | UI receives payload | PLANNED |
| UI-007-T02 | transport | integration | TBD | malformed WebSocket message | app remains stable | PLANNED |
| UI-007-T03 | transport | integration | TBD | disconnect | disconnected state shown | PLANNED |
| UI-008-T01 | mock integration | integration | TBD | backend to UI | prediction visible | PLANNED |
| UI-009-T01 | real adapter | integration | TBD | real output mapping | conforms to UI contract | PLANNED |
| UI-010-T01 | demo | smoke | manual | full startup | system starts successfully | PLANNED |
| UI-010-T02 | demo fallback | smoke | manual | EEG unavailable | demo mode usable | PLANNED |

## Adding a test

Use this format:

```text
| FEATURE-T## | feature | unit/component/integration/smoke | path | condition | expectation | status |
```

Never delete historical tests simply because behavior changed.

If a test is intentionally retired, mark it `SKIPPED` and explain why below.

## Test run history

Append test runs here.

### TEMPLATE

**Date:** YYYY-MM-DD  
**Task:** UI-000  
**Agent:**  
**Command:**

```bash
command here
```

**Result:** PASS / FAIL

**Notes:**
-

### 2026-09-11 — UI-000

**Agent:** Codex

**Exact commands and results:**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_ui -v
```

Unavailable: exit 127, `python` command not found.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
```

PASS: 6 tests, all UI-000-T01 through UI-000-T06 passed.

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

Unavailable: exit 127, `python` command not found.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

FAIL: 8 unittest entries, 6 UI tests passed and 2 module import errors.
`test_combined` and `test_driving_pilot` cannot import `numpy` in the installed
`/usr/bin/python3` environment. Their test bodies did not run; existing-suite
regression validation remains incomplete. No dependencies installed.

**Scope:** Standard-library static HTML checks and the real demo STATE/_set with
engine dependencies temporarily stubbed and sys.modules restored after import.
No main/engine calls, hardware, datasets, server, or network used by the UI tests.
These checks do not execute JavaScript or verify visual rendering. Bytecode writes
were disabled to avoid creating files outside the three allowed paths.
