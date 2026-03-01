"""
entity_extractor.py — Extracts structured entities from legal clauses.

Extracts:
  - Money amounts   (e.g. "$5,000", "€200")
  - Durations       (e.g. "30 days", "2 years", "6 months")
  - Percentages     (e.g. "15%", "5 percent")

Uses spaCy NER + simple token-window pattern for durations.
"""

import spacy
import re

try:
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    raise OSError(
        "spaCy model not found. Run: python -m spacy download en_core_web_sm"
    )

# Duration units we care about
_DURATION_UNITS = {"day", "days", "week", "weeks", "month", "months", "year", "years"}

# Percentage pattern
_PERCENT_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\s*(%|percent|per cent)\b", re.IGNORECASE)


def extract_entities(clause_text: str) -> dict:
    """
    Extract structured entities from a clause.

    Args:
        clause_text: Raw clause string.

    Returns:
        {
            "money":       list of str,
            "durations":   list of str,
            "percentages": list of str
        }
    """
    doc = _nlp(clause_text)

    money = []
    durations = []
    percentages = []

    # ── spaCy NER for MONEY and DATE (partial duration signal) ───────────────
    for ent in doc.ents:
        if ent.label_ == "MONEY":
            money.append(ent.text.strip())

    # ── Token-window scan for durations ─────────────────────────────────────
    tokens = [token.text.lower() for token in doc]
    for i, token in enumerate(tokens):
        if token in _DURATION_UNITS and i > 0:
            prev = doc[i - 1]
            # Accept numeric tokens or written numbers like "thirty"
            if prev.like_num or prev.text.lower() in _written_numbers():
                duration_str = f"{doc[i-1].text} {doc[i].text}"
                durations.append(duration_str)

    # ── Regex for percentages ────────────────────────────────────────────────
    for match in _PERCENT_PATTERN.finditer(clause_text):
        percentages.append(match.group(0).strip())

    # Deduplicate while preserving order
    return {
        "money": _dedupe(money),
        "durations": _dedupe(durations),
        "percentages": _dedupe(percentages)
    }


def _dedupe(lst: list) -> list:
    seen = set()
    result = []
    for item in lst:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _written_numbers() -> set:
    """Common English number words."""
    return {
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty",
        "fifty", "sixty", "seventy", "eighty", "ninety", "hundred"
    }
