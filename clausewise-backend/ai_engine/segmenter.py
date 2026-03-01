"""
segmenter.py — Splits raw contract text into logical clauses using spaCy.

Strategy:
  - Use spaCy's sentence boundary detection.
  - Merge short sentences (< 8 tokens) into the previous clause to avoid
    fragmenting multi-sentence clauses.
  - Strip blank output.
"""

import spacy

# Load once at module level (small English model — fast, good sentence detection)
try:
    _nlp = spacy.load("en_core_web_sm")
except OSError:
    raise OSError(
        "spaCy model not found. Run: python -m spacy download en_core_web_sm"
    )


def segment_clauses(text: str, min_tokens: int = 8) -> list[str]:
    """
    Segment contract text into a list of clause strings.

    Args:
        text:       Raw contract text.
        min_tokens: Sentences shorter than this are merged into the previous clause.

    Returns:
        List of clause text strings.
    """
    doc = _nlp(text)
    raw_sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    clauses = []
    buffer = ""

    for sentence in raw_sentences:
        token_count = len(sentence.split())

        if token_count < min_tokens and buffer:
            # Merge short fragment into previous clause
            buffer += " " + sentence
        else:
            if buffer:
                clauses.append(buffer.strip())
            buffer = sentence

    # Don't forget the last buffer
    if buffer:
        clauses.append(buffer.strip())

    return clauses
