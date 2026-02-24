import requests
import json

BASE_URL = "http://localhost:8000"

def test_structured_evaluation():
    print("\n--- Testing /evaluation ---")
    payload = {
        "question_id": "Q-101",
        "answer_id": "A-202",
        "original_question": "What are the primary benefits of using a vector database for RAG?",
        "generated_answer": "Vector databases allow for efficient similarity search of high-dimensional embeddings. They enable retrieving relevant context for LLMs, which reduces hallucinations and improves response accuracy by grounding the model in specific data.",
        "sources": ["ChromaDB Documentation", "Pinecone Blog on RAG"],
        "provider": "groq"
    }
    
    response = requests.post(f"{BASE_URL}/evaluation", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Verify schema
        required_keys = ["question_id", "answer_id", "evaluation_timestamp", "scores", "final_score", "weighted_breakdown", "overall_feedback"]
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing key: {key}")
            else:
                print(f"✅ Found key: {key}")
                
        # Verify weighted score calculation
        scores = data["scores"]
        f_acc = scores["factual_accuracy"]["score"]
        rel = scores["relevance"]["score"]
        comp = scores["completeness"]["score"]
        log_con = scores["logical_consistency"]["score"]
        
        expected_score = round((f_acc * 0.35) + (rel * 0.30) + (comp * 0.20) + (log_con * 0.15), 2)
        actual_score = data["final_score"]
        
        if expected_score == actual_score:
            print(f"✅ Score calculation matches: {actual_score}")
        else:
            print(f"❌ Score mismatch! Expected: {expected_score}, Got: {actual_score}")
    else:
        print(f"❌ Failed: {response.text}")

def test_chat_untouched():
    print("\n--- Testing /chat (Untouched) ---")
    payload = {
        "question": "What is 2+2?",
        "provider": "groq"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Keys: {list(data.keys())}")
        if "content" in data and "mode" in data:
            print("✅ /chat response format remains correct.")
        else:
            print("❌ /chat response format changed!")

if __name__ == "__main__":
    test_structured_evaluation()
    test_chat_untouched()
