from __future__ import annotations

"""
Run the hand-authored answer-quality golden set
(`src/application/evaluation/answer_quality/golden_answer_set.py`) through the
real question-answering pipeline, then grade each generated answer with a
SECOND, independent LLM call acting as a judge.

This closes the Section 7 / Phase 0 gap described in
`outputs/architecture/answer_quality_and_output_enterprise_hardening_plan.md`:
there was previously no automated way to score generated-answer quality --
only retrieval hit-rate (the retrieval benchmark) and routing/policy
compliance (agent-eval) were measured.

Usage:
    python scripts/run_answer_quality_judge.py
    python scripts/run_answer_quality_judge.py --limit 5
    python scripts/run_answer_quality_judge.py --output outputs/evaluation/answer_quality/report.json
    python scripts/run_answer_quality_judge.py --judge-model qwen2.5:7b

Requires a locally reachable Ollama instance to actually generate/grade
answers. If Ollama is not reachable, each case is reported as "skipped"
rather than crashing the whole run -- see `generate_case_answer()` and
`judge_answer()`, which are the two small, isolated "call the LLM" functions
a unit test can swap out for a fake (see
`tests/unit/cli_scripts/test_run_answer_quality_judge.py`).
"""

import argparse
import json
import re
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

from src.application.evaluation.answer_quality import (  # noqa: E402
    GoldenAnswerCase,
    load_golden_answer_cases,
)
from src.shared.exceptions import ApplicationError  # noqa: E402

_THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
_JSON_OBJECT_PATTERN = re.compile(r"\{.*\}", re.DOTALL)

_STATUS_JUDGED = "judged"
_STATUS_DOCUMENT_NOT_FOUND = "skipped_document_not_found"
_STATUS_GENERATION_FAILED = "skipped_generation_failed"
_STATUS_JUDGE_FAILED = "skipped_judge_failed"


@dataclass(slots=True)
class JudgeRuntime:
    answer_question_tool: Any
    judge_llm_service: Any
    judge_model: str | None
    session: Any = None
    qdrant_client: Any = None


@dataclass(slots=True)
class AnswerAttempt:
    ok: bool
    answer_text: str | None = None
    failure_reason: str | None = None


@dataclass(slots=True)
class JudgeVerdict:
    ok: bool
    score: float | None = None
    justification: str | None = None
    failure_reason: str | None = None


@dataclass(slots=True)
class CaseReport:
    case_id: str
    document_title: str
    question: str
    status: str
    answer_text: str | None = None
    score: float | None = None
    justification: str | None = None
    detail: str | None = None


@dataclass(slots=True)
class AnswerQualityReport:
    cases: list[CaseReport] = field(default_factory=list)

    @property
    def judged_cases(self) -> list[CaseReport]:
        return [case for case in self.cases if case.status == _STATUS_JUDGED]

    @property
    def average_score(self) -> float | None:
        judged = self.judged_cases
        if not judged:
            return None
        return sum(case.score for case in judged if case.score is not None) / len(judged)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_count": len(self.cases),
            "judged_count": len(self.judged_cases),
            "average_score": self.average_score,
            "cases": [
                {
                    "case_id": case.case_id,
                    "document_title": case.document_title,
                    "question": case.question,
                    "status": case.status,
                    "answer_text": case.answer_text,
                    "score": case.score,
                    "justification": case.justification,
                    "detail": case.detail,
                }
                for case in self.cases
            ],
        }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the hand-authored answer-quality golden set through the real "
            "QA pipeline and grade each generated answer with an independent "
            "LLM-as-judge pass."
        )
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Only run the first N golden cases (default: all).",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        metavar="MODEL",
        help="Override the LLM model used for the judge pass (defaults to GENERAL_LLM).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="PATH",
        help="Optional path to write the full JSON report to.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[answer-quality-judge] {message}", flush=True)


def _load_ask_document_module():
    """Dynamically loads scripts/ask_document.py so its existing
    `build_qa_runtime()` composition-root helper can be reused here instead
    of duplicating the retrieval/guardrail/answer-generation wiring it
    already owns. `scripts/` has no `__init__.py`, so it isn't a normal
    importable package -- this mirrors the same load-by-path technique
    `tests/unit/cli_scripts/_test_cli_scripts_part1.py::_load_script` already
    uses to load CLI scripts under test."""
    import importlib.util

    cache_key = "_answer_quality_judge_ask_document_module"
    if cache_key in sys.modules:
        return sys.modules[cache_key]

    script_path = PROJECT_ROOT / "scripts" / "ask_document.py"
    saved_path = list(sys.path)
    spec = importlib.util.spec_from_file_location(cache_key, script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[cache_key] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(cache_key, None)
        raise
    finally:
        sys.path[:] = saved_path
    return module


def build_judge_runtime(*, judge_model: str | None) -> JudgeRuntime:
    from src.application.services.ai import LLMService  # noqa: WPS433
    from src.application.services.document import DocumentCatalogService  # noqa: WPS433
    from src.application.tools.documents import FindDocumentTool  # noqa: WPS433
    from src.application.tools.question_answering import AnswerQuestionTool  # noqa: WPS433
    from src.bootstrap.startup import bootstrap_application  # noqa: WPS433
    from src.config.settings import llm_settings  # noqa: WPS433
    from src.infrastructure.ai.llm import OllamaLLMProvider  # noqa: WPS433
    from src.infrastructure.db.schema_management import ensure_database_schema  # noqa: WPS433
    from src.infrastructure.db.orm_models import (  # noqa: WPS433,F401
        __all__ as _orm_models_loaded,
    )
    from src.infrastructure.db.session import SessionLocal, engine  # noqa: WPS433
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork  # noqa: WPS433

    bootstrap_application()
    ensure_database_schema(engine)

    session = SessionLocal()
    ask_document = _load_ask_document_module()
    qa_runtime = ask_document.build_qa_runtime(session, enable_generation=True)

    uow = SqlAlchemyUnitOfWork(session)
    catalog_service = DocumentCatalogService(uow.documents)
    find_document_tool = FindDocumentTool(catalog_service)
    answer_question_tool = AnswerQuestionTool(
        qa_runtime.workflow,
        find_document_tool=find_document_tool,
    )

    resolved_judge_model = judge_model or llm_settings.general_llm
    judge_llm_service = LLMService(
        OllamaLLMProvider(
            base_url=llm_settings.ollama_base_url,
            default_model=resolved_judge_model,
        )
    )

    return JudgeRuntime(
        answer_question_tool=answer_question_tool,
        judge_llm_service=judge_llm_service,
        judge_model=resolved_judge_model,
        session=session,
        qdrant_client=qa_runtime.qdrant_client,
    )


def resolve_case_document_id(
    answer_question_tool,
    document_title: str,
) -> tuple[str | None, str | None]:
    """Returns (document_id, failure_reason). failure_reason is None on success."""
    from src.application.tools.documents import FindDocumentRequest  # noqa: WPS433

    find_document_tool = answer_question_tool.find_document_tool
    if find_document_tool is None:
        return None, "find_document_tool not configured"

    result = find_document_tool.run(FindDocumentRequest(query_text=document_title))
    if not result.success:
        return None, f"{result.error_code}: {result.message}"
    return result.data["document_id"], None


def generate_case_answer(
    *,
    answer_question_tool,
    document_id: str,
    question: str,
) -> AnswerAttempt:
    """Runs the real pipeline for a single golden case.

    Isolated on purpose: this is the one function that talks to a live LLM
    for answer generation, so a unit test can monkeypatch/replace it (or the
    tool it's given) with a fake instead of requiring a reachable Ollama
    instance.
    """
    from src.application.tools.question_answering import AnswerQuestionRequest  # noqa: WPS433

    request = AnswerQuestionRequest(
        question=question,
        document_id=document_id,
        allow_answer_generation=True,
        require_citations=True,
    )
    try:
        tool_result = answer_question_tool.run(request)
    except ApplicationError as exc:
        return AnswerAttempt(ok=False, failure_reason=f"{exc.error_code}: {exc.message}")
    except Exception as exc:  # pragma: no cover - defensive, mirrors other scripts
        return AnswerAttempt(ok=False, failure_reason=f"unexpected_error: {exc}")

    if not tool_result.success:
        return AnswerAttempt(
            ok=False,
            failure_reason=f"{tool_result.error_code}: {tool_result.message}",
        )

    result = tool_result.data
    answer_text = getattr(result, "answer_text", None)
    if not answer_text:
        return AnswerAttempt(ok=False, failure_reason="empty_answer_text")

    return AnswerAttempt(ok=True, answer_text=answer_text)


_JUDGE_PROMPT_TEMPLATE = """\
You are grading whether a generated answer to a question is factually \
correct and complete, compared to a known-good reference answer.

Question:
{question}

Generated answer to grade:
{answer_text}

Reference (gold) answer:
{expected_answer}

The generated answer MUST cover these factual claims:
{expected_claims}

Score the generated answer from 0.0 to 1.0 using this rubric:
- 1.0: covers all the required claims, does not contradict them, and does \
not fabricate unsupported specifics (numbers, part numbers, etc.).
- around 0.5: covers some but not all required claims, OR is vague/hedged \
where the reference is specific.
- 0.0: contradicts the required claims, fabricates specifics not present \
in the reference, or fails to address the question.

Respond with ONLY a JSON object of this exact shape, no other text:
{{"score": <number between 0.0 and 1.0>, "justification": "<one short sentence>"}}
"""


def _build_judge_prompt(
    *,
    question: str,
    answer_text: str,
    expected_answer: str,
    expected_claims: list[str],
) -> str:
    claims_block = "\n".join(f"- {claim}" for claim in expected_claims)
    return _JUDGE_PROMPT_TEMPLATE.format(
        question=question,
        answer_text=answer_text,
        expected_answer=expected_answer,
        expected_claims=claims_block,
    )


def _parse_judge_response(raw_response: str) -> tuple[float, str]:
    normalized = _THINK_BLOCK_PATTERN.sub("", raw_response or "").strip()
    if normalized.startswith("```") and normalized.endswith("```"):
        lines = normalized.splitlines()
        if len(lines) >= 2:
            normalized = "\n".join(lines[1:-1]).strip()

    payload = _try_parse_json_object(normalized)
    if payload is None:
        raise ValueError(f"Could not parse judge response as JSON: {normalized[:200]!r}")

    score = payload.get("score")
    try:
        score = float(score)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Judge response missing a numeric 'score' field: {payload!r}") from exc

    score = max(0.0, min(1.0, score))
    justification = str(payload.get("justification") or "").strip()
    return score, justification


def _try_parse_json_object(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = _JSON_OBJECT_PATTERN.search(text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def judge_answer(
    *,
    judge_llm_service,
    judge_model: str | None,
    question: str,
    answer_text: str,
    expected_answer: str,
    expected_claims: list[str],
) -> JudgeVerdict:
    """The second, independent LLM call: grades a generated answer against
    the golden case's expected answer/claims. Isolated the same way
    `generate_case_answer()` is, for the same testability reason."""
    prompt = _build_judge_prompt(
        question=question,
        answer_text=answer_text,
        expected_answer=expected_answer,
        expected_claims=expected_claims,
    )
    try:
        raw_response = judge_llm_service.generate(
            prompt,
            model=judge_model,
            json_mode=True,
        )
    except ApplicationError as exc:
        return JudgeVerdict(ok=False, failure_reason=f"{exc.error_code}: {exc.message}")
    except Exception as exc:  # pragma: no cover - defensive
        return JudgeVerdict(ok=False, failure_reason=f"unexpected_error: {exc}")

    try:
        score, justification = _parse_judge_response(raw_response)
    except ValueError as exc:
        return JudgeVerdict(ok=False, failure_reason=str(exc))

    return JudgeVerdict(ok=True, score=score, justification=justification)


def run_case(
    case: GoldenAnswerCase,
    *,
    answer_question_tool,
    judge_llm_service,
    judge_model: str | None,
) -> CaseReport:
    document_id, failure_reason = resolve_case_document_id(
        answer_question_tool,
        case.document_title,
    )
    if document_id is None:
        return CaseReport(
            case_id=case.case_id,
            document_title=case.document_title,
            question=case.question,
            status=_STATUS_DOCUMENT_NOT_FOUND,
            detail=failure_reason,
        )

    attempt = generate_case_answer(
        answer_question_tool=answer_question_tool,
        document_id=document_id,
        question=case.question,
    )
    if not attempt.ok:
        return CaseReport(
            case_id=case.case_id,
            document_title=case.document_title,
            question=case.question,
            status=_STATUS_GENERATION_FAILED,
            detail=attempt.failure_reason,
        )

    verdict = judge_answer(
        judge_llm_service=judge_llm_service,
        judge_model=judge_model,
        question=case.question,
        answer_text=attempt.answer_text or "",
        expected_answer=case.expected_answer,
        expected_claims=case.expected_claims,
    )
    if not verdict.ok:
        return CaseReport(
            case_id=case.case_id,
            document_title=case.document_title,
            question=case.question,
            status=_STATUS_JUDGE_FAILED,
            answer_text=attempt.answer_text,
            detail=verdict.failure_reason,
        )

    return CaseReport(
        case_id=case.case_id,
        document_title=case.document_title,
        question=case.question,
        status=_STATUS_JUDGED,
        answer_text=attempt.answer_text,
        score=verdict.score,
        justification=verdict.justification,
    )


def run_golden_set(
    cases: list[GoldenAnswerCase],
    *,
    answer_question_tool,
    judge_llm_service,
    judge_model: str | None,
    progress_callback=None,
) -> AnswerQualityReport:
    report = AnswerQualityReport()
    for index, case in enumerate(cases, start=1):
        if progress_callback is not None:
            progress_callback(f"[{index}/{len(cases)}] {case.case_id}: {case.question}")
        report.cases.append(
            run_case(
                case,
                answer_question_tool=answer_question_tool,
                judge_llm_service=judge_llm_service,
                judge_model=judge_model,
            )
        )
    return report


def print_report(report: AnswerQualityReport) -> None:
    print()
    for case in report.cases:
        print(f"{case.case_id}  [{case.status}]  {case.document_title}")
        print(f"  Q: {case.question}")
        if case.status == _STATUS_JUDGED:
            print(f"  score: {case.score:.2f}  justification: {case.justification}")
        else:
            print(f"  detail: {case.detail}")
        print()

    judged = report.judged_cases
    print(f"Cases run       : {len(report.cases)}")
    print(f"Cases judged    : {len(judged)}")
    if report.average_score is not None:
        print(f"Average score   : {report.average_score:.3f}")
    else:
        print("Average score   : n/a (no cases were successfully judged)")

    skipped_by_status: dict[str, int] = {}
    for case in report.cases:
        if case.status != _STATUS_JUDGED:
            skipped_by_status[case.status] = skipped_by_status.get(case.status, 0) + 1
    if skipped_by_status:
        print("Skipped cases:")
        for status, count in sorted(skipped_by_status.items()):
            print(f"  {status:<28} {count}")


def write_json_report(report: AnswerQualityReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.to_dict(), indent=2),
        encoding="utf-8",
    )


def close_runtime(runtime: JudgeRuntime | None) -> None:
    if runtime is None:
        return
    session = getattr(runtime, "session", None)
    if session is not None:
        session.close()
    qdrant_client = getattr(runtime, "qdrant_client", None)
    if qdrant_client is None:
        return
    close = getattr(qdrant_client, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            return


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    runtime: JudgeRuntime | None = None

    try:
        cases = load_golden_answer_cases()
        if args.limit is not None:
            cases = cases[: args.limit]

        print_status(f"Loaded {len(cases)} golden answer case(s).")
        print_status("Building answer-quality judge runtime...")
        runtime = build_judge_runtime(judge_model=args.judge_model)
        print_status(f"Judge model: {runtime.judge_model or '(default)'}")

        report = run_golden_set(
            cases,
            answer_question_tool=runtime.answer_question_tool,
            judge_llm_service=runtime.judge_llm_service,
            judge_model=runtime.judge_model,
            progress_callback=print_status,
        )

        print_report(report)

        if args.output is not None:
            write_json_report(report, args.output)
            print_status(f"Wrote JSON report to {args.output}")

        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        close_runtime(runtime)


if __name__ == "__main__":
    raise SystemExit(main())
