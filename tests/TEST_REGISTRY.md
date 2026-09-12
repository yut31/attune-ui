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
| UI-001-T01 | UI shell | unit/static | tests/test_ui.py | test_ui_001_t01_shell_dom_ids | all 12 required IDs exist exactly once | PASS |
| UI-001-T02 | UI shell | unit/static | tests/test_ui.py | test_ui_001_t02_state_request_preserved | /state is still fetched | PASS |
| UI-001-T03 | UI shell | unit/static | tests/test_ui.py | test_ui_001_t03_state_fields_preserved | all 13 state fields remain referenced | PASS |
| UI-001-T04 | UI shell | unit/static | tests/test_ui.py | test_ui_001_t04_attune_heading | ATTUNE branding and header markup exist, including span with systemText ID (UI-001C) | PASS |
| UI-001-T05 | UI shell | unit/static | tests/test_ui.py | test_ui_001_t05_talker_headings | both talker headings exist | PASS |
| UI-001-T06 | UI shell | unit/static | tests/test_ui.py | test_ui_001_t06_eeg_canvas | labeled EEG canvas with positive dimensions and animation hook exists | PASS |
| UI-001-T07 | UI shell | smoke | inline Node VM harness (session command) | deterministic offline state transitions | waiting, A/B, EEG drawing, session values, done, disconnect and recovery work | PASS |
| UI-002-T01 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t01_demo_control_and_required_ids | demo button and required IDs exist | PASS |
| UI-002-T02 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t02_simulated_disclosure | explicit simulated-data and no-playback disclosure exists | PASS |
| UI-002-T03 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t03_real_endpoint_preserved | real /state fetch and stale-response guard remain | PASS |
| UI-002-T04 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t04_no_randomness | no Math.random in frontend script | PASS |
| UI-002-T05 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t05_existing_demo_contract | demo uses exactly the existing 13 fields; accuracy unavailable | PASS |
| UI-002-T06 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t06_deterministic_eeg_source | EEG helper uses deterministic sine waves and elapsed time | PASS |
| UI-002-T07 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t07_both_attention_states | 16-second cycle includes A and B | PASS |
| UI-002-T08 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t08_attune_branding | ATTUNE heading and title preserved | PASS |
| UI-002-T09 | ATTUNE Demo Mode | unit | tests/test_ui.py | test_ui_002_t09_determinism_and_mode_isolation | executed JS: deterministic values, smooth transitions, bounded EEG, demo isolation, exit cleanup and real recovery | PASS |
| UI-003-T01 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t01_vigilance_section | vigilance panel exists | PASS |
| UI-003-T02 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t02_lapse_display | lapse risk text and compact meter exist | PASS |
| UI-003-T03 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t03_real_unavailable_and_demo_exit | real mode never displays risk; exit immediately clears simulated risk, including offline/warmup | PASS |
| UI-003-T04 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t04_deterministic_lapse | equal times and repeated cycles yield equal risk | PASS |
| UI-003-T05 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t05_bounded_smooth_lapse | risk stays finite in 0..1 and varies smoothly through low/high ranges | PASS |
| UI-003-T06 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t06_no_randomness | no Math.random | PASS |
| UI-003-T07 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t07_display_thresholds | Attentive below .4, Watch from .4 to below .7, Elevated lapse risk from .7 | PASS |
| UI-003-T08 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t08_contract_unchanged | existing state keys unchanged; no lapse_score required or auditory inference | PASS |
| UI-003-T09 | Vigilance display | unit | tests/test_ui.py | test_ui_003_t09_existing_shell_preserved | ATTUNE, talkers, EEG and demo disclosure/control remain | PASS |
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


### 2026-09-11 — UI-001

**Agent:** Codex

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

**Results:** Targeted run PASS: 12 tests (6 retained UI-000 + 6 new UI-001).
Discovery FAIL: 14 entries, 12 passed, 2 import errors: `test_combined` and
`test_driving_pilot` both require unavailable `numpy`. No dependencies changed.

**Additional smoke check:** `node` via stdin with built-in `fs`, `vm`, and `assert`;
executed the actual inline UI script with a minimal DOM/canvas stub and a mocked
`fetch`. PASS for warmup, attended A/B, correlation, accuracy, elapsed time, EEG
drawing, completion, disconnection and recovery. No network or server used.
This was a one-off session harness, not an additional installed test dependency.

**Scope notes:** UI-001-T01/T02 previously had generic planned descriptions;
they now follow the explicitly requested UI-001 test mapping. UI-000 tests and
historical run results remain intact. Static markup tests do not prove computed
visibility or visual layout. No browser rendering review performed. Zero
`correct_frac` remains unavailable/ambiguous and is displayed as a dash, preserving
the previous UI's truthy availability convention. Correlation is not a confidence
percentage.


### 2026-09-11 — UI-001B

**Agent:** Codex  
**Status:** PASS

**Updated test:** UI-001-T04 (`test_ui_001_t04_nova_heading`; internal method name
retained). Expects ATTUNE and additionally checks the browser title, subtitle,
initial footer description and absence of old NOVA branding in ui.html.
No tests deleted or weakened; no additional test methods needed.

**Exact command:**
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
```

**Result:** PASS, all 12 tests. Bytecode writes disabled to respect file scope.
Branding-only text changes; /state, DOM IDs, data fields and JS logic unchanged.


### 2026-09-11 — UI-001C

**Agent:** Codex  
**Result:** PASS, 12 tests.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
```

Updated UI-001-T04: renamed to `test_ui_001_t04_attune_heading`, retaining every
assertion and adding an explicit parsed-element check for a span with
`id="systemText"`. This check rejects the reported malformed `<spanid=...>` tag.
The on-disk ui.html already contained the correct `<span id="systemText">Connecting</span>`;
no production edit was necessary. Historical test names above describe prior runs.


### 2026-09-11 — UI-002

**Agent:** Codex

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

**Results:** Final UI run PASS: 21 tests, no skips (12 existing, 9 new).
Full discovery: 23 entries, 21 passed, 2 import errors: test_combined and
 test_driving_pilot cannot import numpy. Existing environment-blocked issue;
no packages installed or tests hidden.

**Initial run:** 20 passed, UI-002-T05 failed because the new source-inspection
regex treated the numeric ternary operand `0:` as a field name. Restricted the
regex to identifier names and reran successfully. Runtime exact-key checks also pass.

**Execution coverage:** T09 runs the real inline script in the existing Node
executable using only built-in vm/assert/fs, fake clock and DOM/canvas/timers/fetch.
Tests repeated timestamps, phase boundaries, both talkers, smooth gains/correlations,
six finite bounded traces, draw calls, no demo fetches, late real successes/errors,
rapid mode round trips, immediate exit cleanup, offline real mode and recovery.
Node is optional on other machines (T09 explicitly skips if absent); it was present
and this test passed here. No new dependency or JS testing framework was introduced.

**Scope:** UI-002-T01/T02 replace generic planned contract placeholders with the
user's explicit Demo Mode test mapping. Earlier run history stays intact. Visual
browser review and hardware/backend integration are not part of this test run.


### 2026-09-11 — UI-003

**Agent:** Codex

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

**Results:** UI suite PASS, 30 tests with no skips (21 existing + 9 UI-003).
Full discovery: 32 entries, 30 passed, 2 existing module import errors:
`test_combined` and `test_driving_pilot` cannot import numpy. No dependencies
installed, tests modified to hide errors, or existing tests skipped.

**Coverage:** New Node VM checks execute actual frontend helpers and mode paths
with mocked DOM, clock and network. Verify periodic repeatability, 2,401 bounded
samples, smoothness, exact display thresholds, unavailable real/warmup/offline
states and immediate cleanup on demo exit. Node was already installed and all
runtime checks passed; these optional checks skip on machines without Node.

**Formula:** `0.5 - 0.4*cos(2*pi*(t % 24)/24)`; range .1–.9, 24-second cycle.
Display thresholds: below .4 Attentive; .4 to below .7 Watch; .7+ Elevated lapse
risk. These are display-only labels for synthetic values, not model thresholds.
Real mode has no score. Demo lapse values remain outside the 13-field state
contract and are never derived from auditory attention or EEG.

**Registry note:** UI-003-T01/T02 generic planned demo-stream placeholders now
follow the user's explicit vigilance-task mapping; past test history retained.
No browser visual review performed.
