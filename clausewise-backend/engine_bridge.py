import time

def run_analysis(pages: dict[int, str]) -> dict:
    """
    Bridge to the AI engine.
    Replace the body of this function with your teammate's analyze_contract() call.
    
    pages: {page_number: text_content}
    returns: dict matching the AnalysisResult schema
    """
    
    # TODO: Replace this block when AI engine is ready:
    # from ai_engine.engine import analyze_contract
    # full_text = "\n".join(pages.values())
    # return analyze_contract(full_text)
    
    # ---- MOCK RESPONSE (remove when AI engine is integrated) ----
    return {
        "document_type": "Rental Agreement",
        "overall_risk_score": 6.4,
        "confidence": 0.84,
        "risk_summary": {
            "financial_liability": 7.1,
            "termination_risk": 6.8,
            "restriction_risk": 5.2,
            "data_privacy_risk": 3.9,
            "ambiguity_risk": 4.7
        },
        "flagged_clauses": [
            {
                "page": 1,
                "section_title": "Security Deposit",
                "risk_category": "Financial Liability",
                "risk_score": 8.2,
                "confidence": 0.91,
                "clause_text": pages.get(1, "")[:300],
                "extracted_entities": {
                    "money_amounts": [50000],
                    "durations": ["11 months"],
                    "percentages": []
                },
                "plain_explanation": "A large security deposit is required with conditions for deductions.",
                "worst_case": "You may lose the full deposit amount due to vague deduction clauses.",
                "why_flagged": "High refundable deposit with deduction clauses."
            }
        ],
        "low_confidence_clauses": [],
        "disclaimer": "This tool provides AI-assisted risk insights and is not legal advice."
    }