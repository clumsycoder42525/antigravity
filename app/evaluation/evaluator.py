import json
import re
import math
from datetime import datetime
from typing import Optional, Dict, Any, List
from .schema import (
    EvaluationRequest, 
    EvaluationResponse, 
    EvaluationScores, 
    WeightedBreakdown,
    FactualAccuracy,
    Relevance,
    Completeness,
    LogicalConsistency,
    ClarityStructure
)
from .scoring_rules import calculate_weighted_score
from ..rag.embedder import Embedder

class Evaluator:
    def __init__(self, provider: Optional[str] = None):
        self.embedder = Embedder()

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        if not magnitude1 or not magnitude2:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def _get_tokens(self, text: str) -> set:
        return set(re.findall(r'\w+', text.lower()))

    def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Orchestrates the deterministic evaluation process.
        """
        # 1. Factual Accuracy (Source Overlap)
        answer_tokens = self._get_tokens(request.generated_answer)
        source_text = " ".join(request.sources) if request.sources else ""
        source_tokens = self._get_tokens(source_text)
        
        factual_score = 0.0
        confidence = 0.0
        if source_tokens:
            intersection = answer_tokens.intersection(source_tokens)
            factual_score = len(intersection) / len(answer_tokens) if answer_tokens else 0.0
            confidence = 1.0 # Deterministic based on overlap
        else:
            factual_score = 0.5 # Neutral if no sources
            confidence = 0.3 # Low confidence
            
        factual_acc = FactualAccuracy(
            score=round(factual_score, 4),
            confidence=round(confidence, 4),
            explanation=f"Based on {len(answer_tokens)} tokens in answer and {len(source_tokens)} in sources."
        )

        # 2. Relevance (Embedding Similarity)
        q_emb = self.embedder.embed_query(request.original_question)
        a_emb = self.embedder.embed_query(request.generated_answer)
        similarity = self._cosine_similarity(q_emb, a_emb)
        
        relevance = Relevance(
            score=round(similarity, 4),
            similarity_score=round(similarity, 4),
            explanation="Cosine similarity between question and answer embeddings."
        )

        # 3. Completeness (Keyword Coverage)
        question_tokens = self._get_tokens(request.original_question)
        # Filters tokens to ignore common stop words if needed, but keeping it simple
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of', 'and', 'what', 'how', 'where', 'when', 'who'}
        keywords = question_tokens - stop_words
        
        covered = answer_tokens.intersection(keywords)
        coverage = len(covered) / len(keywords) if keywords else 1.0
        
        completeness = Completeness(
            score=round(coverage, 4),
            coverage_percentage=round(coverage * 100, 2),
            missing_components=list(keywords - covered)[:5]
        )

        # 4. Logical Consistency (Heuristic)
        # Check for obvious self-contradictions like "Yes, but no" or "However, it is not"
        contradiction_patterns = [r'\byes\b.*\bno\b', r'\bnot\b.*\bbut\b', r'\bhowever\b.*\bnot\b']
        contradictions_found = any(re.search(p, request.generated_answer.lower()) for p in contradiction_patterns)
        logical_score = 0.5 if contradictions_found else 1.0
        
        logical_consistency = LogicalConsistency(
            score=logical_score,
            contradictions_found=contradictions_found,
            explanation="Checked for simple linguistic contradiction patterns."
        )

        # 5. Clarity & Structure (Readability)
        sentences = list(filter(None, re.split(r'[.!?]+', request.generated_answer)))
        avg_sentence_len = len(answer_tokens) / len(sentences) if sentences else 0
        # Simple readability: shorter sentences are often clearer in technical contexts
        readability = max(0, min(1, 1 - (avg_sentence_len - 15) / 30)) if avg_sentence_len > 15 else 1.0
        
        clarity_structure = ClarityStructure(
            score=round(readability, 4),
            readability_score=round(readability * 100, 2),
            explanation=f"Avg sentence length: {round(avg_sentence_len, 2)} tokens."
        )

        scores = EvaluationScores(
            factual_accuracy=factual_acc,
            relevance=relevance,
            completeness=completeness,
            logical_consistency=logical_consistency,
            clarity_structure=clarity_structure
        )

        weights = WeightedBreakdown()
        final_score = calculate_weighted_score(scores, weights)

        return EvaluationResponse(
            question_id=request.question_id,
            answer_id=request.answer_id,
            evaluation_timestamp=datetime.now().isoformat(),
            scores=scores,
            final_score=final_score,
            weighted_breakdown=weights,
            overall_feedback="Deterministic evaluation based on text overlap and embeddings."
        )
