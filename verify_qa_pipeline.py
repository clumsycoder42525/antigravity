import requests
import json

BASE_URL = "http://localhost:8001"

def test_generate_questions():
    print("\n--- Testing /generate-questions ---")
    payload = {
        "keyword": "Artificial Intelligence",
        "num_questions": 3,
        "difficulty": "medium",
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/generate-questions", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_answer():
    print("\n--- Testing /answer ---")
    payload = {
        "questions": [
            "What is Artificial Intelligence?",
            "How does machine learning differ from deep learning?"
        ],
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/answer", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_evaluate():
    print("\n--- Testing /evaluate ---")
    payload = {
        "questions": ["Is the earth flat?"],
        "answers": ["No, the earth is an oblate spheroid."],
        "strict": True
    }
    response = requests.post(f"{BASE_URL}/evaluate", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_chat_untouched():
    print("\n--- Testing /chat (Untouched) ---")
    payload = {
        "question": "What is the capital of France?",
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    # Verify it still has the expected keys for /chat
    data = response.json()
    print(f"Keys: {list(data.keys())}")
    print(f"Mode: {data.get('mode')}")

if __name__ == "__main__":
    test_generate_questions()
    test_answer()
    test_evaluate()
    test_chat_untouched()
