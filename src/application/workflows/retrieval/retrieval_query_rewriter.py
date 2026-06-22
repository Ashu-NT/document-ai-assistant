class RetrievalQueryRewriter:
    _REPLACEMENTS = (
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

    def rewrite(
        self,
        query_text: str,
    ) -> str | None:
        rewritten = " ".join((query_text or "").split())
        for source, target in self._REPLACEMENTS:
            rewritten = rewritten.replace(source, target)

        rewritten = " ".join(rewritten.split()).strip()
        if not rewritten or rewritten == query_text:
            return None
        return rewritten
