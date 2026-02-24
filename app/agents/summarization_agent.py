from .base_agent import BaseAgent
from app.agents.prompts.summary_prompt import SUMMARY_PROMPT

class SummarizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummarizationAgent")

    def simple_chat(self, question: str):
        return self._generate(question)

    def run(self, research_output: dict, max_lines=None):
        self.logger.info("✍️ Summarization started")
        content = research_output.get("content", "")

        prompt = f"{SUMMARY_PROMPT}"
        if max_lines:
            prompt += f" in {max_lines} lines"
        prompt += f":\n\n{content}"

        return self._generate(prompt)
