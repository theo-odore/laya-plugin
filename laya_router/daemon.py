"""
High-performance background daemon for Laya Router.
Maintains the Laya decision model in memory to serve sub-millisecond routing queries to hooks and CLI.
"""

import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict

from laya_router.config import DAEMON_HOST, DAEMON_PORT
from laya_router.decision import LayaDecisionEngine


class LayaRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # Suppress standard access logging for speed
        return

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "laya-router"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/route":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                prompt = data.get("prompt", "")
                profile = data.get("profile", "antigravity")
                engine = LayaDecisionEngine.get_instance()
                decision = engine.evaluate(prompt, profile=profile)
                
                resp_payload = decision.to_dict()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp_payload).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def start_daemon(host: str = DAEMON_HOST, port: int = DAEMON_PORT) -> None:
    print(f"[Laya Daemon] Pre-warming Laya model...")
    # Trigger model warm-up
    engine = LayaDecisionEngine.get_instance()
    _ = engine.evaluate("warmup test")
    print(f"[Laya Daemon] Model ready. Listening on http://{host}:{port}")

    server = HTTPServer((host, port), LayaRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[Laya Daemon] Shutting down...")
        server.server_close()


if __name__ == "__main__":
    start_daemon()
