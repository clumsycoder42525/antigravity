import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
USER_ID = "det_user_v1"
CONV_ID = "det_conv_v1"

def test_deterministic_logic():
    print("\n--- Test 1: Identity Extraction ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "My name is Parv Gaur and I live in Delhi. I am 21 years old."
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Answer: {res.json().get('decision_output', {}).get('answer')}")
    # Should ack name, Delhi, 21.
    
    time.sleep(1)

    print("\n--- Test 2: Memory Recall (Multi-key) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "What is my name and where do I live?"
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Answer: {res.json().get('decision_output', {}).get('answer')}")
    # Should return Parv Gaur and Delhi.

    time.sleep(1)

    print("\n--- Test 3: Task Start (Booking) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "I want to book a flight from Delhi to Mumbai."
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Answer: {res.json().get('decision_output', {}).get('answer')}")
    # Should start booking flight.

    time.sleep(1)

    print("\n--- Test 4: Task Status ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "What am I booking?"
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Answer: {res.json().get('decision_output', {}).get('answer')}")
    # Should summarize the flight details.

if __name__ == "__main__":
    test_deterministic_logic()
