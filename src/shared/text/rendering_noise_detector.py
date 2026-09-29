from __future__ import annotations

# Conservative by design: a chunk is only "rendering-only noise" if
# literally no character in it is alphanumeric. `str.isalnum()` is
# Unicode-aware (a CJK ideograph, an accented Latin letter, etc. all count
# as alphanumeric) - deliberately NOT the ASCII-only `[a-z0-9]` pattern
# `alnum_tokenizer.tokenize_alnum` uses for normalized-key matching
# elsewhere, which would misclassify genuine non-Latin-script content
# (verified against a real corpus document: a single stray CJK character
# chunk) as noise. Real technical content always contains at least one
# alphanumeric character (a model code, a unit, a measurement, an ordinary
# word in any script), even when it also contains pipes/hyphens/colons
# (e.g. "DN25 | PN16 | 80 C", "TCR12-43063", "pressure-temperature"). Only
# pure table-rendering syntax ("| --- | --- |", "----|----", "|-----|-----|")
# or pure whitespace has no alphanumeric character at all.
#
# Blank/whitespace-only text is deliberately NOT classified as noise here -
# that is the existing `no_empty_chunks` invariant's concern, not this
# one's, so the two never double-count the same defect.


def is_rendering_only_noise(text: str | None) -> bool:
    if not text or not text.strip():
        return False
    return not any(character.isalnum() for character in text)


__all__ = ["is_rendering_only_noise"]
