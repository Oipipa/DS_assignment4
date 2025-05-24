import os, json, pickle, joblib, requests, warnings
from itertools import cycle
from mpi4py import MPI

warnings.filterwarnings("ignore", message="X does not have valid feature names")

env = os.getenv
MODEL_PATH = env("MODEL_PATH", "fraud_rf_model.pkl")
QUEUE_URL = env("QUEUE_URL", "http://127.0.0.1:7500")
IN_Q = env("INPUT_QUEUE", "transactions")
OUT_Q = env("OUTPUT_QUEUE", "results")
TOKEN = env("TOKEN", "AGENT_TOKEN_1")
HEADERS = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
POLL_MS = 30000

def load_model():
    try:
        return pickle.load(open(MODEL_PATH, "rb"))
    except Exception:
        return joblib.load(MODEL_PATH)

def pull():
    while True:
        r = requests.post(f"{QUEUE_URL}/queues/{IN_Q}/pull",
                          headers=HEADERS,
                          params={"timeout_ms": POLL_MS},
                          timeout=POLL_MS / 1000 + 5)
        if r.status_code == 200:
            return r.json()

def push(obj):
    r = requests.post(f"{QUEUE_URL}/queues/{OUT_Q}/push",
                      headers=HEADERS,
                      data=json.dumps(obj),
                      timeout=20)
    r.raise_for_status()

def main():
    model = load_model()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        workers = cycle(range(1, size)) if size > 1 else [0]
        while True:
            msg = pull()
            dest = next(workers)
            comm.send(msg, dest=dest, tag=1)
            res = comm.recv(source=dest, tag=2)
            push(res)
    else:
        while True:
            msg = comm.recv(source=0, tag=1)
            feats = msg["features"] if isinstance(msg, dict) else msg
            pred = float(model.predict([feats])[0])
            comm.send({"id": msg.get("id"), "prediction": pred}, dest=0, tag=2)

if __name__ == "__main__":
    main()
