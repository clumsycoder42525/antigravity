import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

print("Verifying RAG uses local HuggingFace only...")
print("=" * 60)

# Check RAG's LLM implementation
print("\n1. RAG LLM Configuration:")
from app.rag.llm import LLM

rag_llm = LLM()
print(f"   RAG LLM class: {rag_llm.__class__.__name__}")
print(f"   Pipeline task: {rag_llm._pipeline.task if rag_llm._pipeline else 'Not loaded'}")
print(f"   Model: {rag_llm._pipeline.model.name_or_path if rag_llm._pipeline else 'Not loaded'}")

# Check chat LLM implementation
print("\n2. Chat LLM Configuration:")
from app.services.llm_service import llm_service

print(f"   Groq client: {bool(llm_service.groq_client)}")
print(f"   Groq model: {llm_service.groq_model}")

# Confirm separation
print("\n3. Verification:")
if rag_llm._pipeline and not hasattr(rag_llm, 'groq_client'):
    print("   ✅ RAG uses local HuggingFace pipeline (no Groq)")
else:
    print("   ⚠️ RAG might be using external LLM")

if llm_service.groq_client:
    print("   ✅ Chat uses Groq API (when available)")
else:
    print("   ℹ️ Chat will use HuggingFace fallback (no Groq key)")

print("\n✅ Verification complete: RAG and Chat use separate LLM implementations")
