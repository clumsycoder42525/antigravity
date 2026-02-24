import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.llm_providers.ollama_provider import OllamaLLM

async def verify_ollama():
    print("--- Verifying Ollama Provider ---")
    provider = OllamaLLM()
    
    print("\n1. Testing Health Check...")
    health = provider.health_check()
    print(f"Health Check Result: {health}")
    
    print("\n2. Testing Generation (Non-blocking)...")
    try:
        # This will likely fail if Ollama isn't running, which is fine for testing error handling
        response = provider.generate("Respond only with 'OK'")
        print(f"Generation Result: {response}")
    except Exception as e:
        print(f"Generation caught unexpected exception: {e}")

if __name__ == "__main__":
    asyncio.run(verify_ollama())
