import json
from typing import List, Dict, Any
from .base_agent import BaseAgent
from app.agents.prompts.evaluation_prompt import EVALUATION_PROMPT

class EvaluationAgent(BaseAgent):
    def __init__(self):
        super().__init__("EvaluationAgent")

    def run(self, questions: List[str], answers: List[str], strict: bool = True) -> Dict[str, Any]:
        """
        Evaluates question-answer pairs.
        """
        if len(questions) != len(answers):
            self.logger.error("Mismatched questions and answers length")
            return {
                "error": "Mismatched questions and answers length",
                "evaluation": [],
                "overall_score": 0
            }

        self.logger.info(f"Evaluating {len(questions)} pairs | strict={strict}")
        
        prompt = EVALUATION_PROMPT.format(
            questions=json.dumps(questions),
            answers=json.dumps(answers),
            strict=strict
        )
        
        response = self._generate(prompt)
        
        try:
            # Clean response potential extra markdown
            clean_res = response.strip()
            if "```json" in clean_res:
                clean_res = clean_res.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_res:
                clean_res = clean_res.split("```")[1].split("```")[0].strip()
                
            return json.loads(clean_res)
        except Exception as e:
            self.logger.error(f"Failed to parse evaluation output: {e}")
            return {
                "evaluation": [],
                "overall_score": 0,
                "error": str(e)
            }
