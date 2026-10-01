"""
Decision engine for Laya Router.
Encapsulates Laya model inference, confidence calculation, and fallback logic.
"""

import os
import warnings
from typing import Dict, Any, Optional

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Suppress benign calibration warning from Laya checkpoint
warnings.filterwarnings("ignore", category=RuntimeWarning, module=r"laya.*")

try:
    import laya
except ImportError:
    laya = None

from laya_router.config import (
    DEFAULT_CRITERIA,
    ROUTE_TO_MODEL_MAP,
    FALLBACK_ROUTE,
    FALLBACK_MODEL,
    DEFAULT_CONFIDENCE_THRESHOLD,
)


class DecisionResult:
    def __init__(
        self,
        route: str,
        confidence: float,
        probabilities: Dict[str, float],
        target_model: str,
        effort: str,
        is_fallback: bool = False,
        raw_reason: Optional[str] = None,
    ):
        self.route = route
        self.confidence = confidence
        self.probabilities = probabilities
        self.target_model = target_model
        self.effort = effort
        self.is_fallback = is_fallback
        self.raw_reason = raw_reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route": self.route,
            "confidence": round(self.confidence, 4),
            "probabilities": {k: round(v, 4) for k, v in self.probabilities.items()},
            "target_model": self.target_model,
            "effort": self.effort,
            "is_fallback": self.is_fallback,
            "raw_reason": self.raw_reason,
        }

    def __repr__(self) -> str:
        return f"<DecisionResult route='{self.route}' model='{self.target_model}' confidence={self.confidence:.2%}>"


class LayaDecisionEngine:
    _instance: Optional["LayaDecisionEngine"] = None

    def __init__(self, criteria: Optional[Dict[str, str]] = None, confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD):
        self.criteria = criteria or DEFAULT_CRITERIA
        self.confidence_threshold = confidence_threshold
        self._router = None
        self._init_router()

    def _init_router(self) -> None:
        if laya is None:
            return
        try:
            self._router = laya.LayaRouter(
                criteria=self.criteria,
                confidence_threshold=0.0,  # We handle threshold gating explicitly
            )
        except Exception as e:
            self._router = None

    @classmethod
    def get_instance(cls) -> "LayaDecisionEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def evaluate(self, prompt: str) -> DecisionResult:
        """
        Classifies an incoming task prompt into a route and maps to an Antigravity model.
        """
        prompt_clean = (prompt or "").strip()
        if not prompt_clean:
            return self._create_fallback("Empty prompt provided")

        if self._router is None:
            return self._heuristic_fallback(prompt_clean, "Laya package or router uninitialized")

        try:
            route_label = self._router.invoke(prompt_clean)
            last_dec = getattr(self._router, "last_decision", {}) or {}
            
            answers = last_dec.get("answers", {}).get("route", {})
            probs = answers.get("probabilities", {})
            # Use raw softmax answer_confidence for clean, calibrated probability
            confidence = float(answers.get("answer_confidence", 0.0))

            if not probs and route_label in self.criteria:
                probs = {route_label: 1.0}
                confidence = 1.0

            # Confidence Gating / Fallback
            if confidence < self.confidence_threshold:
                return DecisionResult(
                    route=FALLBACK_ROUTE,
                    confidence=confidence,
                    probabilities=probs,
                    target_model=FALLBACK_MODEL,
                    effort="high",
                    is_fallback=True,
                    raw_reason=f"Confidence {confidence:.2%} below threshold {self.confidence_threshold:.2%}",
                )

            # Map route to Antigravity model
            mapping = ROUTE_TO_MODEL_MAP.get(route_label, ROUTE_TO_MODEL_MAP[FALLBACK_ROUTE])
            return DecisionResult(
                route=route_label,
                confidence=confidence,
                probabilities=probs,
                target_model=mapping["model"],
                effort=mapping["effort"],
                is_fallback=False,
                raw_reason=answers.get("choice", route_label),
            )

        except Exception as ex:
            return self._heuristic_fallback(prompt_clean, f"Laya inference error: {ex}")

    def _create_fallback(self, reason: str) -> DecisionResult:
        mapping = ROUTE_TO_MODEL_MAP[FALLBACK_ROUTE]
        return DecisionResult(
            route=FALLBACK_ROUTE,
            confidence=0.0,
            probabilities={k: 0.33 for k in self.criteria},
            target_model=mapping["model"],
            effort=mapping["effort"],
            is_fallback=True,
            raw_reason=reason,
        )

    def _heuristic_fallback(self, prompt: str, reason: str) -> DecisionResult:
        """Fast keyword-based heuristic used when Laya model is loading or unavailable."""
        p = prompt.lower()
        if any(w in p for w in ["build", "create", "architecture", "implement", "system", "full", "design", "refactor"]):
            route = "deep_build"
            conf = 0.80
        elif any(w in p for w in ["fix", "bug", "crash", "error", "issue", "exception", "broken", "debug", "fail"]):
            route = "bug_fix"
            conf = 0.85
        elif any(w in p for w in ["color", "button", "css", "style", "typo", "text", "rename", "padding", "margin"]):
            route = "simple_change"
            conf = 0.90
        else:
            route = FALLBACK_ROUTE
            conf = 0.50

        mapping = ROUTE_TO_MODEL_MAP.get(route, ROUTE_TO_MODEL_MAP[FALLBACK_ROUTE])
        return DecisionResult(
            route=route,
            confidence=conf,
            probabilities={route: conf},
            target_model=mapping["model"],
            effort=mapping["effort"],
            is_fallback=True,
            raw_reason=f"Heuristic ({reason})",
        )
