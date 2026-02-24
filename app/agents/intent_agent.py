import json
from .base_agent import BaseAgent
from app.agents.prompts.intent_prompt import INTENT_PROMPT

class IntentAgent(BaseAgent):
    def __init__(self):
        super().__init__("IntentAgent")

    def run(self, question: str) -> dict:
        self.logger.info(f"Analyzing intent for: {question}")
        
        prompt = INTENT_PROMPT.format(question=question)
        
        response = self._generate(prompt)
        
        try:
            # Robust JSON extraction
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            # Clean up potential control characters
            response = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', response)
                
            blueprint = json.loads(response)
            self.logger.info("Intent blueprint extracted successfully")
            return blueprint
        except Exception as e:
            self.logger.error(f"Failed to parse intent blueprint: {e}")
            # Fallback
            return {
                "task_type": "unknown",
                "decision_question": question,
                "constraints": [],
                "success_criteria": [],
                "reasoning_depth": "medium"
            }
