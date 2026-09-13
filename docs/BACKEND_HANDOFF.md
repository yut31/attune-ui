# ATTUNE backend handoff

```text
Audio A --------\
                 \
Audio B ----------> research EEG/audio decoder
                  /
EEG --------------/
                         |
                 thin ATTUNE adapter
                         |
                    publish(...)
                         |
              ATTUNE backend publisher
                         |
                  REST / WebSocket
                         |
                      React UI
```

The existing `run(publish, stop)` producer callback is the integration boundary.
Inject a lightweight producer with `create_app(producer_factory=...)`. Expensive
EEG/audio/model initialization and processing belong in its background worker,
never FastAPI request handlers. Honor cancellation, bound source reads, and clean
up owned inputs in `finally`. Existing session lifecycle, provider prediction,
feedback, publisher, REST and WebSocket infrastructure remain in place.

```python
publish(
    "attention", timestamp, "nova-aad",
    {"decision": "A", "attended": "A", "correlation_a": 0.42,
     "correlation_b": 0.19, "simulated": False},
)
```

Do not create `sequence` or `session_id`: ATTUNE's session callback and publisher
own those and the version-1 envelope. Supply finite, nonnegative, preferably
session-relative seconds, nondecreasing within each source/type. Convert research
clocks explicitly; matching timestamps do not establish physical synchronization.
The existing typed `ResultAdapter` / `ResultProducer` and legacy result helpers
remain available; see [adapter documentation](../backend/adapters/README.md).

## Additive result contract

- `attention`: decision is `A`, `B`, `uncertain`, or `unavailable`; attended is A/B
  for a selected source, otherwise null. Correlations are finite numbers or null,
  never confidence or probability. The UI never infers decisions from them.
- `audio_sources`: exactly two source objects with distinct IDs A and B. Each has
  `label`, `input_type`, and optional `reference` (null when absent). Example:

```json
{"sources": [
  {"id": "A", "label": "Recorded Interview", "input_type": "recording", "reference": "clip-a.wav"},
  {"id": "B", "label": "YouTube Speech", "input_type": "youtube", "reference": "video-example"}
], "simulated": true}
```

Use `backend.adapters.audio_sources.validate_sources` before publication. Only
these four fields are retained. References are public opaque identifiers, not
URLs, local absolute paths, credentials, tokens, cookies or signed links. Labels
and input types must also be non-sensitive display text. Validation cannot detect
arbitrary secrets hidden in otherwise ordinary text; the producer owns that review.
The UI displays metadata as escaped text, never fetches or plays it. Recording,
stream/YouTube reference, microphone, headset/channel and future adapters belong
to the research layer; metadata does not implement acquisition or separation.

- `vigilance`: existing score, or explicit `metric=lapse_probability` and
  `lapse_score`; preserve the upstream meaning. Missing values are null.
- `sync`: status, offset_ms, drift_warning, timeline, fixed_latency_ms. Unmeasured
  physical offset/latency remain null; no synchronization claim is inferred.
- `signal_quality`: quality and artifact; null until supplied by a reviewed
  upstream algorithm. The artificial producer intentionally leaves both null.
- `gain`: a_db and b_db, finite numbers or null; shared-media ATTUNE mode applies supplied gains to browser playback.
- `eeg_display`: sample_rate, channels, bounded two-dimensional samples prepared
  upstream specifically for display. Never publish full raw acquisition streams
  at model frequency. The mock emits 32 illustrative samples per update.
- Existing generic `prediction`, `feedback`, session packets and unknown packet
  fallback remain supported. Generic development prediction is independent of
  the A/B illustration; existing provider output/feedback semantics are preserved.

Every artificial payload declares `simulated: true`; real producers declare false
consistently with their session's `simulated` property. The mock uses index × 0.25
session seconds, A during [0,4), B during [4,8), repeating. To customize its metadata,
use `MockProducer(sources=[...])` via the existing producer factory injection.
Real integration replaces that injected producer, not the transport or React logic.

## Teammate checklist

1. Function/class producing prediction.
2. Exact return object.
3. Meaning and unit of every field.
4. A/B encoding.
5. EEG clock/timestamp source.
6. Audio clock/timestamp source.
7. Prediction/window frequency.
8. Uncertainty/failure representation.
9. Available audio A/B metadata.
10. Whether display EEG can be emitted separately.

No physical acquisition, calibrated synchronization, scientific quality algorithm
or hearing-device actuator is supplied by this handoff. Browser playback is described below. Known disconnects/stale state and terminal
sessions clear focus; silent-stream measurement expiry remains a future explicit
policy, rather than an invented scientific timeout.

## Shared media extension (MEDIA-001)

One runtime-configured file is served at `/api/media/file`; Python uses the same
`MediaTimeline.path`. Only an opaque `media_id`, configured title, media kind and
relative URL leave the server. Configure `ATTUNE_MEDIA_FILE` and optional
`ATTUNE_MEDIA_TITLE`; place recordings in ignored `demo-media/`. No upload or
arbitrary-path HTTP endpoint exists. Two internal stereo outputs map to A/B.

`GET /api/media` supplies public configuration. After existing session start,
`POST /api/media/control` accepts session_id, media_id, client_id (a browser instance
identifier, not authentication), request_id (increasing integer), action, media_time_s,
and duration_s. Actions: prepare, playing, paused, stopped, report. Prepare is a
zero-position paused handshake. Server receipt monotonic seconds establish the
reference anchor; no clock equality is assumed. The browser starts only after the
handshake and reports its actual position/state. Report every 250 ms, including
while paused. Python holds the last observed media position; it does not extrapolate
through silence or pause. Stop resets position and requires a new prepare.

The additive `media` packet reports media_id/title, media_time_s/duration_s,
playback_state, revision, server_reference_s, sync_status and simulated provenance.
Attention/gain carry media_id, media_revision and media_time_s for correspondence.
Envelope timestamps remain session seconds, including after media resets. Reports
expire after 1.5 seconds; invalid progression or missing reports mark desynchronized
and produce unavailable attention / neutral gain. This is application telemetry,
not measured acoustic/EEG alignment or a scientific synchronization-quality score.
Only the prepared browser controls playback until stopped/session reset; out-of-order
commands and old session IDs are rejected. No manual seeking is supported.


### Real predictor replacement

Create one `MediaTimeline` instance for the configured file and inject it both into
`create_app(media=timeline, producer_factory=...)` and your lightweight producer.
The producer implements the existing `run(publish, stop)` and reads
`timeline.snapshot()` in its worker. `timeline.path` is the local shared reference;
never publish it. Server methods and packet sequence/session ownership stay intact.

Use `media_time_s` to select the reference window, and retain the actual EEG clock
and acquisition timestamps separately. `server_reference_s` is prepare receipt;
`server_received_s` is latest report receipt on Python's monotonic clock. Browser
clock equality is neither assumed nor estimated. For real science, measure/map EEG
and audio clock domains and acoustic/device delay upstream; do not treat a received
browser report as an exact simultaneous EEG sample. Pause/stop/report expiry must
prevent the research coordinator from advancing its reference window.

For each valid aligned result, publish attention and gain with the same reference:

```python
reference = {
    'media_id': media['media_id'],
    'media_revision': media['revision'],
    'media_time_s': media['media_time_s'],
}
publish('attention', session_seconds, 'nova-aad', {
    'decision': decision, 'attended': decision if decision in ('A', 'B') else None,
    'correlation_a': correlation_a, 'correlation_b': correlation_b,
    **reference, 'simulated': False,
})
publish('gain', session_seconds, 'nova-gain', {
    'a_db': a_db, 'b_db': b_db, **reference, 'simulated': False,
})
publish('media', session_seconds, 'media-reference', {**media, 'simulated': False})
```

Here `media` is the captured snapshot for that result, not a newer snapshot taken
after processing completes. Decision can be A/B/uncertain/unavailable. Publish
neutral gains for invalid conditions. The player never infers a decision or gain
from correlations; it requires current session, matching media ID/revision and
position within 0.75 s. Processing windows older than that fail neutral; agree on a
reviewed result-age policy before changing that demo tolerance. Its attenuation
range is −80..0 dB, and transitions use a 0.1-second exponential time constant
(~98% settled by 400 ms). Keep Original Mix at unity. Pause retains observed focus
but audio gains are neutral while no audio is playing.

Publish the additive `media` packet regularly in your real producer, plus optional
quality/vigilance/display results, and declare the producer's `simulated = False`.
The default injected mock performs this publication already. Envelope timestamps
remain session-relative and nondecreasing even when the media is stopped/reset.
The generic development provider and feedback are independent and unchanged.
