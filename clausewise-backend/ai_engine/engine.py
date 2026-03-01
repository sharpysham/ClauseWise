from ai_engine.segmenter import segment_clauses
from ai_engine.classifier import classify_clause
from ai_engine.entity_extractor import extract_entities
from ai_engine.risk_scorer import compute_risk_score
from ai_engine.explainer import generate_explanation, generate_contradiction_explanation
import json

CONTRADICTION_PAIRS = [
    ("stipend", "unpaid"),
    ("refundable", "non-refundable"),
    ("confidential", "publicly share"),
    ("leave", "not permitted"),
    ("notice", "immediately"),
    ("belongs to the company", "retains complete ownership"),
    ("residential", "office operations"),
    ("5 hours", "all times"),
    ("paid", "unpaid"),
    ("refunded", "retained"),
    ("permitted", "not permitted"),
    ("guaranteed", "not guaranteed"),
]


def get_risk_level(score: float) -> str:
    if score >= 0.6:
        return "HIGH"
    elif score >= 0.35:
        return "MEDIUM"
    else:
        return "LOW"


def find_contradictions(clauses: list) -> list:
    contradicting_pairs = []
    texts = [c["text"].lower() for c in clauses]
    for i, text_a in enumerate(texts):
        for j, text_b in enumerate(texts):
            if i >= j:
                continue
            for keyword_a, keyword_b in CONTRADICTION_PAIRS:
                if keyword_a in text_a and keyword_b in text_b:
                    contradicting_pairs.append((i, j))
                elif keyword_b in text_a and keyword_a in text_b:
                    contradicting_pairs.append((i, j))
    return list(set(contradicting_pairs))


def analyze_contract(contract_text: str) -> dict:
    clauses = segment_clauses(contract_text)
    results = []

    for i, clause_text in enumerate(clauses):
        if not clause_text.strip():
            continue

        classification = classify_clause(clause_text)
        entities = extract_entities(clause_text)
        risk_score = compute_risk_score(
            probability=classification["probability"],
            category=classification["category"]
        )

        results.append({
            "clause_id": i + 1,
            "text": clause_text.strip(),
            "category": classification["category"],
            "probability": round(classification["probability"], 4),
            "confidence": round(classification["confidence"], 4),
            "risk_score": round(risk_score, 4),
            "risk_level": get_risk_level(risk_score),
            "entities": entities,
            "explanation": None,
            "is_contradicting": False,
            "contradiction_with": None,
        })

    # Contradiction detection
    contradiction_pairs = find_contradictions(results)
    flagged = {i for pair in contradiction_pairs for i in pair}

    for idx, result in enumerate(results):
        if idx in flagged:
            partner_idx = None
            for i, j in contradiction_pairs:
                if i == idx:
                    partner_idx = j
                    break
                elif j == idx:
                    partner_idx = i
                    break

            partner_text = results[partner_idx]["text"]
            result["is_contradicting"] = True
            result["contradiction_with"] = results[partner_idx]["clause_id"]
            result["explanation"] = generate_contradiction_explanation(
                clause_a=result["text"],
                clause_b=partner_text
            )
            result["risk_score"] = min(1.0, result["risk_score"] + 0.3)
            result["risk_level"] = get_risk_level(result["risk_score"])
        else:
            result["explanation"] = generate_explanation(
                clause_text=result["text"],
                category=result["category"],
                confidence=result["confidence"],
                entities=result["entities"]
            )

    # Summary
    high_risk = [r for r in results if r["risk_level"] == "HIGH"]
    medium_risk = [r for r in results if r["risk_level"] == "MEDIUM"]
    total_contradictions = len(contradiction_pairs)

    if total_contradictions > 0 and len(high_risk) > 0:
        summary = (
            f"⚠️ This document contains {total_contradictions} contradiction(s) "
            f"and {len(high_risk)} high-risk clause(s). Do NOT sign without legal review."
        )
    elif total_contradictions > 0:
        summary = (
            f"⚠️ This document contains {total_contradictions} contradiction(s). "
            f"Review carefully before signing."
        )
    elif len(high_risk) > 0:
        summary = (
            f"This document has {len(high_risk)} high-risk clause(s) "
            f"and {len(medium_risk)} medium-risk clause(s). Proceed with caution."
        )
    else:
        summary = (
            f"This document appears relatively low risk with "
            f"{len(medium_risk)} medium-risk clause(s). Still review before signing."
        )

    overall_score = (
        round(sum(r["risk_score"] for r in results) / len(results), 4)
        if results else 0.0
    )

    return {
        "total_clauses": len(results),
        "overall_risk_score": overall_score,
        "total_contradictions": total_contradictions,
        "high_risk_count": len(high_risk),
        "medium_risk_count": len(medium_risk),
        "low_risk_count": len(results) - len(high_risk) - len(medium_risk),
        "summary": summary,
        "clauses": results
    }


if __name__ == "__main__":
    sample = """
    The intern shall receive a monthly stipend of 12,000.
    The internship is strictly unpaid and no monetary compensation shall be provided.
    """
    output = analyze_contract(sample)
    print(json.dumps(output, indent=2))