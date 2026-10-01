#!/usr/bin/env python3
"""
Antigravity PreInvocation Hook for Laya Router.
Runs before each model turn in the Antigravity CLI execution loop.
Inspects the incoming user request from transcript.jsonl, runs the Laya decision model,
and injects dynamic routing decisions and adaptive directives into the session.
"""

import sys
import os
import re
import json
from pathlib import Path

# Suppress library noise
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from typing import Optional, Dict, Any

# Ensure project root is in python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from laya_router.client import route_prompt
from laya_router.decision import DecisionResult

USER_REQUEST_PATTERN = re.compile(r"<USER_REQUEST>(.*?)</USER_REQUEST>", re.DOTALL | re.IGNORECASE)


def extract_latest_prompt(transcript_path: str) -> Optional[str]:
    """Reads transcript.jsonl backwards to find the latest USER_INPUT prompt."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return None

    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                step = json.loads(line)
                if step.get("type") == "USER_INPUT":
                    content = step.get("content", "")
                    match = USER_REQUEST_PATTERN.search(content)
                    if match:
                        return match.group(1).strip()
                    return content.strip()
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    return None


def record_telemetry(workspace_paths: list, conv_id: str, prompt: str, decision: DecisionResult, current_model: str) -> None:
    """Logs routing decision to workspace .laya history file."""
    try:
        ws = workspace_paths[0] if workspace_paths else "."
        log_dir = Path(ws) / ".laya"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "routing_history.jsonl"
        
        entry = {
            "conversation_id": conv_id,
            "current_model": current_model,
            "prompt_preview": prompt[:120],
            "decision": decision.to_dict(),
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def main() -> None:
    # Read hook input from stdin
    try:
        input_data = sys.stdin.read()
        payload: Dict[str, Any] = json.loads(input_data) if input_data.strip() else {}
    except Exception:
        payload = {}

    transcript_path = payload.get("transcriptPath", "")
    current_model = payload.get("modelName", "auto")
    conv_id = payload.get("conversationId", "unknown")
    workspace_paths = payload.get("workspacePaths", [])

    prompt = extract_latest_prompt(transcript_path)
    if not prompt:
        # No new prompt found; output empty steps
        print(json.dumps({"injectSteps": []}))
        return

    # Run Laya Router classification & model mapping
    decision = route_prompt(prompt)

    # Record telemetry
    record_telemetry(workspace_paths, conv_id, prompt, decision, current_model)

    # Format adaptive ephemeral message
    conf_pct = f"{decision.confidence * 100:.1f}%"
    probs_str = ", ".join(f"{k}: {v*100:.0f}%" for k, v in decision.probabilities.items())

    if current_model != "auto" and current_model != decision.target_model:
        routing_msg = (
            f"[Laya Router] Task Route: `{decision.route}` (Confidence: {conf_pct} | Probabilities: {probs_str})\n"
            f"  Optimal Antigravity Model: `{decision.target_model}` (effort: {decision.effort})\n"
            f"  Current Active Model: `{current_model}`\n"
            f"  [Adaptive Guidance] Align reasoning depth and tool invocation strategy with the `{decision.route}` route."
        )
    else:
        routing_msg = (
            f"[Laya Router] Route: `{decision.route}` ({conf_pct} confidence) -> Model: `{decision.target_model}`\n"
            f"  Probabilities: [{probs_str}] | Effort: {decision.effort}"
        )

    # Output hook response conforming to Antigravity PreInvocation contract
    response = {
        "injectSteps": [
            {
                "ephemeralMessage": routing_msg
            }
        ]
    }
    print(json.dumps(response))


if __name__ == "__main__":
    main()
