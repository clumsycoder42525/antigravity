try:
    print("Testing imports...")
    from app.graphs.orchestration_graph import run_graph
    print("orchestration_graph imported successfully")
    from app.api.routes import router
    print("routes imported successfully")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
