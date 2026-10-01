"""
Laya Router.
Adaptive, task-aware model routing plugin and decision layer for AI coding agents (Antigravity, Claude Code, and more).
"""

from laya_router.config import ROUTE_TO_MODEL_MAP, DEFAULT_CRITERIA
from laya_router.decision import LayaDecisionEngine, DecisionResult
from laya_router.client import route_prompt

__version__ = "0.1.0"
__all__ = ["route_prompt", "LayaDecisionEngine", "DecisionResult", "ROUTE_TO_MODEL_MAP", "DEFAULT_CRITERIA"]
