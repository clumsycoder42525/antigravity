import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.llm_providers.factory import LLMFactory
from app.config.settings import settings
from app.services.llm_service import llm_service

def test_factory():
    print("Testing LLMFactory...")
    
    # Test Groq (default)
    groq_llm = LLMFactory.create(provider="groq")
    print(f"Created Groq LLM: {type(groq_llm)}")
    
    # Test Ollama
    ollama_llm = LLMFactory.create(provider="ollama")
    print(f"Created Ollama LLM: {type(ollama_llm)}")
    
    # Test invalid fallback
    fallback_llm = LLMFactory.create(provider="invalid")
    print(f"Created Fallback LLM: {type(fallback_llm)}")

def test_service_backward_compatibility():
    print("\nTesting LLMService backward compatibility...")
    response = llm_service.generate_response("Hello")
    print(f"Service Response Status: {response.get('status')}")
    print(f"Service Response Model: {response.get('model')}")

def test_health_checks():
    print("\nTesting Health Checks...")
    groq_llm = LLMFactory.create(provider="groq")
    print(f"Groq Health: {groq_llm.health_check()}")
    
    ollama_llm = LLMFactory.create(provider="ollama")
    print(f"Ollama Health (likely False if not running): {ollama_llm.health_check()}")

if __name__ == "__main__":
    try:
        test_factory()
        test_service_backward_compatibility()
        test_health_checks()
        print("\n✅ Verification script completed successfully!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
