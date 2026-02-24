import json
from typing import List, Dict, Any
from .base_agent import BaseAgent
from app.agents.prompts.question_generator_prompt import QUESTION_GENERATOR_PROMPT

class QuestionGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("QuestionGeneratorAgent")

    def run(self, keyword: str, num_questions: int = 3, difficulty: str = "mixed") -> Dict[str, Any]:
        """
        Generates conceptual questions based on a keyword.
        """
        self.logger.info(f"Generating {num_questions} {difficulty} questions for: {keyword}")
        
        prompt = QUESTION_GENERATOR_PROMPT.format(
            keyword=keyword,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        response = self._generate(prompt)
        
        try:
            # Clean response potential extra markdown
            clean_res = response.strip()
            if "```json" in clean_res:
                clean_res = clean_res.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_res:
                clean_res = clean_res.split("```")[1].split("```")[0].strip()
                
            data = json.loads(clean_res)
            
            # Basic validation/fix-up if needed
            if "questions" not in data:
                return {"questions": []}
                
            return data
        except Exception as e:
            self.logger.error(f"Failed to parse question generator output: {e}")
            return {
                "questions": []
            }
