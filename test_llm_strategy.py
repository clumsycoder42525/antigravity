import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

print("Testing LLM Provider Strategy...")
print("=" * 60)

from app.services.llm_service import llm_service

# Check configuration
print(f"\n1. Configuration Check:")
print(f"   GROQ_API_KEY set: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"   Groq client initialized: {bool(llm_service.groq_client)}")
print(f"   Default model: {llm_service.groq_model}")

# Test generation
print(f"\n2. Testing LLM Generation:")
test_prompt = "What is 2+2? Answer in one short sentence."

try:
    result = llm_service.generate_response(test_prompt)
    print(f"   Status: {result.get('status')}")
    print(f"   Model: {result.get('model')}")
    print(f"   Response: {result.get('content', result.get('error'))[:100]}...")
    
    if result.get('status') == 'success':
        print("\n✅ LLM service working correctly!")
    else:
        print(f"\n❌ LLM service failed: {result.get('error')}")
        print(f"   Details: {result.get('details')}")
except Exception as e:
    print(f"\n❌ Test failed with exception: {e}")
    import traceback
    traceback.print_exc()
