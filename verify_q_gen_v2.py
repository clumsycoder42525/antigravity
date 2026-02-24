import requests
import json

BASE_URL = "http://localhost:8002"

def test_generate_questions_v2():
    print("\n--- Testing /generate-questions (New Schema) ---")
    payload = {
        "keyword": "Quantum Computing",
        "num_questions": 3,
        "difficulty": "hard",
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/generate-questions", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_generate_questions_v2()
