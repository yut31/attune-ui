"""Local transport app. Producer factory injection is the integration boundary."""
import asyncio
import anyio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from .publisher import Publisher, LaggedSubscriber
from .sessions import Sessions


def create_app(producer_factory=None, publisher=None):
    publisher = publisher if publisher is not None else Publisher()
    sessions = Sessions(publisher, **({'producer_factory': producer_factory} if producer_factory else {}))
    sockets = set()
    stopping = asyncio.Event()

    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            stopping.set()
            await asyncio.gather(*(socket.close(code=1001) for socket in list(sockets)),
                                 return_exceptions=True)
            await asyncio.to_thread(sessions.close)

    app = FastAPI(lifespan=lifespan)
    app.state.publisher = publisher
    app.state.sessions = sessions
    app.state.sockets = sockets

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'protocol_version': 1}

    @app.get('/api/state')
    def state():
        return publisher.snapshot()

    @app.get('/api/sessions')
    def session_list():
        return sessions.list()

    @app.get('/api/sessions/{session_id}')
    def session_detail(session_id: str):
        for record in sessions.list():
            if record['id'] == session_id:
                return record
        raise HTTPException(404, 'unknown session')

    @app.post('/api/session/start')
    def start():
        try:
            return sessions.start()
        except RuntimeError as exc:
            raise HTTPException(409, str(exc)) from exc
        except Exception as exc:
            raise HTTPException(503, 'producer could not start') from exc

    @app.post('/api/session/stop')
    def stop():
        try:
            return sessions.stop()
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc

    @app.websocket('/ws/live')
    async def live(socket: WebSocket):
        await socket.accept()
        sockets.add(socket)

        async def send_packet(packet):
            await asyncio.wait_for(socket.send_json(packet), timeout=5)

        async def send():
            # Atomic snapshot + high-water cursor avoids a subscribe/snapshot race.
            snapshot = publisher.snapshot()
            cursor = snapshot['sequence']
            for packet in snapshot['packets']:
                await send_packet(packet)
            while not stopping.is_set():
                for packet in publisher.events_after(cursor):
                    await send_packet(packet)
                    cursor = packet['sequence']
                await asyncio.sleep(.02)

        async def receive():
            # Server-to-client stream; client messages are not commands.
            while not stopping.is_set():
                message = await socket.receive()
                if message['type'] == 'websocket.disconnect':
                    return

        tasks = [asyncio.create_task(send()), asyncio.create_task(receive())]
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        except (LaggedSubscriber, asyncio.TimeoutError):
            await socket.close(code=1013, reason='Reconnect for latest snapshot')
        except (WebSocketDisconnect, RuntimeError, asyncio.CancelledError):
            pass
        finally:
            for task in tasks:
                task.cancel()
            with anyio.CancelScope(shield=True):
                await asyncio.gather(*tasks, return_exceptions=True)
            sockets.discard(socket)

    return app


app = create_app()
