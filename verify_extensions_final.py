import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
USER_ID = "test_user_v3"
CONV_ID = "test_conv_v2"

def test_evaluation():
    print("\n--- Testing Evaluation ---")
    payload = {
        "question_id": "q1",
        "answer_id": "a1",
        "original_question": "What is the capital of France?",
        "generated_answer": "The capital of France is Paris. It is a beautiful city.",
        "sources": ["France's capital city is Paris."],
        "provider": "groq"
    }
    res = requests.post(f"{BASE_URL}/evaluation", json=payload)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

def test_memory():
    print("\n--- Testing Memory Update ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "My favorite color is blue."
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Update Status: {res.status_code}")
    
    print("\n--- Testing Memory Recall ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "What is my favorite color?"
    }
    res = requests.post(f"{BASE_URL}/chat/memory", json=payload)
    print(f"Recall Status: {res.status_code}")
    print(json.dumps(res.json().get("decision_output", {}), indent=2))

def test_ticket_booking():
    print("\n--- Testing Ticket Booking (Turn 1) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "I want to book a flight from London."
    }
    res = requests.post(f"{BASE_URL}/agent/ticket", json=payload)
    print(f"Turn 1 Status: {res.status_code}")
    print(res.json().get("message"))
    
    print("\n--- Testing Ticket Booking (Turn 2) ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "To Paris"
    }
    res = requests.post(f"{BASE_URL}/agent/ticket", json=payload)
    print(f"Turn 2 Status: {res.status_code}")
    print(res.json().get("message"))

    print("\n--- Testing Ticket Recall ---")
    payload = {
        "user_id": USER_ID,
        "conversation_id": CONV_ID,
        "question": "What ticket did I book?"
    }
    res = requests.post(f"{BASE_URL}/agent/ticket", json=payload)
    print(f"Recall Status: {res.status_code}")
    print(res.json().get("message"))

if __name__ == "__main__":
    try:
        test_evaluation()
        test_memory()
        test_ticket_booking()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the server is running on http://127.0.0.1:8000")
