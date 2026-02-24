from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..evaluation.schema import EvaluationRequest, EvaluationResponse
from ..evaluation.evaluator import Evaluator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/evaluation", response_model=EvaluationResponse, tags=["Evaluation"])
def evaluate_answer(req: EvaluationRequest):
    """
    Evaluates a generated answer using the deterministic scoring engine.
    STRICT JSON only.
    """
    try:
        evaluator = Evaluator(provider=req.provider)
        result = evaluator.evaluate(req)
        # return EvaluationResponse directly for automatic JSON serialization
        return result

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Evaluation engine error", "details": str(e)}
        )
