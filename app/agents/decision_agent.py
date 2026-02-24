import json
from .base_agent import BaseAgent
from app.agents.prompts.decision_prompt import DECISION_PROMPT

class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("DecisionAgent")

    def run(self, reasoning_map: dict) -> dict:
        self.logger.info("Synthesizing final decision")
        
        prompt = DECISION_PROMPT.format(
            reasoning_map=json.dumps(reasoning_map, indent=2)
        )
        
        response = self._generate(prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
                
            # Clean up potential control characters
            response = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', response)

            decision = json.loads(response)
            self.logger.info("Decision synthesis completed successfully")
            return decision
        except Exception as e:
            self.logger.error(f"Failed to parse decision synthesis: {e}")
            return {
                "executive_summary": "Error parsing LLM response",
                "final_recommendation": "Manual review required",
                "key_rationale": [response],
                "major_risks": ["Parsing failure"],
                "assumptions_made": [],
                "next_steps": ["Retry with normalized input"]
            }
