import json
from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent

class AnswerAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnswerAgent")

    def run(self, questions: List[str], provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Answers a list of questions directly using the LLM service.
        """
        self.logger.info(f"Answering {len(questions)} questions")
        
        results = []
        for q in questions:
            self.logger.info(f"Processing question: {q[:50]}...")
            # Use self._generate to leverage BaseAgent's LLM handling
            answer = self._generate(q)
            results.append({
                "question": q,
                "answer": answer
            })
            
        self.logger.info("Batch answering completed")
        return results
