from enum import StrEnum


class ViolationType(StrEnum):
    UNRELATED_QUERY = "unrelated_query"
    AMBIGUOUS_QUERY = "ambiguous_query"
    NO_EVIDENCE = "no_evidence"
    WEAK_EVIDENCE = "weak_evidence"
    IDENTIFIER_NOT_FOUND = "identifier_not_found"
    LOW_CONFIDENCE_SCORE = "low_confidence_score"
    IRRELEVANT_CHUNKS = "irrelevant_chunks"
    TOC_CHUNK = "toc_chunk"
    BRANDING_CHUNK = "branding_chunk"
    NOISE_CHUNK = "noise_chunk"
    MISSING_CITATION = "missing_citation"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    SAFETY_CONTENT = "safety_content"
