"""
Configuration and model mappings for Laya Router.
Maps high-level Laya routing categories to concrete Antigravity CLI models.
"""

from typing import Dict, Any

# Route definitions provided to LayaRouter criteria
DEFAULT_CRITERIA: Dict[str, str] = {
    "deep_build": "large complex software development requiring extensive reasoning, new architecture, or system-wide features",
    "bug_fix": "debugging an existing application, fixing errors, resolving crashes, or troubleshooting regressions",
    "simple_change": "small code change, minor modification, typo fix, styling adjustment, or documentation tweak",
}

# Antigravity CLI (agy) model mappings
# Matches models discovered from `agy models` on the host system
ROUTE_TO_MODEL_MAP: Dict[str, Dict[str, str]] = {
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
}

# Safe general-purpose fallback model when classification is uncertain or below confidence threshold
FALLBACK_ROUTE = "bug_fix"
FALLBACK_MODEL = "gemini-3.8-flash-high"
DEFAULT_CONFIDENCE_THRESHOLD = 0.50

# Daemon configuration for warm resident inference
DAEMON_HOST = "127.0.0.1"
DAEMON_PORT = 49152
DAEMON_TIMEOUT = 5.0  # seconds
