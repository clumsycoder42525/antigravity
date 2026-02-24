from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class GenerateQuestionsRequest(BaseModel):
    keyword: str
    num_questions: int = Field(default=3, ge=3, le=5)
    difficulty: Literal["easy", "medium", "hard", "mixed"] = "mixed"
    provider: Optional[Literal["groq", "ollama"]] = "groq"

class QuestionDetail(BaseModel):
    id: int
    type: str
    difficulty: str
    question: str

class GenerateQuestionsResponse(BaseModel):
    questions: List[QuestionDetail]

class AnswerQuestionsRequest(BaseModel):
    questions: List[str]
    provider: Optional[Literal["groq", "ollama"]] = "groq"

class AnswerResult(BaseModel):
    question: str
    answer: str

class AnswerQuestionsResponse(BaseModel):
    results: List[AnswerResult]

class EvaluateQARequest(BaseModel):
    questions: List[str]
    answers: List[str]
    strict: bool = True

class EvaluationDetail(BaseModel):
    question: str
    answer_quality: Literal["good", "partial", "weak"]
    fact_check: Literal["supported", "uncertain", "incorrect"]
    feedback: str

class EvaluateQAResponse(BaseModel):
    evaluation: List[EvaluationDetail]
    overall_score: float
