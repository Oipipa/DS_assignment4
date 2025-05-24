import uvicorn
import sys
from .config import load_config
from .storage import QueueStorage
from .auth import Auth
from .server import create_app

def main():
    cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
    storage = QueueStorage(cfg["service"])
    auth = Auth(cfg["security"])
    for q in cfg["service"].get("default_queues", []):
        storage.create_queue(q)
    app = create_app(storage, auth)
    uvicorn.run(app, host="0.0.0.0", port=7500)
