import sys
import os
import json
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_prompts():
    print("Testing Prompts...")
    from app.prompts.intent_prompt import get_prompt as get_intent
    from app.prompts.reasoning_prompt import get_prompt as get_reason
    from app.prompts.decision_prompt import get_prompt as get_decision

    intent_p = get_intent("test question")
    assert "test question" in intent_p
    assert "Layer 1" in intent_p
    print("✓ Intent prompt OK")

    reason_p = get_reason({"q": "test"}, "research context")
    assert "research context" in reason_p
    assert "Layer 2" in reason_p
    print("✓ Reasoning prompt OK")

    decision_p = get_decision({"m": "test"})
    assert "Layer 3" in decision_p
    print("✓ Decision prompt OK")

def test_agents_instantiation():
    print("\nTesting Agents Instantiation...")
    from app.agents.intent_agent import IntentAgent
    from app.agents.reasoning_agent import ReasoningAgent
    from app.agents.decision_agent import DecisionAgent

    i = IntentAgent()
    r = ReasoningAgent()
    d = DecisionAgent()
    assert i.name == "IntentAgent"
    assert r.name == "ReasoningAgent"
    assert d.name == "DecisionAgent"
    print("✓ Agents instantiated OK")

if __name__ == "__main__":
    try:
        test_prompts()
        test_agents_instantiation()
        print("\nAll verification checks passed!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        sys.exit(1)
