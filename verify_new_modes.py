import requests
import json

BASE_URL = "http://localhost:8001"

def test_chat_mode():
    print("\n--- Testing Direct Question Mode ---")
    payload = {
        "question": "What is the capital of France?",
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_keyword_mode():
    print("\n--- Testing Keyword Mode ---")
    payload = {
        "keyword": "Artificial Intelligence",
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_evaluation_mode():
    print("\n--- Testing Evaluation Mode ---")
    payload = {
        "evaluate": True,
        "questions": ["What is AI?", "Is earth flat?"],
        "answers": ["AI stands for Artificial Intelligence.", "No, the earth is an oblate spheroid."],
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    try:
        test_chat_mode()
        test_keyword_mode()
        test_evaluation_mode()
    except Exception as e:
        print(f"An error occurred: {e}")
