# ATTUNE transport foundation — Phase 1

This is a local, mock-only Python transport application. It does not replace
`neuro-attention/src/live_demo.py`, change `/state`, or import NOVA/novaAAD models.
There is no React application in this phase.

## Run from the repository root

Use an isolated Python environment (tested with Python 3.9; the scientific package
has its own Python >=3.12 requirement and is not part of this environment).

```sh
python3 -m venv /tmp/attune-transport-env
/tmp/attune-transport-env/bin/python -m pip install -r backend/requirements-test.txt
PYTHONDONTWRITEBYTECODE=1 /tmp/attune-transport-env/bin/python -m unittest discover -s backend/tests -v
/tmp/attune-transport-env/bin/python -m uvicorn backend.app.server:app --host 127.0.0.1 --port 8001
```

Port 8001 is an explicit example to avoid the legacy demo's default 8000.
Run **one server worker**: state is process-local. The app does not start a producer
until commanded. Runtime and test requirements are scoped to this application.

```sh
curl http://127.0.0.1:8001/api/health
curl -X POST http://127.0.0.1:8001/api/session/start
curl http://127.0.0.1:8001/api/state
curl -X POST http://127.0.0.1:8001/api/session/stop
```

Connect a WebSocket client to `ws://127.0.0.1:8001/ws/live`. Incoming client text
or binary messages are ignored; commands belong to REST.

## Module boundaries

- `app/protocol.py`: packet construction, envelope/JSON validation and size limit.
- `app/publisher.py`: thread-safe event publication and latest-state snapshots.
- `app/sessions.py`: serialized commands, background producer lifecycle and errors.
- `app/server.py`: FastAPI endpoints, lifespan and WebSocket delivery only.
- `adapters/base.py`: producer interface; `adapters/mock.py`: deterministic results.
- `sources/base.py`: EEG/audio source protocols only; no physical implementations.
- `tests/test_foundation.py`: protocol, publisher, concurrency, REST, WebSocket and lifecycle tests.

## Packet contract, version 1

```json
{
  "version": 1,
  "type": "attention",
  "timestamp": 0.0,
  "sequence": 2,
  "source": "mock-aad",
  "session_id": "opaque-session-id",
  "payload": {
    "attended": "A",
    "correlation_a": 0.42,
    "correlation_b": 0.19,
    "simulated": true
  }
}
```

`type`, `source` and `session_id` are nonempty strings, max 128 characters.
`sequence` is a JavaScript-safe nonnegative integer, assigned by the publisher;
accepted publication increments it once. It increases across sessions within one
server process and resets when the process restarts. Session UUIDs distinguish
sessions across restarts. Do not compare timestamps across sessions.

`timestamp` is nonnegative session-relative seconds, not wall-clock time. A
producer supplies the result's timestamp; the server does not infer physical
alignment. Nondecreasing timestamps are enforced per currently retained
`(source, type)` stream, not across independent sources. Transport order is the
publisher sequence, not timestamp order.

`payload` is a JSON object. Unknown types and extra envelope/payload fields are
preserved. Null/partial payload values are allowed. Payload semantics are not
validated by the transport. NaN/Infinity, non-JSON objects, non-string keys,
nesting deeper than 32 and packets over 256 KiB are rejected. Producer objects
are detached on publication; snapshots and returned events are defensive copies.

## Delivery and memory bounds

`GET /api/state` returns `{sequence, session_id, packets}`. Packets are the latest
value for each retained `(source, type)`, ordered by sequence. Maximum 128 streams;
least recently updated streams are evicted. Starting a session clears latest state.

WebSocket connections first receive those individual latest packets, then all
new events after the snapshot's atomic high-water cursor. The event ring retains
256 packets across session boundaries; each connected socket has its own cursor.
There is no unbounded per-client queue. Slow clients that overrun the ring receive
close code **1013** and must reconnect for a fresh latest snapshot. A send timeout
also closes with 1013. Quiet disconnects cancel both socket tasks. This is bounded
live delivery, **not durable event storage or historical replay**. Reconnection
may repeat snapshot packets; future consumers must deduplicate by session/sequence.

Worst-case payload memory is bounded by packet size and buffer/stream limits,
with temporary defensive-copy overhead. Producers never wait for clients. They
briefly share the publisher lock while validating/copying a bounded packet.

## Commands and lifecycle

- `GET /api/health`: transport health/version, independent of model availability.
- `GET /api/state`: current snapshot; empty before first start.
- `POST /api/session/start`: start mock producer, or return current session if active.
- `POST /api/session/stop`: request stop and join worker; idempotent, null before start.
- `GET /api/sessions`, `GET /api/sessions/{id}`: in-memory summaries only, max 32.
- `WS /ws/live`: output stream.

Start/stop commands are serialized. Producer computation runs in a background
thread; FastAPI synchronous handlers execute outside its async event loop.
Producer construction must be lightweight; expensive initialization belongs in
`run()`. `run(publish, stop_event)` must check cancellation and use bounded I/O.
The factory is injectable with `create_app(producer_factory=...)`.

The server publishes session start and terminal stopped/error events. Source
`server` is reserved. Failure payloads use `producer_failed`, not raw exception
messages. Once a producer returns, its session cannot publish more results.
Shutdown closes sockets and signals/joins the worker. A worker that ignores
cancellation is reported after a three-second deadline; Python cannot forcibly
stop such a thread. Process-isolated execution is deferred. The mock cooperates
and terminates promptly, including while waiting between samples.

## Mock data

Every index yields the same values at timestamp `index * 0.25`. Packets include
attention, vigilance, sync, eeg_display, gain and unavailable signal_quality.
Attention alternates A/B every four seconds with matching correlations/gains.
Vigilance is an explicitly simulated cosine illustration. EEG display contains
one synthetic channel with 32 samples and display rate metadata, not raw EEG.
All mock payloads say `simulated: true`; session metadata also identifies mock data.
Session UUIDs and actual lifecycle timestamps are operational metadata, not fixed
mock measurements.

Sync declares the session timeline, unknown status, null offset/fixed latency and
no drift warning. It does not perform calibration or claim synchronization.

## Deferred

No hardware, real models, signal processing, physical clock calibration, raw EEG
streaming, React client, decoder registry, database, authentication, CORS policy,
cloud deployment or multi-process shared state. Bind to loopback for this phase.
Future integrations should implement producers/adapters around existing algorithms,
not move scientific code into HTTP handlers. Readiness/liveness heartbeat and
persisted event replay can be added under a separate protocol revision if needed.
