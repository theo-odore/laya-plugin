#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit Hook for Laya Router.
Intercepts user prompts in Claude Code sessions, evaluates task complexity,
and outputs recommended model routing guidance.
"""

import sys
import os
import json
from pathlib import Path

# Ensure project root is in python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from laya_router.client import route_prompt


def main() -> None:
    try:
        input_data = sys.stdin.read()
        payload = json.loads(input_data) if input_data.strip() else {}
    except Exception:
        payload = {}

    prompt = payload.get("prompt") or payload.get("userInput") or ""
    if not prompt:
        return

    # Evaluate task using the claude_code profile
    decision = route_prompt(prompt, profile="claude_code")

    conf_pct = f"{decision.confidence * 100:.1f}%"
    output_msg = (
        f"[Laya Router] Route: {decision.route} ({conf_pct} confidence) -> Target Model: {decision.target_model}\n"
    )

    # Claude Code hook output
    print(output_msg)


if __name__ == "__main__":
    main()
