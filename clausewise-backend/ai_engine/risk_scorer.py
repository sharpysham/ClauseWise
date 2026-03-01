"""
risk_scorer.py — Computes composite risk score for a classified clause.

Formula:
    risk_score = classification_probability × severity_multiplier

Severity multipliers are hand-tuned based on legal risk domain knowledge.
Range: 0.0 – 1.0 (higher = riskier)
"""

# Severity multipliers per risk category (tune these for your domain)
SEVERITY_MULTIPLIERS = {
    "Financial Liability":   1.0,   # Highest — direct monetary exposure
    "Termination Risk":      0.85,  # High — can end the agreement unilaterally
    "Restriction of Rights": 0.80,  # High — limits freedom of action
    "Data Privacy Risk":     0.75,  # High — legal / regulatory exposure
    "Auto-Renewal":          0.60,  # Medium — often overlooked, financial impact
    "Ambiguity Risk":        0.50,  # Medium — uncertainty introduces legal risk
}

# Default if category not found
_DEFAULT_MULTIPLIER = 0.5


def compute_risk_score(probability: float, category: str) -> float:
    """
    Compute a composite risk score for a clause.

    Args:
        probability: Classification confidence (0.0 – 1.0).
        category:    Predicted risk category string.

    Returns:
        risk_score (float, 0.0 – 1.0)
    """
    multiplier = SEVERITY_MULTIPLIERS.get(category, _DEFAULT_MULTIPLIER)
    score = probability * multiplier

    # Clamp to [0.0, 1.0] just in case
    return max(0.0, min(1.0, score))
