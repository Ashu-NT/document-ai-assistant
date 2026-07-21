import re

# Pure character/symbol normalization -- deliberately boundary-free. These
# must match regardless of adjacent characters (e.g. a dash inside
# "cost-benefit" or a multiplication sign glued to digits), unlike the
# word-like abbreviations below.
_SYMBOL_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("–", "-"),
    ("—", "-"),
    ("−", "-"),
    ("×", "x"),
    ("…", "..."),
)

_ABBREVIATION_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("part no.", "part number"),
    ("part no", "part number"),
    ("part nr.", "part number"),
    ("part nr", "part number"),
    ("p/n", "part number"),
    ("pn.", "part number"),
    ("pn ", "part number "),

    ("serial no.", "serial number"),
    ("serial no", "serial number"),
    ("serial nr.", "serial number"),
    ("serial nr", "serial number"),
    ("s/no", "serial number"),
    ("s/n", "serial number"),
    ("ser. no.", "serial number"),

    ("order no.", "order number"),
    ("order no", "order number"),
    ("order nr.", "order number"),
    ("order nr", "order number"),
    ("ord. no.", "order number"),

    ("drawing no.", "drawing number"),
    ("drawing no", "drawing number"),
    ("dwg no.", "drawing number"),
    ("dwg no", "drawing number"),
    ("dwg.", "drawing"),

    ("cert. no.", "certificate number"),
    ("cert no.", "certificate number"),
    ("cert no", "certificate number"),
    ("certificate no.", "certificate number"),

    ("rev.", "revision"),
    ("rev no.", "revision number"),
    ("rev no", "revision number"),

    ("tag no.", "tag number"),
    ("tag no", "tag number"),
    ("id no.", "id number"),
    ("id no", "id number"),

    ("nominal dia.", "nominal diameter"),
    ("nominal dia", "nominal diameter"),
    ("dia.", "diameter"),
)

def _compile_abbreviation(source: str, target: str) -> tuple[re.Pattern[str], str]:
    """Anchors the escaped source with a lookaround on whichever edge is a
    word character, so mid-word substring collisions are rejected (e.g.
    "rev." must not match inside "prev.") without also rejecting valid
    matches whose own edge is already punctuation/whitespace (e.g. "pn " in
    "pn 123" -- a trailing space needs no extra lookahead, and adding one
    unconditionally would wrongly require a non-word character after the
    space, i.e. after the next word already started). Unlike a plain `\\b`,
    this works regardless of what the abbreviation itself starts/ends with.
    """
    prefix = r"(?<!\w)" if re.match(r"\w", source[0]) else ""
    suffix = r"(?!\w)" if re.match(r"\w", source[-1]) else ""
    pattern = re.compile(f"{prefix}{re.escape(source)}{suffix}", re.IGNORECASE)
    return pattern, target


# Compiled once at module load, case-insensitive, so capitalized input like
# "Part No." or "PART NO." expands the same as "part no." -- the original
# used a plain case-sensitive str.replace() against these lowercase source
# strings, so capitalized abbreviations silently never expanded.
#
# The symbol group is deliberately left unanchored since those are pure
# character substitutions with no word-like shape (a dash inside
# "cost-benefit" must still normalize). The abbreviation group is anchored
# via `_compile_abbreviation` -- without it, "rev." matches as a bare
# substring inside "prev." ("Check the prev. maintenance date" silently
# became "...prevision...").
_COMPILED_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(re.escape(source), re.IGNORECASE), target)
    for source, target in _SYMBOL_REPLACEMENTS
) + tuple(
    _compile_abbreviation(source, target)
    for source, target in _ABBREVIATION_REPLACEMENTS
)


class RetrievalQueryRewriter:
    def rewrite(
        self,
        query_text: str,
    ) -> str | None:
        rewritten = " ".join((query_text or "").split())
        for pattern, target in _COMPILED_REPLACEMENTS:
            rewritten = pattern.sub(target, rewritten)

        rewritten = " ".join(rewritten.split()).strip()
        if not rewritten or rewritten == query_text:
            return None
        return rewritten
