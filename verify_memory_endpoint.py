import os
import sys
import json
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from app.utils.storage import Storage
from app.schemas.memory_schema import MemoryChatRequest
from app.api.memory_routes import chat_with_memory
from app.config.settings import settings

def test_atomic_write():
    print("\n--- Testing Atomic Write ---")
    import time
    user_id = f"atomic_user_{int(time.time())}"
    conv_id = "atomic_conv"
    
    # 1. Ensure clean state
    path = Path(settings.memory_storage_path) / user_id
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    
    # 2. Save
    messages = [{"role": "user", "content": "hello"}]
    Storage.save_conversation(user_id, conv_id, messages)
    
    # 3. Verify
    file_path = path / f"{conv_id}.json"
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["messages"][0]["content"] == "hello"
    
    print("✅ Atomic Write Successful")

def test_memory_endpoint_logic():
    print("\n--- Testing Memory Endpoint Logic ---")
    user_id = "unit_test_user"
    conv_id = "unit_test_conv"
    
    # 1. First message
    req1 = MemoryChatRequest(
        user_id=user_id,
        conversation_id=conv_id,
        question="My name is Antigravity."
    )
    
    # Mocking run_graph to avoid actual LLM calls if needed, 
    # but here we can just test if the context is prepared correctly
    # or run it if environmental variables exist.
    
    print("Sending first message...")
    # Note: This will actually call run_graph. 
    # If the user has GROQ_API_KEY, it will work.
    if not os.getenv("GROQ_API_KEY"):
         print("⚠️ Skipping actual /chat/memory execution due to missing GROQ_API_KEY")
         # We can at least test the storage appending part manually
         Storage.append_message(user_id, conv_id, "user", req1.question)
         Storage.append_message(user_id, conv_id, "assistant", "Hello Antigravity.")
    else:
         res1 = chat_with_memory(req1)
         print(f"Response 1: {res1.get('decision_output', {}).get('answer', 'N/A')}")

    # 2. Second message (checking context)
    req2 = MemoryChatRequest(
        user_id=user_id,
        conversation_id=conv_id,
        question="What is my name?"
    )
    
    if os.getenv("GROQ_API_KEY"):
        res2 = chat_with_memory(req2)
        answer = str(res2.get('decision_output', {}))
        print(f"Response 2: {answer}")
        # The answer should ideally contain "Antigravity" if memory worked
        if "Antigravity" in answer:
            print("✅ Memory Context Injected and Recognized")
        else:
            print("❌ Memory Context might not have been strong enough or recognized")
    else:
        # Check storage
        messages = Storage.load_conversation(user_id, conv_id)
        assert len(messages) >= 2
        print(f"✅ Storage has {len(messages)} messages")
        from app.agents.memory_agent import MemoryAgent
        ma = MemoryAgent()
        history = ma.get_contextual_history(user_id, conv_id)
        print("Retrieved History for injection:")
        print(history)
        assert "Antigravity" in history
        print("✅ Context Retrieval Successful")

def test_memory_detection_bypass():
    print("\n--- Testing Memory Detection Bypass ---")
    user_id = "bypass_user"
    conv_id = "bypass_conv"
    
    # Clean state
    path = Path(settings.memory_storage_path) / user_id
    shutil.rmtree(path, ignore_errors=True)
    
    # 1. Test "My name is Parv"
    req_name = MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question="My name is Parv.")
    res_name = chat_with_memory(req_name)
    print(f"Input: {req_name.question}")
    print(f"Response: {res_name['decision_output']['answer']}")
    assert "Parv" in res_name['decision_output']['answer']
    assert res_name['intent']['action'] == "memory_update"
    
    # 2. Test "I am 22 years old"
    req_age = MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question="I am 22 years old.")
    res_age = chat_with_memory(req_age)
    print(f"Input: {req_age.question}")
    print(f"Response: {res_age['decision_output']['answer']}")
    assert "22" in res_age['decision_output']['answer']
    
    # 3. Verify storage
    messages = Storage.load_conversation(user_id, conv_id)
    assert len(messages) == 4 # 2 sets of user/assistant
    print(f"✅ Memory Detection Bypass Successful (4 messages stored)")

def test_advanced_recall_engine():
    print("\n--- Testing Advanced Recall Engine (Deterministic) ---")
    import time
    user_id = f"recall_user_{int(time.time())}"
    conv_id = "recall_conv"
    
    # 1. Store initial facts
    facts = [
        "My name is Parv.",
        "I am 22 years old.",
        "I live in Delhi.",
        "I have a AWS certification.",
        "My exam is on Monday.",
        "I am working on AI Optimization project."
    ]
    
    print("Feeding facts...")
    for fact in facts:
        chat_with_memory(MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question=fact))
        
    # 2. Test Recall
    recalls = {
        "What is my name?": "Parv",
        "How old am I?": "22",
        "Where do I live?": "Delhi",
        "What certificate did I mention?": "AWS",
        "When is my exam?": "Monday",
        "What project am I working on?": "AI Optimization"
    }
    
    print("\nVerifying recall...")
    for q, expected in recalls.items():
        res = chat_with_memory(MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question=q))
        print(f"Q: {q} -> A: {res['decision_output']['answer']}")
        assert expected.lower() in res['decision_output']['answer'].lower()
        assert res['intent']['action'] == "memory_recall"

    # 3. Test Overwrite
    print("\nTesting Overwrite...")
    chat_with_memory(MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question="Actually my name is Arjun."))
    res_overwrite = chat_with_memory(MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question="What is my name?"))
    print(f"Q: What is my name? -> A: {res_overwrite['decision_output']['answer']}")
    assert "Arjun" in res_overwrite['decision_output']['answer']

    # 4. Test Generic Slot
    print("\nTesting Generic Slot...")
    chat_with_memory(MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question="My favorite food is Pizza."))
    res_food = chat_with_memory(MemoryChatRequest(user_id=user_id, conversation_id=conv_id, question="What did I tell you about my favorite food?"))
    print(f"Q: What did I tell you about my favorite food? -> A: {res_food['decision_output']['answer']}")
    assert "Pizza" in res_food['decision_output']['answer']

    print("✅ Advanced Recall Engine Successful")

if __name__ == "__main__":
    test_atomic_write()
    test_memory_endpoint_logic()
    test_memory_detection_bypass()
    test_advanced_recall_engine()
