from src.shared.text.alnum_tokenizer import tokenize_alnum

_MORPH_FAMILIES: tuple[frozenset[str], ...] = (
    frozenset({"electrical", "electrically", "electric"}),
    frozenset({"connect", "connected", "connecting", "connection", "connections"}),
    frozenset({"calibrate", "calibrated", "calibrating", "calibration"}),
    frozenset({"lubricate", "lubricated", "lubricating", "lubrication"}),
    frozenset({"order", "ordered", "ordering"}),
    frozenset({"install", "installed", "installing", "installation"}),
    frozenset({"commission", "commissioned", "commissioning"}),
    frozenset({"macerator", "macerators"}),
    frozenset({"pump", "pumps"}),
    frozenset({"valve", "valves"}),
    frozenset({"component", "components"}),
    frozenset({"interval", "intervals"}),
    frozenset({"quantity", "quantities"}),
    frozenset({"procedure", "procedures"}),
    frozenset({"instruction", "instructions"}),
    frozenset({"specification", "specifications"}),
    frozenset({"remove", "removed", "removing", "removal"}),
    frozenset({"inspect", "inspected", "inspecting", "inspection"}),
    frozenset({"replace", "replaced", "replacing", "replacement"}),
    frozenset({"adjust", "adjusted", "adjusting", "adjustment"}),
    frozenset({"operate", "operated", "operating", "operation"}),
    frozenset(
        {"optimize", "optimise", "optimized", "optimised", "optimizing", "optimising"}
    ),
    frozenset({"analyse", "analyze", "analysing", "analyzing", "analysis"}),
)
MORPH_VARIANTS: dict[str, frozenset[str]] = {
    term: family for family in _MORPH_FAMILIES for term in family
}


def expand_query_terms_with_morph_variants(terms: list[str]) -> list[str]:
    seen: set[str] = set(terms)
    extra: list[str] = []
    for term in terms:
        for variant in MORPH_VARIANTS.get(term, frozenset()):
            if variant not in seen:
                seen.add(variant)
                extra.append(variant)
    return terms + extra


def contains_compact_id(compact_id: str, text: str) -> bool:
    if not compact_id or not text:
        return False
    tokens = tokenize_alnum(text)
    for window in (1, 2, 3):
        for index in range(len(tokens) - window + 1):
            if "".join(tokens[index : index + window]) == compact_id:
                return True
    return False


def section_path_hit(term: str, padded_path: str) -> bool:
    if f" {term} " in padded_path:
        return True
    for variant in MORPH_VARIANTS.get(term, frozenset()):
        if f" {variant} " in padded_path:
            return True
    return False
