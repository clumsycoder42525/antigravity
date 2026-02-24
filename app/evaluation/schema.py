from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ScoreDetail(BaseModel):
    score: float
    explanation: str

class FactualAccuracy(ScoreDetail):
    confidence: float

class Relevance(ScoreDetail):
    similarity_score: float

class Completeness(BaseModel):
    score: float
    coverage_percentage: float
    missing_components: List[str] = []

class LogicalConsistency(BaseModel):
    score: float
    contradictions_found: bool = False
    explanation: str

class ClarityStructure(ScoreDetail):
    readability_score: float

class EvaluationScores(BaseModel):
    factual_accuracy: FactualAccuracy
    relevance: Relevance
    completeness: Completeness
    logical_consistency: LogicalConsistency
    clarity_structure: ClarityStructure

class WeightedBreakdown(BaseModel):
    factual_accuracy_weight: float = 0.35
    relevance_weight: float = 0.30
    completeness_weight: float = 0.20
    logical_consistency_weight: float = 0.15

class EvaluationResponse(BaseModel):
    question_id: str
    answer_id: str
    evaluation_timestamp: str
    scores: EvaluationScores
    final_score: float
    weighted_breakdown: WeightedBreakdown = WeightedBreakdown()
    overall_feedback: str

class EvaluationRequest(BaseModel):
    question_id: str
    answer_id: str
    original_question: str
    generated_answer: str
    sources: Optional[List[str]] = None
    provider: Optional[str] = None
