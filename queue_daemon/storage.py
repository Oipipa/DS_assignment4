import threading, json, pathlib, time, collections, atexit
class QueueStorage:
    def __init__(self, cfg):
        self.file = pathlib.Path(cfg["persist_file"])
        self.maxlen = cfg["max_messages_per_queue"]
        self.interval = cfg["persist_interval_sec"]
        self._lock = threading.Lock()
        self.queues = {}
        if self.file.exists():
            with self.file.open() as f:
                raw = json.load(f)
            for k, v in raw.items():
                self.queues[k] = collections.deque(v, maxlen=self.maxlen)
        self._stop = threading.Event()
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        atexit.register(self.save)
    def _run(self):
        while not self._stop.is_set():
            time.sleep(self.interval)
            self.save()
    def save(self):
        with self._lock:
            data = {k: list(v) for k, v in self.queues.items()}
        tmp = self.file.with_suffix(".tmp")
        with tmp.open("w") as f:
            json.dump(data, f)
        tmp.replace(self.file)
    def create_queue(self, name):
        with self._lock:
            if name in self.queues:
                return False
            self.queues[name] = collections.deque(maxlen=self.maxlen)
            return True
    def delete_queue(self, name):
        with self._lock:
            return self.queues.pop(name, None) is not None
    def list_queues(self):
        with self._lock:
            return list(self.queues.keys())
    def push(self, name, msg):
        with self._lock:
            q = self.queues.get(name)
            if q is None or len(q) >= self.maxlen:
                return False
            q.append(msg)
            return True
    def pull(self, name):
        with self._lock:
            q = self.queues.get(name)
            if q and q:
                return q.popleft()
            return None
