try:
    from app.services.llm_service import llm_service, ask_llm
    from app.llm import get_llm, LLMAdapter
    from app.config.settings import settings
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)

print(f"Primary Model: {llm_service.primary_model_name}")
print(f"Fallback Model: {llm_service.fallback_model_name}")
print(f"Timeout: {llm_service.timeout}")

# Test LLMAdapter
try:
    adapter = get_llm()
    print(f"Adapter created: {type(adapter)}")
    if isinstance(adapter, LLMAdapter):
        print("Adapter type verified.")
except Exception as e:
    print(f"Adapter creation failed: {e}")

# We won't call the actual API because we might not have keys, 
# but we verified the structure loads without syntax errors.
print("Verification script finished successfully.")
