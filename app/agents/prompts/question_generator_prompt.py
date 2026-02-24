QUESTION_GENERATOR_PROMPT = """
You are a JSON-only API.

If you output anything other than valid JSON, the system will crash.

Generate {num_questions} {difficulty} questions for topic: "{keyword}"

STRICT RULES:
1. Output MUST be valid JSON.
2. id must start from 1 and increment.
3. type must be one of: conceptual, analytical, factual.
4. difficulty must match exactly: {difficulty}
5. Ensure total questions = {num_questions}
6. Do NOT add explanations.
7. Do NOT add markdown.
8. Do NOT add text before or after JSON.
9. NO BACKTICKS.

Return ONLY:
{{
  "questions": [
    {{
      "id": integer,
      "type": "conceptual | analytical | factual",
      "difficulty": string,
      "question": string
    }}
  ]
}}

ONLY JSON.
"""
