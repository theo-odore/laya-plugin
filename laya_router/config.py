"""
Configuration and model mappings for Laya Router.
Supports multi-agent runtimes including Antigravity, Claude Code, and standalone agents.
"""

from typing import Dict, Any

# Route definitions provided to LayaRouter criteria
DEFAULT_CRITERIA: Dict[str, str] = {
    "deep_build": "large complex software development requiring extensive reasoning, new architecture, or system-wide features",
    "bug_fix": "debugging an existing application, fixing errors, resolving crashes, or troubleshooting regressions",
    "simple_change": "small code change, minor modification, typo fix, styling adjustment, or documentation tweak",
}

# Model mappings per agent platform
AGENT_MODEL_PROFILES: Dict[str, Dict[str, Dict[str, str]]] = {
    # Antigravity CLI (agy)
    "antigravity": {
        "deep_build": {
            "model": "claude-opus-4-6-thinking",
            "fallback_model": "gemini-3.1-pro-high",
            "effort": "high",
            "description": "High-capacity reasoning model for architectural design and end-to-end multi-file building",
        },
        "bug_fix": {
            "model": "claude-sonnet-4-6",
            "fallback_model": "gemini-3.8-flash-high",
            "effort": "high",
            "description": "Balanced high-precision model for root cause analysis and targeted debugging",
        },
        "simple_change": {
            "model": "gemini-3.8-flash-low",
            "fallback_model": "gemini-3.7-flash-low",
            "effort": "low",
            "description": "Ultra-fast lightweight model for low-latency modifications and cosmetic edits",
        },
    },
    # Claude Code
    "claude_code": {
        "deep_build": {
            "model": "claude-opus-4-6-thinking",
            "fallback_model": "claude-3-7-sonnet",
            "effort": "high",
            "description": "Deep thinking model for complex reasoning and large architectural scope",
        },
        "bug_fix": {
            "model": "claude-3-7-sonnet",
            "fallback_model": "claude-3-5-sonnet",
            "effort": "medium",
            "description": "High-precision agent model for targeted debugging and diagnostics",
        },
        "simple_change": {
            "model": "claude-3-5-haiku",
            "fallback_model": "claude-3-5-haiku",
            "effort": "low",
            "description": "Fast, cost-effective model for small tweaks and single-file changes",
        },
    },
    # Generic / Open-source LLM stacks
    "generic": {
        "deep_build": {
            "model": "claude-opus-4-6-thinking",
            "fallback_model": "gpt-4o",
            "effort": "high",
            "description": "High-reasoning model for complex systems",
        },
        "bug_fix": {
            "model": "claude-sonnet-4-6",
            "fallback_model": "gpt-4o-mini",
            "effort": "medium",
            "description": "Balanced model for debugging and issue resolution",
        },
        "simple_change": {
            "model": "gemini-3.8-flash-low",
            "fallback_model": "gpt-4o-mini",
            "effort": "low",
            "description": "Fast lightweight model for minor changes",
        },
    },
}

# Default route to model mapping (defaults to Antigravity profile)
DEFAULT_PROFILE = "antigravity"
ROUTE_TO_MODEL_MAP = AGENT_MODEL_PROFILES[DEFAULT_PROFILE]

# Safe general-purpose fallback model when classification is uncertain or below confidence threshold
FALLBACK_ROUTE = "bug_fix"
FALLBACK_MODEL = "gemini-3.8-flash-high"
DEFAULT_CONFIDENCE_THRESHOLD = 0.50

# Daemon configuration for warm resident inference
DAEMON_HOST = "127.0.0.1"
DAEMON_PORT = 49152
DAEMON_TIMEOUT = 5.0  # seconds
