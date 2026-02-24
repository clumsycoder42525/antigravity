import json
from datetime import datetime
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from .prompts.evaluation_prompt import STRUCTURED_EVALUATION_PROMPT

class StructuredEvaluationAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__("StructuredEvaluationAgent", llm=llm)

    def evaluate(self, 
                 question_id: str, 
                 answer_id: str, 
                 original_question: str, 
                 generated_answer: str, 
                 sources: Optional[list] = None) -> Dict[str, Any]:
        """
        Generates a structured evaluation for a given answer.
        """
        self.logger.info(f"🧐 Evaluating Answer ID: {answer_id}")

        timestamp = datetime.now().isoformat()
        
        prompt = STRUCTURED_EVALUATION_PROMPT.format(
            question_id=question_id,
            answer_id=answer_id,
            original_question=original_question,
            generated_answer=generated_answer,
            sources=json.dumps(sources) if sources else "None Provided",
            timestamp=timestamp
        )

        # Generate response from LLM
        response = self._generate(prompt)
        
        try:
            # Clean response potential extra markdown or text
            clean_res = response.strip()
            # If the LLM still returns markdown, try to extract JSON
            if clean_res.startswith("```json"):
                clean_res = clean_res.split("```json")[1].split("```")[0].strip()
            elif clean_res.startswith("```"):
                clean_res = clean_res.split("```")[1].split("```")[0].strip()
            
            evaluation_data = json.loads(clean_res)
            
            # Recalculate final_score to ensure deterministic behavior based on scoring rules
            # Computing: final_score = (factual_accuracy.score * 0.35) + (relevance.score * 0.30) + 
            # (completeness.score * 0.20) + (logical_consistency.score * 0.15)
            
            scores = evaluation_data.get("scores", {})
            f_acc = scores.get("factual_accuracy", {}).get("score", 0)
            rel = scores.get("relevance", {}).get("score", 0)
            comp = scores.get("completeness", {}).get("score", 0)
            log_con = scores.get("logical_consistency", {}).get("score", 0)
            
            weighted_score = (
                (f_acc * 0.35) +
                (rel * 0.30) +
                (comp * 0.20) +
                (log_con * 0.15)
            )
            
            evaluation_data["final_score"] = round(weighted_score, 2)
            
            return evaluation_data

        except Exception as e:
            self.logger.error(f"❌ Failed to parse evaluation JSON: {e}")
            self.logger.error(f"Raw response: {response}")
            return {
                "error": "Failed to generate valid evaluation JSON",
                "details": str(e),
                "status": "failure"
            }
