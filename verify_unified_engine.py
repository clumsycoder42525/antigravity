import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
USER_ID = "arch_user_v1"
CONV_ID = "arch_conv_v1"

def test_unified_flow():
    print("\n--- Turn 1: Memory Update (Identity) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "My name is Alice and I am a software engineer."
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json().get('decision_output', {}).get('answer')}")
    time.sleep(2)

    print("\n--- Turn 2: Task Start (Booking) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "I want to book a flight from Berlin."
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json().get('decision_output', {}).get('answer')}")
    time.sleep(2)

    print("\n--- Turn 3: Memory Recall (Natural) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "What is my job?"
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json().get('decision_output', {}).get('answer')}")
    time.sleep(2)

    print("\n--- Turn 4: Task Continue ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "To Tokyo"
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json().get('decision_output', {}).get('answer')}")
    time.sleep(2)

    print("\n--- Turn 5: General Chat (Context Injection) ---")
    # This should trigger summarization as it's the 5th message
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "Thinking about my trip, what should I pack?"
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    # Answer should ideally refer to Alice/Tokyo
    print(f"Response: {res.json().get('decision_output', {}).get('answer')}")

    print("\n--- Turn 6: Task Summary (Special Question) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "What am I booking?"
    }
    # This might be routed as recall or chat depending on how router sees it
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json().get('decision_output', {}).get('answer')}")

if __name__ == "__main__":
    test_unified_flow()
