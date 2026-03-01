"""
classifier.py — Zero-shot semantic classification of legal clauses.

Model: facebook/bart-large-mnli  (zero-shot, no training needed)
Output: category label + probability + confidence score
"""

from transformers import pipeline
import torch

# ── Risk categories ──────────────────────────────────────────────────────────
RISK_CATEGORIES = [
    "Financial Liability",
    "Termination Risk",
    "Restriction of Rights",
    "Data Privacy Risk",
    "Auto-Renewal",
    "Ambiguity Risk",
]

# ── Load pipeline once ───────────────────────────────────────────────────────
# Uses CPU by default. If you have a GPU, change device=0
_classifier = pipeline(
    task="zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=-1,  # -1 = CPU. Change to 0 for GPU.
)


def classify_clause(clause_text: str) -> dict:
    """
    Classify a single clause into a risk category.

    Args:
        clause_text: The raw text of one legal clause.

    Returns:
        {
            "category":    str,   # top predicted risk category
            "probability": float, # score of the top label
            "confidence":  float, # gap between top and second label (reliability signal)
            "all_scores":  dict   # all categories and their scores
        }
    """
    if not clause_text.strip():
        return {
            "category": "Ambiguity Risk",
            "probability": 0.0,
            "confidence": 0.0,
            "all_scores": {}
        }

    result = _classifier(
        clause_text,
        candidate_labels=RISK_CATEGORIES,
        hypothesis_template="This clause is related to {}."
    )

    labels = result["labels"]
    scores = result["scores"]

    top_label = labels[0]
    top_score = scores[0]
    second_score = scores[1] if len(scores) > 1 else 0.0

    # Confidence = gap between top score and runner-up (higher = more certain)
    confidence = top_score - second_score

    return {
        "category": top_label,
        "probability": top_score,
        "confidence": confidence,
        "all_scores": dict(zip(labels, scores))
    }
