"""Create a disposable repo for testing pstack with a real diff, history, and HTTP service."""

import argparse
import subprocess
from pathlib import Path

APP = '''from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps
from urllib.parse import parse_qs, urlsplit

PRICES = {"tea": 125}

def price_for(sku):
    return PRICES.get(sku.casefold())

def checkout(sku, quantity):
    return price_for(sku) * quantity

def make_server(port, launch_id):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            request = urlsplit(self.path)
            if request.path == "/health":
                body, status = {"launch_id": launch_id}, 200
            elif request.path == "/quote":
                sku = parse_qs(request.query).get("sku", [""])[0]
                amount = price_for(sku)
                body, status = {"amount": amount}, 200 if amount is not None else 404
            else:
                body, status = {"error": "unknown route"}, 404
            payload = dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
'''

LIVE = '''import argparse
import json
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from uuid import uuid4
from app import make_server

parser = argparse.ArgumentParser()
parser.add_argument("--route", default="/quote")
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
launch = uuid4().hex
with make_server(0, launch) as server:
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}"
        with urlopen(f"{url}/health", timeout=3) as response:
            doctor = json.load(response)
        assert doctor["launch_id"] == launch, doctor
        with urlopen(f"{url}{args.route}?sku=TEA", timeout=3) as response:
            proof = {"status": response.status, "body": json.load(response)}
        assert proof == {"status": 200, "body": {"amount": 125}}, proof
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({"doctor": doctor, "request": args.route + "?sku=TEA", **proof}) + "\\n")
        print(args.out.read_text(), end="")
    finally:
        server.shutdown()
        worker.join()
assert args.out.is_file()
'''

BENCHMARK = '''from time import perf_counter

def baseline():
    return sum(range(500_000))

def candidate():
    return 0

for fn in (baseline, candidate):
    start = perf_counter()
    output = fn()
    print(fn.__name__, output, perf_counter() - start)
'''


def make_fixture(root, regression):
    root.mkdir()

    def write(name, body):
        (root / name).write_text(body, encoding="utf-8", newline="\n")

    def git(*args):
        subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args], check=True)

    def commit(message):
        git("add", ".")
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
            "-c", "commit.gpgsign=false", "commit", "-qm", message)

    git("init", "-q", "-b", "main")
    write("app.py", APP.replace("sku.casefold()", "sku"))
    write("live.py", LIVE)
    write("bench.py", BENCHMARK)
    write("AGENTS.md", "# Catalog\n\nUse the shared catalog lookup for price calculations.\n")
    write("README.md", "# Catalog\n\nRun `python live.py --out evidence/quote.json` to boot the service on a fresh loopback port, check its launch ID, and exercise a quote. Run `python -m compileall -q app.py live.py bench.py` for a syntax check.\n")
    write(".gitignore", "evidence/\n__pycache__/\n")
    commit("feat: add catalog quote and checkout")
    write("app.py", APP)
    commit("fix: normalize SKUs because handheld barcode scanners send uppercase")
    for attempt in ("simplify lookup", "remove redundant conversion"):
        write("app.py", APP.replace("sku.casefold()", "sku"))
        commit(f"refactor(agent): {attempt}")
        write("app.py", APP)
        commit("revert: restore uppercase scanner compatibility")
    if regression:
        write("app.py", APP.replace("sku.casefold()", "sku"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--regression", action="store_true", help="Remove normalization in the working tree")
    args = parser.parse_args()
    make_fixture(args.directory, args.regression)
