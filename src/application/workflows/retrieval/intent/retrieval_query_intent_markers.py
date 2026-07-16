import re

# Patterns that signal the user is asking about what a document contains or how
# it is structured, rather than asking for a specific fact inside the document.
#
# Each pattern covers a semantic shape rather than a literal phrase so that
# novel phrasings still match without a growing hardcoded list.
EXPLORATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    # "what (information|content|data) is/are in/inside/within this/the ..."
    re.compile(
        r"what\s+(information|content|data|details?)\s+(is|are)\s+(in|inside|within|available\s+in)\b"
    ),
    # "what does this/the document/manual/pdf/file contain/cover/include/have"
    re.compile(
        r"what\s+does\s+(this|the)\s+\S+\s+(contain|cover|include|have|describe|document)\b"
    ),
    # "what sections/chapters/topics/identifiers/tables/figures/... are/exist/available/covered"
    re.compile(
        r"what\s+(sections?|chapters?|topics?|subjects?|parts?|identifiers?|part\s+numbers?|"
        r"serial\s+numbers?|model\s+numbers?|tables?|figures?|images?|pictures?|assets?|"
        r"equipment|components?|products?|devices?|systems?)\s+"
        r"(are|is|exist|available|present|covered|listed|documented|mentioned|referenced|in\s+(this|the))\b"
    ),
    # "what is documented/available/covered/described here or in this"
    re.compile(
        r"what\s+is\s+(documented|available|covered|described|listed|included)\s+"
        r"(here|in\s+this|in\s+the)\b"
    ),
    # "what is in this document/pdf/manual/file/report"
    re.compile(
        r"what\s+is\s+in\s+(this|the)\s+(document|pdf|manual|file|report|guide|datasheet|drawing)\b"
    ),
    # "what can I find in this"
    re.compile(r"what\s+(can|could)\s+\w+\s+find\s+(in|inside|within)\b"),
    # "list / show / enumerate / display sections / structure / identifiers / tables / ..."
    re.compile(
        r"(list|show|display|enumerate|give\s+me|provide)\s+(all\s+|the\s+)?"
        r"(sections?|chapters?|topics?|structure|contents?|identifiers?|tables?|figures?|assets?|equipment)\b"
    ),
    # "document / manual / pdf structure / outline / overview / contents / index"
    re.compile(
        r"(document|manual|pdf|file|report)\s+"
        r"(structure|outline|overview|contents?|index|inventory|coverage)\b"
    ),
    # "what topics/subjects/areas are covered/discussed/addressed in"
    re.compile(
        r"what\s+(topics?|subjects?|areas?|items?|things?)\s+(are|is)\s+"
        r"(covered|discussed|addressed|documented|included)\b"
    ),
    # "what is this document/manual/pdf about"
    re.compile(
        r"what\s+is\s+(this|the)\s+(document|manual|pdf|file|report|guide|datasheet)\s+about\b"
    ),
)
EXPLICIT_IDENTIFIER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(serial|part|order|model|drawing|certificate|approval|position|tag)\s+"
        r"(number|numbers|no|code|codes|designation)\b"
    ),
    re.compile(r"\bspare\s+part\s+(number|no|code)\b"),
    re.compile(r"\bordering\s+code\b"),
    re.compile(r"\border\s+code\b"),
    re.compile(r"\bwhat\s+product\s+is\s+type\s+[a-z0-9-]+\b"),
    re.compile(r"\bwhat\s+is\s+type\s+[a-z0-9-]+\b"),
    re.compile(r"\bwhat\s+is\s+position\s+[a-z0-9-]+\b"),
)
IDENTIFIER_LISTING_VERBS: tuple[str, ...] = (
    "list",
    "show",
    "display",
    "enumerate",
    "provide",
    "give me",
    "find all",
)
IDENTIFIER_LISTING_MARKERS: tuple[str, ...] = (
    "serial",
    "part",
    "order code",
    "order number",
    "model",
    "drawing",
    "certificate",
    "tag",
    "manufacturer",
    "supplier",
)
OVERVIEW_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bwhat\s+does\s+.+\s+do\b"),
    re.compile(r"\bwhat\s+is\s+.+\s+used\s+for\b"),
    re.compile(r"\bwhat\s+is\s+the\s+(purpose|function)\s+of\b"),
    re.compile(r"\bhow\s+does\s+.+\s+work\b"),
)
PROCEDURE_MARKERS: tuple[str, ...] = (
    "how to",
    "procedure",
    "steps",
    "step",
    "replace",
    "install",
    "configure",
    "calibrate",
    "start",
    "run",
    "restart",
    "remove",
    "connect",
    "shutdown",
    "commission",
    "commissioning",
    "lubricate",
)
# NOTE on cross-module duplication (investigated, not merged): "general
# maintenance topic" detection is independently reimplemented in at least
# three places -- here, AnswerIntentAnalyzer._MAINTENANCE_TERMS (answer
# formatting), and RetrievalSignalExtractor._MAINTENANCE_TERMS (LangGraph
# strategy signals) -- and their vocabularies have drifted by more than a
# marker or two (e.g. this list deliberately excludes bare "service" and
# "inspection", which the other two include, since those bare words are
# broad enough to misfire on retrieval chunk-type targeting specifically --
# "inspection" alone already overlaps AnswerIntentAnalyzer's OWN
# CERTIFICATION_TERMS). This is unlike the MAINTENANCE_INTERVAL_MARKERS
# consolidation in maintenance_signal_detection.py, where the two lists
# solved the identical narrow sub-problem for two consumers and differed by
# exactly one marker each way -- a safe, mechanical merge. Here the three
# lists serve three different downstream decisions (what to retrieve vs. how
# to format an answer vs. which strategy signal to weight) with different
# false-positive tolerances, so forcing a shared vocabulary would either
# broaden retrieval's targeting (risking wrong chunk types) or narrow answer
# formatting's tuning. Left separate, deliberately, rather than merged.
MAINTENANCE_MARKERS: tuple[str, ...] = (
    "maintenance",
    "service interval",
    "service schedule",
    "inspection schedule",
    "maintenance interval",
    "maintenance intervals",
    "maintenance task",
    "maintenance tasks",
    "preventive maintenance",
    "oil change",
    "lubricat",
    "grease",
    "how often",
    "interval",
)
FIGURE_MARKERS: tuple[str, ...] = ("figure", "diagram", "drawing", "schematic", "image")
TABLE_MARKERS: tuple[str, ...] = (
    "table",
    "spare part",
    "parts list",
    "spare parts list",
    "matrix",
)
TABLE_REQUEST_MARKERS: tuple[str, ...] = (
    *TABLE_MARKERS,
    "row",
    "rows",
    "list",
)
IDENTIFIER_KEYWORD_MARKERS: tuple[str, ...] = (
    "serial number",
    "part number",
    "part no",
    "order code",
    "order number",
    "model number",
    "drawing number",
    "certificate number",
    "what is position ",
)
IDENTIFIER_TABLE_MARKERS: tuple[str, ...] = (
    *IDENTIFIER_KEYWORD_MARKERS,
    "serial numbers",
    "part numbers",
    "model numbers",
)
SPECIFICATION_MARKERS: tuple[str, ...] = (
    "specification",
    "specifications",
    "parameter",
    "voltage",
    "current",
    "tolerance",
    "dimension",
    "torque",
    "pressure",
    "approval",
    "certificate",
)
SPECIFICATION_TABLE_MARKERS: tuple[str, ...] = (
    *SPECIFICATION_MARKERS,
    "technical data",
    "datasheet",
    "operating limits",
)
TROUBLESHOOTING_MARKERS: tuple[str, ...] = (
    "troubleshoot",
    "problem",
    "fault",
    "error",
    "not working",
    "causes",
    "remedies",
    "diagnose",
    "symptom",
)
SAFETY_MARKERS: tuple[str, ...] = ("safety", "warning", "danger", "hazard")
OVERVIEW_KEYWORD_MARKERS: tuple[str, ...] = (
    "overview",
    "summary",
    "introduction",
    "explain",
    "objective",
    "purpose",
    "function",
)
COMPARATIVE_MARKERS: tuple[str, ...] = (
    "difference between",
    "compare",
    "comparison",
    " vs ",
    " vs. ",
    " versus ",
)
