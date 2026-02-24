from .schema import EvaluationScores, WeightedBreakdown

def calculate_weighted_score(scores: EvaluationScores, weights: WeightedBreakdown) -> float:
    """
    Calculates the final weighted score based on individual component scores.
    Formula: (factual * 0.35) + (relevance * 0.30) + (completeness * 0.20) + (logical * 0.15)
    """
    # Apply hallucination penalty to factual accuracy if confidence is low
    factual_score = scores.factual_accuracy.score
    if scores.factual_accuracy.confidence < 0.5:
        factual_score *= 0.5
        
    final_score = (
        (factual_score * weights.factual_accuracy_weight) +
        (scores.relevance.score * weights.relevance_weight) +
        (scores.completeness.score * weights.completeness_weight) +
        (scores.logical_consistency.score * weights.logical_consistency_weight)
    )
    return round(final_score, 4)
