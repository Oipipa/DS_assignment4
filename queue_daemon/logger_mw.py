import logging, time, json
from starlette.middleware.base import BaseHTTPMiddleware
class RequestLogger(BaseHTTPMiddleware):
    def __init__(self, app, logfile):
        super().__init__(app)
        self.log = logging.getLogger("rq")
        h = logging.FileHandler(logfile)
        self.log.addHandler(h)
        self.log.setLevel(logging.INFO)
    async def dispatch(self, request, call_next):
        start = time.time()
        body = await request.body()
        resp = await call_next(request)
        duration = time.time() - start
        entry = {
            "src": str(request.client.host),
            "dst": str(request.url),
            "method": request.method,
            "status": resp.status_code,
            "headers": dict(request.headers),
            "body": body.decode(errors="ignore"),
            "resp_headers": dict(resp.headers),
            "duration": duration,
        }
        self.log.info(json.dumps(entry))
        return resp
