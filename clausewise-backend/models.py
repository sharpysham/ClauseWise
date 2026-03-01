from pydantic import BaseModel
from typing import List, Dict, Optional

class ExtractedEntities(BaseModel):
    money_amounts: List[float] = []
    durations: List[str] = []
    percentages: List[float] = []

class FlaggedClause(BaseModel):
    page: int
    section_title: str
    risk_category: str
    risk_score: float
    confidence: float
    clause_text: str
    extracted_entities: ExtractedEntities
    plain_explanation: str
    worst_case: str
    why_flagged: str

class RiskSummary(BaseModel):
    financial_liability: float
    termination_risk: float
    restriction_risk: float
    data_privacy_risk: float
    ambiguity_risk: float

class AnalysisResult(BaseModel):
    document_type: str
    overall_risk_score: float
    confidence: float
    processing_time_ms: float
    risk_summary: RiskSummary
    flagged_clauses: List[FlaggedClause]
    low_confidence_clauses: List[FlaggedClause] = []
    disclaimer: str