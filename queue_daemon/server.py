import asyncio, time
from fastapi import FastAPI, Header, HTTPException, status, Body, Query
from queue_daemon.logger_mw import RequestLogger

def create_app(storage, auth):
    app = FastAPI()
    app.add_middleware(RequestLogger, logfile="access.log")

    def token(h: str | None = Header(None, alias="X-Auth-Token")):
        if h is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return h

    @app.post("/queues")
    async def create(name: str = Body(..., embed=True), t=token()):
        auth.require_admin(t)
        if not storage.create_queue(name):
            raise HTTPException(400, "exists")

    @app.delete("/queues/{name}")
    async def delete(name: str, t=token()):
        auth.require_admin(t)
        if not storage.delete_queue(name):
            raise HTTPException(404, "not found")

    @app.get("/queues")
    async def listing(t=token()):
        auth.require_admin(t)
        return storage.list_queues()

    @app.post("/queues/{name}/push")
    async def push(name: str, msg: dict = Body(...), t=token()):
        auth.require_agent_or_admin(t)
        if not storage.push(name, msg):
            raise HTTPException(400, "queue full or missing")

    @app.post("/queues/{name}/pull")
    async def pull(name: str, timeout_ms: int = Query(0, ge=0), t=token()):
        auth.require_agent_or_admin(t)
        deadline = time.monotonic() + timeout_ms / 1000
        while True:
            res = storage.pull(name)
            if res is not None:
                return res
            if timeout_ms == 0 or time.monotonic() >= deadline:
                raise HTTPException(404, "empty or missing")
            await asyncio.sleep(0.05)

    return app
