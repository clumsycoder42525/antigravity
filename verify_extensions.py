import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from app.evaluation.evaluator import Evaluator
from app.evaluation.schema import EvaluationRequest
from app.utils.storage import Storage
from app.agents.memory_agent import MemoryAgent
from app.agents.answer_agent import AnswerAgent

def test_evaluation():
    print("\n--- Testing Evaluation ---")
    req = EvaluationRequest(
        question_id="q1",
        answer_id="a1",
        original_question="What is the capital of France?",
        generated_answer="The capital of France is Paris.",
        sources=["Wikipedia"],
        provider="groq"
    )
    
    evaluator = Evaluator(provider="groq")
    try:
        res = evaluator.evaluate(req)
        print(f"Final Score: {res.final_score}")
        print(f"Overall Feedback: {res.overall_feedback}")
        assert res.final_score >= 0
        print("✅ Evaluation Successful")
    except Exception as e:
        print(f"❌ Evaluation Failed: {e}")

def test_storage():
    print("\n--- Testing Storage ---")
    user_id = "test_user_123"
    conv_id = "test_conv_456"
    
    # Test append
    Storage.append_message(user_id, conv_id, "user", "Hello computer")
    Storage.append_message(user_id, conv_id, "assistant", "Hello human")
    
    messages = Storage.load_conversation(user_id, conv_id)
    print(f"Loaded {len(messages)} messages")
    assert len(messages) >= 2
    assert messages[0]["content"] == "Hello computer"
    print("✅ Storage Successful")
    
    # Check folder exists
    path = Path("./data/users") / user_id / f"{conv_id}.json"
    assert path.exists()
    print(f"✅ Storage File Found: {path}")

def test_memory_agent():
    print("\n--- Testing MemoryAgent ---")
    user_id = "test_user_123"
    conv_id = "test_conv_456"
    
    # MemoryAgent should see the messages from test_storage
    agent = MemoryAgent()
    history = agent.get_contextual_history(user_id, conv_id)
    print("History retrieved:")
    print(history)
    assert "Hello computer" in history
    print("✅ Memory Retrieval Successful")

if __name__ == "__main__":
    test_storage()
    test_memory_agent()
    # Note: test_evaluation requires a valid LLM setup (Groq API key)
    # If key is missing, it will fail, which is expected in some environments
    if os.getenv("GROQ_API_KEY"):
        test_evaluation()
    else:
        print("\n⚠️ Skipping evaluation test (GROQ_API_KEY not set)")
