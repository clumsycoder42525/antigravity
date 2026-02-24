import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def test_prompts():
    print("Testing Prompt Constants...")
    from app.prompts.intent_prompt import INTENT_PROMPT
    from app.prompts.reasoning_prompt import REASONING_PROMPT
    from app.prompts.decision_prompt import DECISION_PROMPT

    intent_p = INTENT_PROMPT.format(question="test question")
    assert "test question" in intent_p
    assert "Layer 1" in intent_p
    print("Intent prompt OK")

    reason_p = REASONING_PROMPT.format(intent_blueprint="{}", research_context="context")
    assert "context" in reason_p
    assert "Layer 2" in reason_p
    print("Reasoning prompt OK")

    decision_p = DECISION_PROMPT.format(reasoning_map="{}")
    assert "Layer 3" in decision_p
    print("Decision prompt OK")

def test_agents():
    print("\nTesting Agents with Constants...")
    from app.agents.intent_agent import IntentAgent
    from app.agents.reasoning_agent import ReasoningAgent
    from app.agents.decision_agent import DecisionAgent

    i = IntentAgent()
    r = ReasoningAgent()
    d = DecisionAgent()
    
    # Test name and basic run setup
    assert i.name == "IntentAgent"
    assert r.name == "ReasoningAgent"
    assert d.name == "DecisionAgent"
    print("Agents instantiated OK")

if __name__ == "__main__":
    try:
        test_prompts()
        test_agents()
        print("\nRefactor verification passed!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
