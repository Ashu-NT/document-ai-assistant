from src.application.workflows.parsing.builders.chunking.policies.profile.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking.policies.profile.features.structural_document_features import (
    StructuralDocumentFeatures,
)


class DatasheetScorer:
    profile = ChunkingProfile.DATASHEET

    def score(self, features: StructuralDocumentFeatures) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []
        datasheet_evidence = features.evidence[ChunkingProfile.DATASHEET]

        if datasheet_evidence.total_occurrences > 0:
            score += min(5.0, datasheet_evidence.total_occurrences * 1.7)
            reasons.append(
                f"Datasheet/specification markers found in title/sections ({datasheet_evidence.total_occurrences} hits)."
            )

        if features.table_ratio >= 0.22:
            score += 2.5
            reasons.append(
                f"Tables are dominant (ratio {features.table_ratio:.2f})."
            )
        elif features.table_ratio >= 0.12:
            score += 1.2
            reasons.append(
                f"Tables are a notable structural signal (ratio {features.table_ratio:.2f})."
            )

        if features.short_text_ratio >= 0.35:
            score += 1.2
            reasons.append(
                f"Text blocks are short and spec-like (short-text ratio {features.short_text_ratio:.2f})."
            )

        if 0 < features.avg_text_tokens <= 14:
            score += 0.9
            reasons.append(
                f"Average text blocks are concise ({features.avg_text_tokens:.1f} tokens)."
            )

        if features.max_section_depth <= 2 and features.root_section_count >= features.nested_section_count:
            score += 0.6
            reasons.append(
                "Section structure is shallow, which fits specification-style documents."
            )

        manual_evidence = features.evidence[ChunkingProfile.MANUAL]
        if manual_evidence.total_occurrences >= 3 or features.procedure_like_section_count >= 2:
            score -= 2.0
            reasons.append(
                "Strong manual/procedure signals reduce datasheet confidence."
            )

        if features.long_text_ratio >= 0.35:
            score -= 1.0
            reasons.append(
                "Long narrative text is less typical for a datasheet."
            )

        return score, reasons
