import json
from typing import Any, Optional
from .base_agent import BaseAgent
from app.agents.prompts.reasoning_prompt import REASONING_PROMPT

class ReasoningAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReasoningAgent")

    def run(self, intent_blueprint: dict, research_data: Optional[dict] = None) -> dict:
        self.logger.info(f"Expanding reasoning for: {intent_blueprint.get('decision_question')}")
        
        research_context = ""
        if research_data:
            research_context = f"""
RESEARCH INSIGHTS:
{research_data.get('key_insights', [])}

MARKET SIGNALS:
{research_data.get('market_signals', [])}

SUPPORTING EVIDENCE:
{research_data.get('supporting_evidence', [])}
"""

        prompt = REASONING_PROMPT.format(
            intent_blueprint=json.dumps(intent_blueprint, indent=2),
            research_context=research_context
        )
        
        response = self._generate(prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            # Clean up potential control characters
            response = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', response)
                
            reasoning_map = json.loads(response)
            self.logger.info("Reasoning map generated successfully")
            return reasoning_map
        except Exception as e:
            self.logger.error(f"Failed to parse reasoning map: {e}")
            return {
                "sub_questions": [],
                "assumptions": [],
                "risks": [],
                "decision_map": response # Return raw text if JSON fails
            }
