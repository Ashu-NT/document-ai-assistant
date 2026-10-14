from dataclasses import asdict, dataclass
import hashlib
import re


_WINDOWS_PATH_PATTERN = re.compile(r"[A-Za-z]:\\(?:[^\\\r\n]+\\)*[^\\\r\n]+")
_UNIX_PATH_PATTERN = re.compile(r"(?<!\w)/(?:[^/\s]+/)*[^/\s]+")

# Matches this codebase's own IdGenerator.new_id() output shape
# (f"{prefix}_{uuid4().hex}" - see src/shared/ids/id_generator.py and
# IdPrefix's values, e.g. "doc", "chunk", "extraction") wherever it
# appears embedded in prompt text. These IDs are freshly generated every
# process run (never content-derived), so two otherwise byte-identical
# prompts rendered in two separate runs will always differ here even when
# nothing semantically meaningful changed - see hash_prompt_canonical().
_GENERATED_ID_PATTERN = re.compile(r"\b[a-z][a-z_]*_[0-9a-f]{32}\b")


@dataclass(slots=True)
class ExtractionBatchDiagnostics:
    batch_index: int
    batch_count: int
    chunk_ids: list[str]
    char_count: int
    word_count: int
    model_name: str | None
    parse_success: bool
    parse_error: str | None = None
    raw_response_preview: str | None = None
    # SHA-256 of the exact rendered prompt text sent to the model for this
    # attempt -- lets two runs be compared for "did the prompt actually
    # differ" without storing the prompt's full (potentially large, and
    # source-document-derived) content. NOTE: this is sensitive to
    # process-local generated IDs (chunk_id, document_id, ...) embedded in
    # the prompt text, so it is NOT suitable, by itself, for comparing two
    # SEPARATE process runs of the same semantic input -- use
    # `prompt_sha256_canonical` for that (see `hash_prompt_canonical`).
    prompt_sha256: str | None = None
    # SHA-256 of the SAME prompt text with every embedded generated-ID
    # token (chunk_xxxx, doc_xxxx, ...) replaced by a fixed placeholder
    # before hashing. Two prompts that differ ONLY in which fresh IDs got
    # embedded (the common case across two separate process runs of
    # identical semantic input) hash identically here, while any genuine
    # content/instruction difference still changes this hash too.
    prompt_sha256_canonical: str | None = None
    budget_exhausted: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def hash_prompt_canonical(prompt: str) -> str:
    """Canonical, cross-process-run-comparable fingerprint of a rendered
    prompt: identical to `hash_prompt` except every embedded generated ID
    (this codebase's own `IdGenerator.new_id()` shape) is first replaced
    with a fixed placeholder. Diagnostic-only -- never applied to the
    prompt actually sent to the model, so production prompt content is
    completely unchanged.
    """
    canonicalized = _GENERATED_ID_PATTERN.sub("<ID>", prompt)
    return hashlib.sha256(canonicalized.encode("utf-8")).hexdigest()


def safe_response_preview(response: str, *, max_chars: int) -> str:
    normalized = response.strip().replace("\r\n", "\n")
    normalized = _WINDOWS_PATH_PATTERN.sub("[path]", normalized)
    normalized = _UNIX_PATH_PATTERN.sub("[path]", normalized)
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[:max_chars].rstrip()}..."
