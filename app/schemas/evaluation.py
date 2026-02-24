from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ScoreDetail(BaseModel):
    score: int
    confidence: int
    explanation: str

class RelevanceDetail(BaseModel):
    score: int
    similarity_score: float
    explanation: str

class CompletenessDetail(BaseModel):
    score: int
    coverage_percentage: int
    missing_components: List[str]

class LogicDetail(BaseModel):
    score: int
    contradictions_found: bool
    explanation: str

class ClarityDetail(BaseModel):
    score: int
    readability_score: int
    explanation: str

class EvaluationScores(BaseModel):
    factual_accuracy: ScoreDetail
    relevance: RelevanceDetail
    completeness: CompletenessDetail
    logical_consistency: LogicDetail
    clarity_structure: ClarityDetail

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
    weighted_breakdown: WeightedBreakdown
    overall_feedback: str

class EvaluationRequest(BaseModel):
    question_id: str
    answer_id: str
    original_question: str
    generated_answer: str
    sources: Optional[List[str]] = None
    provider: Optional[str] = None
