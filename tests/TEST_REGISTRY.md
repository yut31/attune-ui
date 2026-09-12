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
| UI-004-T01 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t01_signal_section | signal-quality section exists | PASS |
| UI-004-T02 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t02_quality_display | EEG quality text and meter exist | PASS |
| UI-004-T03 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t03_artifact_display | artifact status text exists | PASS |
| UI-004-T04 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t04_real_unavailable | real mode displays unavailable and no invented values | PASS |
| UI-004-T05 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t05_deterministic_quality | identical elapsed times produce identical quality/artifact results | PASS |
| UI-004-T06 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t06_quality_bounds_and_smoothness | quality is bounded 0..1 and smooth | PASS |
| UI-004-T07 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t07_quality_thresholds | Good >= .75, Fair >= .45 and < .75, Poor < .45 | PASS |
| UI-004-T08 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t08_artifact_interval | clean/artifact text and low-quality artifact interval boundaries verified | PASS |
| UI-004-T09 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t09_no_randomness | no Math.random | PASS |
| UI-004-T10 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t10_backend_contract_unchanged | 13-field backend contract preserved; no inference from unrelated fields | PASS |
| UI-004-T11 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t11_existing_features | ATTUNE, vigilance, talkers, EEG and demo remain | PASS |
| UI-004-T12 | Signal-quality display | unit | tests/test_ui.py | test_ui_004_t12_exit_resets_quality_and_artifact | demo exit immediately resets metrics; offline/recovery and pending-response isolation verified | PASS |
| UI-005-T01 | Session History | unit | tests/test_ui.py | test_ui_005_t01_section | Session History exists | PASS |
| UI-005-T02 | Session History | unit | tests/test_ui.py | test_ui_005_t02_attention_labels | attention history with visible A/B legend | PASS |
| UI-005-T03 | Session History | unit | tests/test_ui.py | test_ui_005_t03_vigilance_history | lapse history exists | PASS |
| UI-005-T04 | Session History | unit | tests/test_ui.py | test_ui_005_t04_signal_history | signal history and artifact stripe legend exist | PASS |
| UI-005-T05 | Session History | unit | tests/test_ui.py | test_ui_005_t05_determinism | equal demo time produces equal bounded values | PASS |
| UI-005-T06 | Session History | unit | tests/test_ui.py | test_ui_005_t06_bounded_history | 30 one-second samples maximum; duplicates ignored and expired samples removed | PASS |
| UI-005-T07 | Session History | unit | tests/test_ui.py | test_ui_005_t07_reuses_helpers | history values match existing demo helpers | PASS |
| UI-005-T08 | Session History | unit | tests/test_ui.py | test_ui_005_t08_no_randomness | no Math.random | PASS |
| UI-005-T09 | Session History | unit | tests/test_ui.py | test_ui_005_t09_real_vigilance_unavailable | real lapse history empty and awaiting pipeline | PASS |
| UI-005-T10 | Session History | unit | tests/test_ui.py | test_ui_005_t10_real_signal_unavailable | real signal history empty and awaiting pipeline | PASS |
| UI-005-T11 | Session History | unit | tests/test_ui.py | test_ui_005_t11_contract | existing backend fields unchanged | PASS |
| UI-005-T12 | Session History | unit | tests/test_ui.py | test_ui_005_t12_preserved_features | existing ATTUNE dashboard and demo preserved | PASS |
| UI-005-T13 | Session History | unit | tests/test_ui.py | test_ui_005_t13_exit_clears_and_real_recovers | simulated rows cleared immediately; stale responses ignored; real attention resumes | PASS |
| UI-005-T14 | Session History | unit | tests/test_ui.py | test_ui_005_t14_no_external_dependencies | no external script/link/import dependency | PASS |
| UI-006-T01 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t01_adapter_exists | normalizeState exists | PASS |
| UI-006-T02 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t02_valid_mapping | all current fields map into grouped frontend structure | PASS |
| UI-006-T03 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t03_invalid_defaults | null/non-object input yields safe unavailable defaults | PASS |
| UI-006-T04 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t04_attended_validation | only numeric 0/1 accepted | PASS |
| UI-006-T05 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t05_eeg_validation | invalid EEG rejected; valid rectangular finite traces retained | PASS |
| UI-006-T06 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t06_finite_numbers_and_strings | nonfinite/mistyped values safely default | PASS |
| UI-006-T07 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t07_real_path_normalized | real fetch passes through adapter and malformed data renders unavailable | PASS |
| UI-006-T08 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t08_normalized_attention_rendering | rendering uses grouped attention | PASS |
| UI-006-T09 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t09_normalized_session_rendering | rendering uses grouped session | PASS |
| UI-006-T10 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t10_normalized_history | history uses valid normalized talker; invalid talker not recorded | PASS |
| UI-006-T11 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t11_no_fabricated_metrics | no future metrics in normalized output | PASS |
| UI-006-T12 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t12_backend_unchanged | 13 backend keys unchanged | PASS |
| UI-006-T13 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t13_demo_determinism | demo remains deterministic through adapter | PASS |
| UI-006-T14 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t14_no_randomness | no Math.random | PASS |
| UI-006-T15 | Frontend adapter | unit | tests/test_ui.py | test_ui_006_t15_features_preserved | existing dashboard remains | PASS |
| UI-007-T01 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t01_normalized_vigilance_object | normalized vigilance object contains lapseScore | PASS |
| UI-007-T02 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t02_valid_lapse_scores | finite 0, 0.5, and 1 values normalize unchanged | PASS |
| UI-007-T03 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t03_missing_and_null_scores | missing and null scores normalize to null | PASS |
| UI-007-T04 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t04_numeric_string_rejected | numeric strings are rejected without coercion | PASS |
| UI-007-T05 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t05_nonfinite_scores_rejected | NaN and Infinity normalize to null | PASS |
| UI-007-T06 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t06_out_of_range_scores_rejected | values outside [0,1] normalize to null | PASS |
| UI-007-T07 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t07_no_fabricated_metrics | signal quality, artifact, and confidence are not fabricated | PASS |
| UI-007-T08 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t08_real_missing_score_is_unavailable | missing real score preserves Awaiting pipeline UI | PASS |
| UI-007-T09 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t09_real_score_uses_existing_label | valid real score uses existing vigilance thresholds | PASS |
| UI-007-T10 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t10_real_score_not_simulated | real score is labeled pipeline, not simulated | PASS |
| UI-007-T11 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t11_demo_remains_deterministic_and_separate | demo lapse helper remains deterministic and separate | PASS |
| UI-007-T12 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t12_real_history_consumes_normalized_score | real history records normalized lapse score | PASS |
| UI-007-T13 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t13_missing_real_values_are_gaps | missing real seconds render gaps without zero/carry-forward | PASS |
| UI-007-T14 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t14_real_signal_history_unavailable | real signal-quality history remains unavailable | PASS |
| UI-007-T15 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t15_state_fetch_is_preserved | no-store /state polling remains intact | PASS |
| UI-007-T16 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t16_backend_state_remains_thirteen_fields | live_demo.STATE remains the current 13-field contract | PASS |
| UI-007-T17 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t17_no_randomness | no Math.random is introduced | PASS |
| UI-007-T18 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t18_no_external_resources | no external dependencies or resources are introduced | PASS |
| UI-007-T19 | Lapse-score readiness | unit | tests/test_ui.py | test_ui_007_t19_previous_features_remain | UI-001 through UI-006 feature markers remain present | PASS |
| UI-008-T01 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t01_initial_connecting_state | initial Real Mode is connecting before a valid response | PASS |
| UI-008-T02 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t02_valid_response_marks_connected | valid response marks backend connected | PASS |
| UI-008-T03 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t03_fetch_rejection_continues_polling | fetch rejection is handled and polling continues | PASS |
| UI-008-T04 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t04_non_ok_response_unavailable | explicit non-OK response marks backend unavailable | PASS |
| UI-008-T05 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t05_json_parse_failure_safe | JSON failure leaves safe unavailable UI | PASS |
| UI-008-T06 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t06_malformed_top_level_safe | malformed top-level payload produces no measurements | PASS |
| UI-008-T07 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t07_failure_clears_previous_measurements | failure clears previously displayed live measurements | PASS |
| UI-008-T08 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t08_success_recovers_after_failure | later valid response recovers the UI | PASS |
| UI-008-T09 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t09_older_real_response_ignored | older Real response cannot overwrite newer response | PASS |
| UI-008-T10 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t10_mode_generation_ignores_real_after_demo | mode generation rejects stale Real response in Demo | PASS |
| UI-008-T11 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t11_real_to_demo_isolates_history | Real history is cleared on Demo entry | PASS |
| UI-008-T12 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t12_demo_to_real_clears_simulated_history | Demo history is cleared on Real entry | PASS |
| UI-008-T13 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t13_real_waits_for_fresh_response | returning to Real waits for fresh backend data | PASS |
| UI-008-T14 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t14_simulated_vigilance_does_not_leak | simulated vigilance does not leak into Real | PASS |
| UI-008-T15 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t15_simulated_signal_does_not_leak | simulated signal/artifact does not leak into Real | PASS |
| UI-008-T16 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t16_warmup_does_not_show_talker_a | warmup does not present default Talker A as genuine | PASS |
| UI-008-T17 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t17_warmup_clears_correlations_and_gains | warmup clears correlations and gains | PASS |
| UI-008-T18 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t18_warmup_vigilance_unavailable | vigilance stays unavailable during warmup | PASS |
| UI-008-T19 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t19_warmup_signal_unavailable | signal quality stays unavailable during warmup | PASS |
| UI-008-T20 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t20_malformed_empty_eeg_safe | malformed/empty EEG is safe | PASS |
| UI-008-T21 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t21_real_mode_never_creates_synthetic_eeg | Real Mode does not create synthetic EEG | PASS |
| UI-008-T22 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t22_failure_creates_history_gap | backend failure creates a lapse history gap | PASS |
| UI-008-T23 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t23_history_remains_bounded | real history remains limited to 30 bins | PASS |
| UI-008-T24 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t24_no_local_storage | history is not persisted with localStorage | PASS |
| UI-008-T25 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t25_no_randomness | no Math.random is used | PASS |
| UI-008-T26 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t26_state_polling_is_no_store | /state polling remains cache no-store | PASS |
| UI-008-T27 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t27_backend_contract_unchanged | live_demo.STATE remains unchanged | PASS |
| UI-008-T28 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t28_lapse_score_readiness_preserved | UI-007 optional lapse-score behavior remains | PASS |
| UI-008-T29 | Integration hardening | unit | tests/test_ui.py | test_ui_008_t29_previous_features_remain | UI-001 through UI-007 features remain | PASS |
| UI-009-T01 | Final polish | unit | tests/test_ui.py | test_ui_009_t01_attune_title | ATTUNE user-facing title remains present | PASS |
| UI-009-T02 | Final polish | unit | tests/test_ui.py | test_ui_009_t02_subtitle | Neuro-Adaptive Hearing subtitle remains present | PASS |
| UI-009-T03 | Final polish | unit | tests/test_ui.py | test_ui_009_t03_footer_branding | footer branding remains correct | PASS |
| UI-009-T04 | Final polish | unit | tests/test_ui.py | test_ui_009_t04_demo_disclosure | Demo Mode has explicit simulated disclosure | PASS |
| UI-009-T05 | Final polish | unit | tests/test_ui.py | test_ui_009_t05_real_vigilance_unavailable | real unavailable vigilance is clear | PASS |
| UI-009-T06 | Final polish | unit | tests/test_ui.py | test_ui_009_t06_real_signal_unavailable | real signal quality remains unavailable | PASS |
| UI-009-T07 | Final polish | unit | tests/test_ui.py | test_ui_009_t07_no_medical_claim | no medical or diagnostic claim is introduced | PASS |
| UI-009-T08 | Final polish | unit | tests/test_ui.py | test_ui_009_t08_accessible_demo_control | Demo control has accessible label/state attributes | PASS |
| UI-009-T09 | Final polish | unit | tests/test_ui.py | test_ui_009_t09_focus_visible_style | interactive control has focus-visible styling | PASS |
| UI-009-T10 | Final polish | unit | tests/test_ui.py | test_ui_009_t10_status_semantics | status areas remain semantically labeled | PASS |
| UI-009-T11 | Final polish | unit | tests/test_ui.py | test_ui_009_t11_narrow_responsive_rule | narrow responsive CSS rule exists | PASS |
| UI-009-T12 | Final polish | unit | tests/test_ui.py | test_ui_009_t12_history_narrow_layout | history has narrow-screen handling | PASS |
| UI-009-T13 | Final polish | unit | tests/test_ui.py | test_ui_009_t13_responsive_eeg | EEG visualization is constrained and responsive | PASS |
| UI-009-T14 | Final polish | unit | tests/test_ui.py | test_ui_009_t14_no_external_resources | no external CSS/JS resources exist | PASS |
| UI-009-T15 | Final polish | unit | tests/test_ui.py | test_ui_009_t15_no_framework_artifacts | no React/Vite/npm artifacts exist | PASS |
| UI-009-T16 | Final polish | unit | tests/test_ui.py | test_ui_009_t16_no_randomness | no Math.random is used | PASS |
| UI-009-T17 | Final polish | unit | tests/test_ui.py | test_ui_009_t17_no_local_storage | no localStorage is used | PASS |
| UI-009-T18 | Final polish | unit | tests/test_ui.py | test_ui_009_t18_same_origin_state_endpoint | /state remains same-origin | PASS |
| UI-009-T19 | Final polish | unit | tests/test_ui.py | test_ui_009_t19_no_store_polling | cache no-store polling remains | PASS |
| UI-009-T20 | Final polish | unit | tests/test_ui.py | test_ui_009_t20_stale_protection_preserved | UI-008 stale protection remains | PASS |
| UI-009-T21 | Final polish | unit | tests/test_ui.py | test_ui_009_t21_mode_isolation_preserved | UI-008 Real/Demo isolation remains | PASS |
| UI-009-T22 | Handoff | unit | tests/test_ui.py | test_ui_009_t22_handoff_files_are_approved | ATTUNE_UI contains only approved files | PASS |
| UI-009-T23 | Handoff | unit | tests/test_ui.py | test_ui_009_t23_handoff_ui_matches_production | handoff ui.html matches production byte-for-byte | PASS |
| UI-009-T24 | Handoff | unit | tests/test_ui.py | test_ui_009_t24_readme_has_no_absolute_path | README has no machine-specific absolute path | PASS |
| UI-009-T25 | Handoff | unit | tests/test_ui.py | test_ui_009_t25_integration_documents_lapse_score | handoff contract documents optional lapse_score | PASS |
| UI-009-T26 | Handoff | unit | tests/test_ui.py | test_ui_009_t26_integration_documents_unavailable_quality | handoff contract documents unavailable quality/artifact | PASS |
| UI-009-T27 | Handoff | unit | tests/test_ui.py | test_ui_009_t27_handoff_has_no_secret_files | handoff has no suspicious secret/config files | PASS |
| UI-009-T28 | Final polish | unit | tests/test_ui.py | test_ui_009_t28_previous_features_remain | UI-001 through UI-008 behavior remains | PASS |
| UI-010-T01 | transport | integration | TBD | valid WebSocket message | UI receives payload | PLANNED |
| UI-010-T02 | transport | integration | TBD | malformed WebSocket message | app remains stable | PLANNED |
| UI-010-T03 | transport | integration | TBD | disconnect | disconnected state shown | PLANNED |
| UI-011-T01 | mock integration | integration | TBD | backend to UI | prediction visible | PLANNED |
| UI-012-T01 | real adapter | integration | TBD | real output mapping | conforms to UI contract | PLANNED |
| UI-013-T01 | demo | smoke | manual | full startup | system starts successfully | PLANNED |
| UI-013-T02 | demo fallback | smoke | manual | EEG unavailable | demo mode usable | PLANNED |

| BACKEND-001-T01 | Transport foundation | unit/integration | backend/tests/test_foundation.py | ProtocolTests.test_packet_creation_and_unknown_payload | packet creation and unknown payload | PASS |
| BACKEND-001-T02 | Transport foundation | unit/integration | backend/tests/test_foundation.py | ProtocolTests.test_malformed_envelopes | malformed envelopes | PASS |
| BACKEND-001-T03 | Transport foundation | unit/integration | backend/tests/test_foundation.py | ProtocolTests.test_payload_limits_and_nonfinite | payload limits and nonfinite | PASS |
| BACKEND-001-T04 | Transport foundation | unit/integration | backend/tests/test_foundation.py | ProtocolTests.test_deep_payload_and_oversized_timestamp_rejected | deep payload and oversized timestamp rejected | PASS |
| BACKEND-001-T05 | Transport foundation | unit/integration | backend/tests/test_foundation.py | PublisherTests.test_events_preserved_and_snapshot_latest | events preserved and snapshot latest | PASS |
| BACKEND-001-T06 | Transport foundation | unit/integration | backend/tests/test_foundation.py | PublisherTests.test_bounds_and_lag_detection | bounds and lag detection | PASS |
| BACKEND-001-T07 | Transport foundation | unit/integration | backend/tests/test_foundation.py | PublisherTests.test_sessions_timestamp_validation_and_rejection_atomicity | sessions timestamp validation and rejection atomicity | PASS |
| BACKEND-001-T08 | Transport foundation | unit/integration | backend/tests/test_foundation.py | PublisherTests.test_concurrent_publication_sequences | concurrent publication sequences | PASS |
| BACKEND-001-T09 | Transport foundation | unit/integration | backend/tests/test_foundation.py | WorkerTests.test_mock_deterministic_and_multiple_types | mock deterministic and multiple types | PASS |
| BACKEND-001-T10 | Transport foundation | unit/integration | backend/tests/test_foundation.py | WorkerTests.test_idempotent_commands_restart_and_close | idempotent commands restart and close | PASS |
| BACKEND-001-T11 | Transport foundation | unit/integration | backend/tests/test_foundation.py | WorkerTests.test_worker_failure_is_reported | worker failure is reported | PASS |
| BACKEND-001-T12 | Transport foundation | unit/integration | backend/tests/test_foundation.py | WorkerTests.test_stop_deadline_is_explicit | stop deadline is explicit | PASS |
| BACKEND-001-T13 | Transport foundation | unit/integration | backend/tests/test_foundation.py | WorkerTests.test_concurrent_start_is_single_worker | concurrent start is single worker | PASS |
| BACKEND-001-T14 | Transport foundation | unit/integration | backend/tests/test_foundation.py | TransportTests.test_rest_health_state_commands_and_shutdown | rest health state commands and shutdown | PASS |
| BACKEND-001-T15 | Transport foundation | unit/integration | backend/tests/test_foundation.py | TransportTests.test_websocket_mock_snapshot_events_and_reconnect | websocket mock snapshot events and reconnect | PASS |
| BACKEND-001-T16 | Transport foundation | unit/integration | backend/tests/test_foundation.py | TransportTests.test_unknown_partial_payload_delivered_unchanged | unknown partial payload delivered unchanged | PASS |
| BACKEND-001-T17 | Transport foundation | unit/integration | backend/tests/test_foundation.py | TransportTests.test_factory_failure_is_clean_http_error | factory failure is clean http error | PASS |
| BACKEND-001-T18 | Transport foundation | unit/integration | backend/tests/test_foundation.py | TransportTests.test_lagged_websocket_explicitly_requests_reconnect | lagged websocket explicitly requests reconnect | PASS |
| BACKEND-001-T19 | Transport foundation | unit/integration | backend/tests/test_foundation.py | TransportTests.test_idle_socket_disconnect_does_not_leave_subscriber | idle socket disconnect does not leave subscriber | PASS |

| F02-T01 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | attention decoder preserves decisions and correlations | attention decoder preserves decisions and correlations | PASS |
| F02-T02 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | vigilance decoder preserves valid zero and rejects unavailable scores | vigilance decoder preserves valid zero and rejects unavailable scores | PASS |
| F02-T03 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | sync decoder preserves false zero and unknown values | sync decoder preserves false zero and unknown values | PASS |
| F02-T04 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | EEG decoder passes display samples without computation | EEG decoder passes display samples without computation | PASS |
| F02-T05 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | unknown types and registry extensions preserve opaque payloads | unknown types and registry extensions preserve opaque payloads | PASS |
| F02-T06 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | missing optional fields remain unavailable in all decoders | missing optional fields remain unavailable in all decoders | PASS |
| F02-T07 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | malformed envelopes and nonfinite JSON are rejected | malformed envelopes and nonfinite JSON are rejected | PASS |
| F02-T08 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | packet size depth and identifier bounds are enforced | packet size depth and identifier bounds are enforced | PASS |
| F02-T09 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | duplicate and out-of-order sequences cannot replace state | duplicate and out-of-order sequences cannot replace state | PASS |
| F02-T10 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | timestamps are ordered per stream and failures are atomic | timestamps are ordered per stream and failures are atomic | PASS |
| F02-T11 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | new sessions clear old streams and snapshots permit process reset | new sessions clear old streams and snapshots permit process reset | PASS |
| F02-T12 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | malformed inconsistent snapshots are rejected | malformed inconsistent snapshots are rejected | PASS |
| F02-T13 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | latest state bounds source streams | latest state bounds source streams | PASS |
| F02-T14 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | REST methods paths and HTTP failures | REST methods paths and HTTP failures | PASS |
| F02-T15 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | reconnect resnapshots and ignores previous socket callbacks | reconnect resnapshots and ignores previous socket callbacks | PASS |
| F02-T16 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | failed REST retries with bounded backoff and stop cancels | failed REST retries with bounded backoff and stop cancels | PASS |
| F02-T17 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | delayed snapshots and timeouts cannot revive stopped clients | delayed snapshots and timeouts cannot revive stopped clients | PASS |
| F02-T18 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | socket errors malformed frames and secure URLs | socket errors malformed frames and secure URLs | PASS |
| F02-T19 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | Python mock packets decode across language boundary | Python mock packets decode across language boundary | PASS |
| F02-T20 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | debug dashboard renders status unavailable values and escaped payloads | debug dashboard renders status unavailable values and escaped payloads | PASS |
| F02-T21 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | restart between REST snapshot and socket forces a fresh snapshot | restart between REST snapshot and socket forces a fresh snapshot | PASS |
| F02-T22 | Phase 2 transport client | unit/contract | frontend/tests/client.test.js | replay duplicates do not replace newer snapshot measurements | replay duplicates do not replace newer snapshot measurements | PASS |
| F02-T23 | Phase 2 transport client | integration/live | frontend/tests/live.integration.js | live Python to Vite proxy to frontend decoders and reconnect | live Python to Vite proxy to frontend decoders and reconnect | FAIL |

| A03-B01 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_four_attention_states | four attention states | PASS |
| A03-B02 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_aad_mapping_does_not_recompute_decision | aad mapping does not recompute decision | PASS |
| A03-B03 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_combined_object_and_dictionary_explicit_timestamp | combined object and dictionary explicit timestamp | PASS |
| A03-B04 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_lapse_and_vigilance_semantics_and_unavailable | lapse and vigilance semantics and unavailable | PASS |
| A03-B05 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_sync_has_no_fabricated_measurement | sync has no fabricated measurement | PASS |
| A03-B06 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_invalid_results_do_not_reach_publisher | invalid results do not reach publisher | PASS |
| A03-B07 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_display_samples_are_detached_and_not_processed | display samples are detached and not processed | PASS |
| A03-B08 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_publisher_assigns_sequence_and_session | publisher assigns sequence and session | PASS |
| A03-B09 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_result_producer_cancellation_and_error_propagation | result producer cancellation and error propagation | PASS |
| A03-B10 | Phase 3 adapters | unit/ASGI | backend/tests/test_adapters.py | test_independent_producer_to_rest_websocket_lifecycle | independent producer to rest websocket lifecycle | PASS |
| A03-F01 | Phase 3 adapters | unit/contract | frontend/tests/adapters.test.js | explicit attention states survive decoding | explicit attention states survive decoding | PASS |
| A03-F02 | Phase 3 adapters | unit/contract | frontend/tests/adapters.test.js | lapse probability is not displayed as vigilance | lapse probability is not displayed as vigilance | PASS |
| A03-F03 | Phase 3 adapters | unit/contract | frontend/tests/adapters.test.js | real Python adapters flow through unchanged frontend transport state | real Python adapters flow through unchanged frontend transport state | PASS |

| DOC-AUDIT-001-T01 | Retrospective documents | static/audit | docs/development/ | inline audit: sections, paths, fences | All four documents contain required sections, balanced fences and existing cited file paths | PASS |
| DOC-AUDIT-001-T02 | Retrospective provenance | static/audit | docs/development/CURRENT_STATE.md | inline audit: HEAD comparison | Handoff records current HEAD and explicitly notes untracked phase implementation | PASS |
| DOC-AUDIT-001-T03 | Documentation privacy | static/audit | docs/development/ | inline audit: secret patterns | No private-key/service-token pattern in new documents | PASS |

| REPO-001-T01 | Repository preparation | static/provenance | sibling NOVA2026/docs/development/LOCAL_APP_PROVENANCE.json | SHA-256 preservation check | All 37 original app/docs files unchanged; 36 prepared copies byte-identical, primary CURRENT_STATE intentionally revised | PASS |
| REPO-001-T02 | Repository preparation | static/git | original and sibling Git repositories | unstaged and scientific-diff check | All indexes empty; only upstream tracked .gitignore changed | PASS |
| REPO-001-T03 | Local artifact protection | static/git | .gitignore and sibling NOVA2026/.gitignore | git check-ignore | Environments, frontend dependencies/builds and secrets excluded, including symlink | PASS |
| REPO-001-T04 | Repository handoff | static/docs | sibling NOVA2026/docs/development/CURRENT_STATE.md | required section check | Requested repository sources/base/branches/pipeline/application sections present | PASS |

| FB-B01 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_middle_and_upper_mock_trigger | middle and upper mock trigger | PASS |
| FB-B02 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_low_mock_none | low mock none | PASS |
| FB-B03 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_invalid_unavailable_error_never_active | invalid unavailable error never active | PASS |
| FB-B04 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_nonmock_and_missing_numeric_never_active | nonmock and missing numeric never active | PASS |
| FB-B05 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_five_second_cooldown | five second cooldown | PASS |
| FB-B06 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_low_and_invalid_do_not_reset_cooldown | low and invalid do not reset cooldown | PASS |
| FB-B07 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_stale_time_suppressed_and_emission_time_does_not_regress | stale time suppressed and emission time does not regress | PASS |
| FB-B08 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_action_contract_validation_and_defensive_copy | action contract validation and defensive copy | PASS |
| FB-B09 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_prediction_to_feedback_websocket_and_session_reset | prediction to feedback websocket and session reset | PASS |
| FB-B10 | Development feedback | unit/ASGI | backend/tests/test_feedback.py | test_malformed_prediction_emits_suppression_without_worker_failure | malformed prediction emits suppression without worker failure | PASS |
| FB-F01 | Development feedback | render/unit | frontend/tests/feedback.test.js | active feedback is obvious and development labeled | active feedback is obvious and development labeled | PASS |
| FB-F02 | Development feedback | render/unit | frontend/tests/feedback.test.js | none and empty feedback render safely | none and empty feedback render safely | PASS |
| FB-F03 | Development feedback | render/unit | frontend/tests/feedback.test.js | cooldown suppression is visible | cooldown suppression is visible | PASS |
| FB-F04 | Development feedback | render/unit | frontend/tests/feedback.test.js | stale or stopped sessions cannot highlight cached active feedback | stale or stopped sessions cannot highlight cached active feedback | PASS |
| FB-F05 | Development feedback | render/unit | frontend/tests/feedback.test.js | undeclared feedback cannot appear active | undeclared feedback cannot appear active | PASS |

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


### 2026-09-11 — UI-004

**Contributor:** Development workflow

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

**Results:** UI suite PASS, 42 tests, no skips (30 preserved + 12 new).
Discovery: 44 entries, 42 passed, 2 existing import errors:
`ModuleNotFoundError: No module named 'numpy'` in test_combined and
 test_driving_pilot. No dependencies installed or existing tests altered/skipped.

**Coverage:** UI-004-T01–T12 cover markup, unavailable real mode, deterministic
quality/artifacts, bounds/smoothness, exact label and artifact interval boundaries,
no randomness, unchanged backend contract, existing features, immediate demo exit
cleanup, late-response isolation, offline real mode and recovery. Runtime checks
reuse the existing Node VM harness with mocked browser/network facilities.
Node was already available and all checks executed; runtime tests skip if absent
on another machine. No browser visual review performed.

**Display assumptions:** Quality = .6 + .35*cos(2*pi*(t % 20)/20), range .25–.95.
Good >= .75; Fair >= .45 and < .75; Poor < .45. Separate time condition marks
artifact when 8 <= (t % 20) < 12, where quality is below .45. Simulation only;
no EEG assessment or artifact rejection. Real mode remains unavailable.

**Registry note:** UI-004-T01/T02 generic planned attention-card placeholders now
follow this explicit signal-quality task mapping; historical runs retained.


### 2026-09-11 — UI-005

**Contributor:** Development workflow

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

**Results:** UI PASS, 56 tests with no skips (42 preserved + 14 new).
Discovery: 58 entries, 56 passed, 2 existing import errors:
`ModuleNotFoundError: No module named 'numpy'` for test_combined/test_driving_pilot.
No installs or changes to those tests.

**Coverage:** UI-005-T01–T14 verify markup/labels, deterministic helper reuse,
30-sample bound, duplicate prevention/expiry, no randomness/persistence,
unavailable real metrics, unchanged contract, preserved UI, exit clearing,
stale-response isolation, real recovery and no external chart resources.
Runtime checks use existing Node and mocked browser facilities; all ran here.
They skip if Node is absent on another machine. No browser visual review performed.

**Design:** Native HTML/CSS rows, A/B text per attention bin, lapse/quality bars,
striped artifact bins, text legend and accessible per-sample descriptions.
One-second resolution, maximum 30 samples/row, updated at most once per second.
Demo reconstructs integer-second history from elapsed time, starting at zero;
real history uses browser receipt-time seconds and only observed running attention.
Missing observations remain gaps. No real lapse/quality/artifact values generated.

**Registry note:** UI-005-T01/T02 generic planned signal/artifact placeholders now
follow the user's explicit history-task mapping. Historical entries retained.


### 2026-09-11 — UI-006

**Contributor:** Development workflow

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

**Results:** UI PASS: 71 tests, no skips (56 existing + 15 new).
Discovery: 73 entries, 71 passed, 2 existing import errors: missing numpy in
 test_combined/test_driving_pilot. No packages installed or those tests altered.

**Coverage:** UI-006-T01–T15 cover mapping, malformed/null/non-object inputs,
strict attended values, invalid/ragged/nonfinite EEG, nonfinite numbers, real
adapter execution, normalized rendering/history, absence of future metrics,
backend compatibility, demo determinism, no randomness and existing features.
Runtime checks use the existing installed Node VM harness with fake browser and
network. All ran here; runtime tests skip on machines without Node.

**Existing assertions updated:** UI-003-T08 and UI-004-T10 now assert demo-only
helper calls use `state.elapsedSeconds` instead of raw `s.t`. All test methods
and behavioral assertions retained; raw field coverage now exercises the adapter.

**Defaults:** strict booleans; invalid numbers/talker/elapsed/accuracy => null;
invalid strings => empty string; invalid EEG => empty array. Elapsed must be
nonnegative and accuracy within 0..1. Valid EEG is copied, finite, rectangular,
with at least two samples/channel. No numerical coercion or invented metrics.
UI-006-T01/T02 replace generic planned history placeholders per this task's mapping.


### 2026-09-12 — BACKEND-001 (Phase 1)

**Contributor:** Development workflow

**Commands:**
```bash
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ui -q
```

**Backend result:** PASS, 19 tests. Initial 16-test run exposed two WebSocket
client-disconnect cancellation errors; fixed server task cleanup, then added
nesting/oversized-timestamp, buffer-overrun and idle-disconnect tests. Final run
passed all 19. ASGI TestClient exercises REST/WebSocket without a physical server,
hardware, datasets or external network. Worker tests include concurrency,
cancellation deadline, terminal error and graceful app shutdown.

**Existing UI result:** PASS, 147 tests. No legacy UI/backend/scientific files
changed. Full scientific suite not rerun: this scope does not alter algorithms,
and the previously documented system-Python dependency limitation remains.

**Environment:** Used the temporary isolated virtual environment installed during
the preceding authorized integration attempt. No installation in this phase.
Reproduction/runtime commands are in backend/README.md; dependency manifests are
local to backend/. No protocol tests depend on the scientific Python packages.


### FRONTEND-002 — Phase 2 verification (2026-09-12)

- `npm test --prefix frontend`: PASS, 22 tests, no skips.
- `npm run build --prefix frontend`: PASS, Vite production build (29 modules).
- `ATTUNE_PYTHON=/private/tmp/attune-backbone-venv/bin/python npm run test:live --prefix frontend`: PASS, 1 live integration test, no skips.
- `PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v`: PASS, 19 backend tests.
- Initial frontend test invocation preceded dependency installation and failed to import React. Sandboxed installation failed DNS; approved official npm registry install succeeded.
- Initial live invocation was blocked by sandbox loopback permissions. Approved runs exposed test-harness path escaping and Uvicorn SIGTERM-exit assumptions, both corrected; final run passes without weakening transport assertions. Graceful shutdown completion remains explicitly asserted.


### ADAPTER-003 — Phase 3 verification (2026-09-12)

- `PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v`: PASS, 29 tests (10 new adapter tests, 19 existing).
- `npm test --prefix frontend`: PASS, 25 tests (3 new adapter decoder/real-Python fixture tests, 22 existing).
- `npm run build --prefix frontend`: PASS, 29 modules.
- No scientific modules imported, models loaded, sources opened or dependencies installed. ASGI REST/WS and Python-to-JavaScript fixture paths exercised; physical source and real-model execution intentionally deferred.


### DOC-AUDIT-001 — Current repository retrospective (2026-09-12)

Current HEAD: a3ee2ba21115cda4eb3d1cac469c2239892e03c4. Backend/frontend are
untracked; ledger phase attribution is not independently proven by Git.

Commands/results from this audit (not copied from prior passes):

```bash
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
npm test --prefix frontend
npm run build --prefix frontend
ATTUNE_PYTHON=/private/tmp/attune-backbone-venv/bin/python npm run test:live --prefix frontend
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
curl --max-time 5 -fsS http://127.0.0.1:5173/api/health
curl --max-time 5 -fsS -o /dev/null -w 'frontend HTTP %{http_code}\n' http://127.0.0.1:5173/
```

- Backend PASS: 29 tests. Frontend PASS: 25 tests. Build PASS: 29 modules.
- Live F02-T23 FAIL: Vite selected occupied port 5173 despite requesting port 0.
  Existing user frontend preserved; no code/test rewrite. Latest registry status
  updated to FAIL while historical run entries remain unchanged.
- Root discovery FAIL: 149 reported, 147 legacy UI PASS, two import errors for
  test_combined/test_driving_pilot because system Python lacks numpy. Scientific
  test bodies did not execute; this is not an algorithm correctness failure.
- Safe existing-server smoke PASS: frontend HTTP 200 and proxy health ok/version 1.
- Inline documentation checks PASS: required sections, balanced fences, existing
  cited repository paths, HEAD hash equality, no secret-pattern matches.
- No physical hardware, models, downloads or package installation required.


### REPO-001 — Upstream reconciliation (2026-09-12)

New primary: sibling NOVA2026, branch integration/application-layer, base a506ce2.
Original NOVA and its 37 application/documentation files preserved unchanged.
Checks were run from `/Users/yutong/Documents/New project/NOVA2026`:

```bash
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
npm test --prefix frontend
npm run build --prefix frontend
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python3 -m unittest discover -s tests/streaming -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python3 -m scripts.dataproc.riemann.checks
```

- Backend PASS 29; frontend PASS 25; build PASS 29 modules.
- Streaming: 15 loader errors (missing scientific dependencies including mne/numpy); no test bodies executed.
- Riemann: import failure, missing numpy. No environment installation or model run.
- Preservation/index/research-diff/ignore/document checks PASS. Initial ignore
  verification caught directory-only pattern not covering node_modules symlink;
  primary .gitignore corrected and verification passed. No test assertions weakened.
- Prior live test not rerun; its earlier port-isolation failure remains documented.


### FEEDBACK-001 — Development-only feedback verification

From original NOVA workspace only:
```bash
PYTHONDONTWRITEBYTECODE=1 /private/tmp/attune-backbone-venv/bin/python -m unittest discover -s backend/tests -v
npm test --prefix frontend
npm run build --prefix frontend
```
PASS: backend 45 tests (10 new); frontend 31 tests (5 new); build 30 modules.
No scientific/model/actuator execution. ASGI packet delivery and static React
rendering verified. Cooldown uses deterministic session event time, not wall-clock
actuation time; no frontend thresholds. Sibling repositories untouched.
