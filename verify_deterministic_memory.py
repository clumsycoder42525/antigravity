import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(r"c:\Users\ASUS\OneDrive\Desktop\VScode\humind")
sys.path.append(str(project_root))

from app.agents.memory_agent import MemoryAgent
from app.utils.storage import Storage

def test_memory_logic():
    agent = MemoryAgent()
    user_id = "test_user_recall"
    conv_id = "test_conv_recall"
    
    # Clean up previous test data
    file_path = Storage._get_conversation_path(user_id, conv_id)
    if file_path.exists():
        os.remove(file_path)
    
    print("--- Phase 1: Identity and Age ---")
    messages = [
        {"role": "user", "content": "My name is Parv."},
        {"role": "assistant", "content": "Nice to meet you Parv."},
        {"role": "user", "content": "I am 22 years old."}
    ]
    for m in messages:
        Storage.append_message(user_id, conv_id, m["role"], m["content"])
    
    # Reload and test recall
    history = Storage.load_conversation(user_id, conv_id)
    slots = agent._extract_slots_from_messages(history)
    print(f"Extracted Slots: {slots}")
    
    # Test recall: name
    recall = agent.detect_memory_recall("What is my name?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: What is my name? -> A: {ans}")
    
    # Test recall: age
    recall = agent.detect_memory_recall("How old am i?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: How old am i? -> A: {ans}")

    print("\n--- Phase 2: Overwrites ---")
    Storage.append_message(user_id, conv_id, "user", "Actually my name is Arjun.")
    history = Storage.load_conversation(user_id, conv_id)
    slots = agent._extract_slots_from_messages(history)
    recall = agent.detect_memory_recall("Who am I?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: Who am I? -> A: {ans}")

    print("\n--- Phase 3: Task-related Memory ---")
    Storage.append_message(user_id, conv_id, "user", "My exam is on Monday.")
    Storage.append_message(user_id, conv_id, "user", "I got AWS Certified certification.")
    history = Storage.load_conversation(user_id, conv_id)
    slots = agent._extract_slots_from_messages(history)
    
    recall = agent.detect_memory_recall("When is my exam?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: When is my exam? -> A: {ans}")
        
    recall = agent.detect_memory_recall("What certificate did I mention?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: What certificate did I mention? -> A: {ans}")

    print("\n--- Phase 4: Generic Memory ---")
    Storage.append_message(user_id, conv_id, "user", "My favorite food is Pizza.")
    history = Storage.load_conversation(user_id, conv_id)
    slots = agent._extract_slots_from_messages(history)
    
    recall = agent.detect_memory_recall("What did I tell you about my favorite food?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: What did I tell you about my favorite food? -> A: {ans}")

    print("\n--- Phase 5: Fuzzy & Multi-turn ---")
    recall = agent.detect_memory_recall("You remember my city right?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: You remember my city right? -> A: {ans}") # Should be "don't have info yet"
    else:
        print("Q: You remember my city right? -> Not detected as recall by current patterns")

    Storage.append_message(user_id, conv_id, "user", "I live in Delhi.")
    history = Storage.load_conversation(user_id, conv_id)
    slots = agent._extract_slots_from_messages(history)
    recall = agent.detect_memory_recall("Where do I live?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: Where do I live? -> A: {ans}")

    print("\n--- Phase 6: Synconyms/Case ---")
    recall = agent.detect_memory_recall("What certification do i have?")
    if recall:
        ans = agent.generate_recall_response(recall["requested_slot"], slots)
        print(f"Q: What certification do i have? -> A: {ans}")

if __name__ == "__main__":
    test_memory_logic()
