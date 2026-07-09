import re

_RAW_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("–", "-"),
    ("—", "-"),
    ("−", "-"),
    ("×", "x"),
    ("…", "..."),

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

# Compiled once at module load, case-insensitive, so capitalized input like
# "Part No." or "PART NO." expands the same as "part no." -- the original
# used a plain case-sensitive str.replace() against these lowercase source
# strings, so capitalized abbreviations silently never expanded.
_COMPILED_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(re.escape(source), re.IGNORECASE), target)
    for source, target in _RAW_REPLACEMENTS
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
