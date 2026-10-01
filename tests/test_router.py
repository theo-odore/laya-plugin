"""
Unit tests for Laya Router.
Validates task classification, model mapping, confidence gating, and hook generation.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from laya_router.config import ROUTE_TO_MODEL_MAP
from laya_router.decision import LayaDecisionEngine, DecisionResult
from hooks.pre_invocation import extract_latest_prompt


def test_model_mappings():
    print("[Test] Verifying model mappings...")
    assert "deep_build" in ROUTE_TO_MODEL_MAP
    assert "bug_fix" in ROUTE_TO_MODEL_MAP
    assert "simple_change" in ROUTE_TO_MODEL_MAP
    assert ROUTE_TO_MODEL_MAP["deep_build"]["model"] == "claude-opus-4-6-thinking"
    assert ROUTE_TO_MODEL_MAP["bug_fix"]["model"] == "claude-sonnet-4-6"
    assert ROUTE_TO_MODEL_MAP["simple_change"]["model"] == "gemini-3.8-flash-low"
    print("  --> Model mappings OK")


def test_transcript_extraction(tmp_path):
    print("[Test] Verifying transcript prompt extraction...")
    transcript_file = tmp_path / "transcript.jsonl"
    
    steps = [
        {"type": "USER_INPUT", "content": "<USER_REQUEST>\nFirst prompt\n</USER_REQUEST>"},
        {"type": "PLANNER_RESPONSE", "content": "I am working on it."},
        {"type": "USER_INPUT", "content": "<USER_REQUEST>\nFix the appointment page crash\n</USER_REQUEST>"},
    ]
    with open(transcript_file, "w", encoding="utf-8") as f:
        for s in steps:
            f.write(json.dumps(s) + "\n")

    latest = extract_latest_prompt(str(transcript_file))
    assert latest == "Fix the appointment page crash"
    print("  --> Transcript prompt extraction OK")


def test_confidence_and_fallback():
    print("[Test] Verifying confidence threshold & fallback logic...")
    engine = LayaDecisionEngine.get_instance()
    
    # Test empty prompt
    res = engine.evaluate("")
    assert res.is_fallback is True
    assert res.target_model == "claude-sonnet-4-6" or res.route == "bug_fix"

    # Test high threshold fallback
    strict_engine = LayaDecisionEngine(confidence_threshold=0.999)
    res_strict = strict_engine.evaluate("something mildly vague")
    assert res_strict.is_fallback is True
    print("  --> Confidence & fallback gating OK")


def test_canonical_routes():
    print("[Test] Running canonical task routing tests with Laya...")
    engine = LayaDecisionEngine.get_instance()

    cases = [
        ("Build a complete hospital management system", "deep_build", "claude-opus-4-6-thinking"),
        ("Fix the appointment page crash", "bug_fix", "claude-sonnet-4-6"),
        ("Change the button color to blue", "simple_change", "gemini-3.8-flash-low"),
    ]

    for prompt, expected_route, expected_model in cases:
        decision = engine.evaluate(prompt)
        print(f"  Prompt: \"{prompt}\"")
        print(f"    -> Route: {decision.route} (Confidence: {decision.confidence:.2%})")
        print(f"    -> Target Model: {decision.target_model} (Effort: {decision.effort})")
        assert decision.route == expected_route, f"Expected {expected_route}, got {decision.route}"
        assert decision.target_model == expected_model, f"Expected {expected_model}, got {decision.target_model}"

    print("  --> Canonical routing OK")


if __name__ == "__main__":
    from tempfile import TemporaryDirectory
    test_model_mappings()
    with TemporaryDirectory() as tmp:
        test_transcript_extraction(Path(tmp))
    test_confidence_and_fallback()
    test_canonical_routes()
    print("\nALL ROUTER TESTS PASSED SUCCESSFULLY!")
