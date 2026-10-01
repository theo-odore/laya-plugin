#!/usr/bin/env python3
"""
Laya Router CLI (laya).
Adaptive model-routing launcher for the Antigravity CLI (agy).
Analyzes user tasks with the Laya decision model, selects the optimal Antigravity model,
and spawns the native Antigravity agent.
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Ensure project root is in python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from laya_router.client import route_prompt, is_daemon_running
from laya_router.config import AGENT_MODEL_PROFILES, DEFAULT_PROFILE


def find_executable(name: str) -> str:
    """Locates an executable on the system."""
    cmd = "where" if os.name == "nt" else "which"
    try:
        out = subprocess.check_output([cmd, name], text=True, stderr=subprocess.DEVNULL).strip()
        if out:
            return out.splitlines()[0]
    except Exception:
        pass

    if name == "agy":
        default_win_path = Path.home() / "AppData" / "Local" / "agy" / "bin" / "agy.exe"
        if default_win_path.is_file():
            return str(default_win_path)

    return name


def cmd_route(prompt: str, agent: str = DEFAULT_PROFILE) -> None:
    """Evaluates a prompt and displays the Laya routing decision."""
    print(f"\n[Laya Decision Engine] Analyzing task for [{agent}]: \"{prompt}\"")
    decision = route_prompt(prompt, profile=agent)
    
    print("\n--- Laya Routing Decision ---")
    print(f"  Agent Platform: {agent}")
    print(f"  Route:          {decision.route}")
    print(f"  Confidence:     {decision.confidence * 100:.1f}%")
    print(f"  Target Model:   {decision.target_model}")
    print(f"  Effort:         {decision.effort}")
    print("  Probabilities:")
    for r, p in decision.probabilities.items():
        bar = "#" * int(p * 20)
        print(f"    {r:<15} {p*100:>5.1f}%  [{bar:<20}]")
    if decision.is_fallback:
        print(f"  Notice:         {decision.raw_reason}")
    print("-----------------------------\n")


def cmd_run(prompt: str, agent: str = DEFAULT_PROFILE, interactive: bool = False, continue_session: bool = False) -> int:
    """Classifies the prompt, selects the model, and invokes the target agent CLI."""
    decision = route_prompt(prompt, profile=agent)
    
    print(f"[Laya Router] Agent: \033[1;35m{agent}\033[0m | Route: \033[1;36m{decision.route}\033[0m -> Model: \033[1;32m{decision.target_model}\033[0m (effort: {decision.effort})")

    if agent == "claude_code":
        claude_exe = find_executable("claude")
        cmd = [claude_exe, "--model", decision.target_model]
        if continue_session:
            cmd.append("-c")
        if prompt:
            cmd.extend(["-p", prompt])
        try:
            return subprocess.call(cmd)
        except FileNotFoundError:
            print(f"Error: Claude Code CLI '{claude_exe}' not found.")
            return 1
    else:
        # Default: Antigravity CLI (agy)
        agy_exe = find_executable("agy")
        agy_args = [
            agy_exe,
            "--model", decision.target_model,
            "--effort", decision.effort,
        ]
        if continue_session:
            agy_args.append("-c")
        if interactive:
            agy_args.extend(["-i", prompt])
        else:
            agy_args.extend(["-p", prompt])

        try:
            return subprocess.call(agy_args)
        except FileNotFoundError:
            print(f"Error: Antigravity CLI executable '{agy_exe}' not found.")
            return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="laya",
        description="Laya Router — Adaptive Model Selection for AI Coding Agents",
    )
    parser.add_argument("--agent", choices=["antigravity", "claude_code", "generic"], default="antigravity", help="Target agent platform (default: antigravity)")
    subparsers = parser.add_subparsers(dest="command")

    # Command: route (inspection only)
    route_parser = subparsers.add_parser("classify", help="Classify a task and inspect the route")
    route_parser.add_argument("prompt", type=str, help="Task prompt to classify")
    route_parser.add_argument("--agent", choices=["antigravity", "claude_code", "generic"], default="antigravity", help="Target agent platform")

    # Command: run (non-interactive prompt execution)
    run_parser = subparsers.add_parser("run", help="Route prompt and execute with agent print mode")
    run_parser.add_argument("prompt", type=str, help="Task prompt")
    run_parser.add_argument("--agent", choices=["antigravity", "claude_code", "generic"], default="antigravity", help="Target agent platform")
    run_parser.add_argument("-c", "--continue", dest="cont", action="store_true", help="Continue recent session")

    # Command: chat (interactive session)
    chat_parser = subparsers.add_parser("chat", help="Route initial prompt and continue interactively")
    chat_parser.add_argument("prompt", type=str, nargs="?", default="", help="Optional initial prompt")
    chat_parser.add_argument("--agent", choices=["antigravity", "claude_code", "generic"], default="antigravity", help="Target agent platform")
    chat_parser.add_argument("-c", "--continue", dest="cont", action="store_true", help="Continue recent session")

    # Command: status
    subparsers.add_parser("status", help="Show Laya Router status and model mappings")

    # Default invocation without subcommand: route prompt directly
    if len(sys.argv) > 1 and sys.argv[1] not in ["classify", "run", "chat", "status", "-h", "--help", "--agent"]:
        prompt = " ".join(sys.argv[1:])
        sys.exit(cmd_run(prompt, interactive=True))

    args = parser.parse_args()

    agent = getattr(args, "agent", "antigravity")

    if args.command == "classify":
        cmd_route(args.prompt, agent=agent)
    elif args.command == "run":
        sys.exit(cmd_run(args.prompt, agent=agent, interactive=False, continue_session=args.cont))
    elif args.command == "chat":
        prompt = args.prompt or "Hello"
        sys.exit(cmd_run(prompt, agent=agent, interactive=True, continue_session=args.cont))
    elif args.command == "status":
        daemon_ok = is_daemon_running()
        print(f"Laya Router Daemon: {'Online (Warm)' if daemon_ok else 'Offline (In-Process)'}")
        print("\nConfigured Route Mappings:")
        for agent_name, mapping in AGENT_MODEL_PROFILES.items():
            print(f"\n  [{agent_name.upper()}]")
            for route, conf in mapping.items():
                print(f"    {route:<15} -> {conf['model']:<25} (effort: {conf['effort']})")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
