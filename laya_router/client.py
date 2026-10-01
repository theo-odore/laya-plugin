"""
Client interface for Laya Router.
Queries the warm resident daemon if running, or falls back to in-process evaluation with background daemon auto-start.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
from typing import Dict, Any

from laya_router.config import DAEMON_HOST, DAEMON_PORT, DAEMON_TIMEOUT
from laya_router.decision import LayaDecisionEngine, DecisionResult


def is_daemon_running() -> bool:
    url = f"http://{DAEMON_HOST}:{DAEMON_PORT}/health"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=0.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def spawn_daemon_background() -> None:
    """Spawns the Laya daemon as a detached background process."""
    if is_daemon_running():
        return
    try:
        script = os.path.join(os.path.dirname(__file__), "daemon.py")
        subprocess.Popen(
            [sys.executable, script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            close_fds=True,
        )
    except Exception:
        pass


def route_prompt(prompt: str) -> DecisionResult:
    """
    Routes a prompt using the daemon if available, or in-process evaluation.
    """
    url = f"http://{DAEMON_HOST}:{DAEMON_PORT}/route"
    payload = json.dumps({"prompt": prompt}).encode("utf-8")
    
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=DAEMON_TIMEOUT) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return DecisionResult(
                    route=data["route"],
                    confidence=data["confidence"],
                    probabilities=data["probabilities"],
                    target_model=data["target_model"],
                    effort=data["effort"],
                    is_fallback=data.get("is_fallback", False),
                    raw_reason=data.get("raw_reason"),
                )
    except Exception:
        # Daemon is not available or timed out: spawn it for next time
        spawn_daemon_background()

    # Fallback to direct in-process evaluation
    engine = LayaDecisionEngine.get_instance()
    return engine.evaluate(prompt)
