from fastapi import APIRouter, HTTPException
from ..schemas.qa_schemas import (
    GenerateQuestionsRequest, GenerateQuestionsResponse,
    AnswerQuestionsRequest, AnswerQuestionsResponse,
    EvaluateQARequest, EvaluateQAResponse
)
from ..agents.question_generator_agent import QuestionGeneratorAgent
from ..agents.answer_agent import AnswerAgent
from ..agents.evaluation_agent import EvaluationAgent
from ..llm_providers.factory import LLMFactory

router = APIRouter()

@router.post("/generate-questions", response_model=GenerateQuestionsResponse, tags=["QA Pipeline"])
def generate_questions(req: GenerateQuestionsRequest):
    agent = QuestionGeneratorAgent()
    llm = LLMFactory.create(provider=req.provider)
    agent.set_llm(llm)
    return agent.run(
        keyword=req.keyword,
        num_questions=req.num_questions,
        difficulty=req.difficulty
    )

@router.post("/answer", response_model=AnswerQuestionsResponse, tags=["QA Pipeline"])
def answer_questions(req: AnswerQuestionsRequest):
    agent = AnswerAgent()
    llm = LLMFactory.create(provider=req.provider)
    agent.set_llm(llm)
    results = agent.run(questions=req.questions, provider=req.provider)
    return {"results": results}

@router.post("/evaluate", response_model=EvaluateQAResponse, tags=["QA Pipeline"])
def evaluate_qa(req: EvaluateQARequest):
    if len(req.questions) != len(req.answers):
        raise HTTPException(status_code=400, detail="Mismatched questions and answers length")
    
    agent = EvaluationAgent()
    # Note: Evaluation doesn't take a provider in the request model, 
    # it will use the default provider configured in settings.
    return agent.run(
        questions=req.questions,
        answers=req.answers,
        strict=req.strict
    )
