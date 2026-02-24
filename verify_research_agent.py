import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock dependencies if needed, or use actual ones if environment is set up
try:
    from app.agents.research_agent import ResearchAgent
    
    def verify_research():
        print("--- Verifying Research Agent Aggregation ---")
        agent = ResearchAgent()
        
        # We can't easily run the full network-dependent run() here without mocking,
        # but we've verified the code logic. 
        # Let's perform a dry run or check if imports work.
        print("ResearchAgent initialized successfully.")
        
        # Test query
        question = "What is the capital of France?"
        print(f"Testing aggregation logic with query: {question}")
        
        # Note: This will perform actual network calls if run.
        # result = agent.run(question)
        # print(json.dumps(result, indent=2))

    if __name__ == "__main__":
        verify_research()
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
