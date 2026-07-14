from __future__ import annotations

"""
Inspect the real question-answering pipeline for one question/document pair.

Usage:
    python scripts/debug_answer_pipeline.py --question "What are the maintenance intervals?" --document "19P006-31-FWC12-5-1-0_Manual"
    python scripts/debug_answer_pipeline.py --question "table of spare part list" --document-id doc_123 --run-llm --include-prompt
"""

import argparse
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for _import_root in (PROJECT_ROOT, SRC_ROOT):
    _import_root_str = str(_import_root)
    if _import_root_str not in sys.path:
        sys.path.insert(0, _import_root_str)

from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.workflows.question_answering.question_answering_request import (
    QuestionAnsweringRequest,
)
from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)
from src.shared.text.text_preview import preview_text


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the QA pipeline for one question and write a Markdown debug report."
    )
    parser.add_argument("--question", required=True, help="Question to inspect.")
    parser.add_argument("--document", help="Document title/file-name hint.")
    parser.add_argument("--document-id", help="Exact document ID.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output Markdown path. Defaults to outputs/debug_answering/<doc>_<question>_answer_pipeline.md",
    )
    parser.add_argument(
        "--run-llm",
        action="store_true",
        help="Run final answer generation too. Otherwise stop after prompt/debug stages.",
    )
    parser.add_argument(
        "--include-prompt",
        action="store_true",
        help="Include the full prompt text in the Markdown report.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def print_status(message: str) -> None:
    print(f"[debug-answer-pipeline] {message}", flush=True)


def slugify(value: str, *, max_length: int = 60) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_")
    if not normalized:
        normalized = "question"
    return normalized[:max_length].rstrip("_")


def default_output_path(question: str, document_name: str | None) -> Path:
    document_slug = slugify(document_name or "document")
    question_slug = slugify(question)
    return (
        PROJECT_ROOT
        / "outputs"
        / "debug_answering"
        / f"{document_slug}_{question_slug}_answer_pipeline.md"
    ).resolve()


def resolve_document(session, *, document: str | None, document_id: str | None) -> tuple[str, str]:
    from src.application.services.document import DocumentCatalogService
    from src.application.tools.documents import FindDocumentRequest, FindDocumentTool
    from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

    uow = SqlAlchemyUnitOfWork(session)
    tool = FindDocumentTool(DocumentCatalogService(uow.documents))
    request = (
        FindDocumentRequest(document_id=document_id)
        if document_id
        else FindDocumentRequest(query_text=document)
    )
    result = tool.run(request)
    if not result.success:
        raise ValueError(result.message or "Document could not be resolved.")
    return result.data["document_id"], result.data["display_name"]


def decode_table_rows(metadata: dict[str, str]) -> list[list[str]]:
    raw = metadata.get("table_rows_json")
    if not raw:
        return []
    try:
        decoded = json.loads(raw)
    except ValueError:
        return []
    return decoded if isinstance(decoded, list) else []


def json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, indent=2, default=str) + "\n```"


def text_block(value: str) -> str:
    return "```text\n" + value + "\n```"


def chunk_lines(chunks: Sequence[Any], *, title: str) -> list[str]:
    lines = [f"## {title}", ""]
    if not chunks:
        return [*lines, "_No chunks._", ""]
    for index, chunk in enumerate(chunks, start=1):
        metadata = dict(getattr(chunk, "metadata", {}) or {})
        rows = decode_table_rows(metadata)
        source = getattr(chunk, "source", None)
        lines.extend(
            [
                f"### Chunk {index}",
                f"- chunk_id: `{getattr(chunk, 'chunk_id', None)}`",
                f"- chunk_type: `{getattr(getattr(chunk, 'chunk_type', None), 'value', getattr(chunk, 'chunk_type', None))}`",
                f"- retrieval_source: `{getattr(chunk, 'retrieval_source', None)}`",
                f"- score: `{getattr(chunk, 'score', None)}`",
                f"- pages: `{getattr(source, 'page_start', None)}-{getattr(source, 'page_end', None)}`",
                f"- section_path: `{ ' > '.join(getattr(chunk, 'section_path', []) or []) }`",
                f"- table_category: `{metadata.get('table_category')}`",
                f"- hydrated: `{metadata.get('table_evidence_hydrated', 'false')}`",
                f"- logical_table_family_id: `{metadata.get('logical_table_family_id')}`",
                f"- decoded_table_rows: `{len(rows)}`",
                f"- content_preview: `{preview_text(getattr(chunk, 'content', ''), 300, empty_fallback='')}`",
                "",
            ]
        )
        if rows:
            lines.append("First rows:")
            for row in rows[:5]:
                lines.append(f"- `{row}`")
            lines.append("")
    return lines


def build_report(data: dict[str, Any], *, include_prompt: bool) -> str:
    lines = [
        "# Answer Pipeline Debug Report",
        "",
        "## Input",
        f"- question: `{data['question']}`",
        f"- document: `{data['document_name']}`",
        f"- document_id: `{data['document_id']}`",
        f"- route: `{data['route']}`",
        "",
        "## Query Analysis",
        f"- detected_intent: `{data['analyzed_query'].detected_intent}`",
        f"- chunk_types: `{[chunk_type.value for chunk_type in data['analyzed_query'].chunk_types]}`",
        f"- rewritten_query: `{data['analyzed_query'].rewritten_query}`",
        "",
        "Retrieval workflow diagnostics:",
        json_block(data["workflow_result"].diagnostics),
        "",
    ]
    lines.extend(chunk_lines(data["workflow_result"].final_chunks, title="Retrieved Chunks"))
    lines.extend(chunk_lines(data["prepared_chunks"], title="Prepared Chunks After Table Hydration"))
    lines.extend(
        [
            "## Guardrails and Structured Evidence",
            "",
            f"- approved_chunks: `{len(data['approved_chunks'])}`",
            f"- rejected_chunks: `{len(data['rejected_chunks'])}`",
            f"- structured_identifiers: `{len(data['structured_bundle'].identifiers)}`",
            f"- structured_entities: `{len(data['structured_bundle'].structured_entities)}`",
            "",
            "Structured evidence diagnostics:",
            json_block(data["structured_bundle"].diagnostics),
            "",
            "## Structured Context",
            "",
            f"- answer_intent: `{data['resolved_request'].answer_intent.value}`",
            f"- sources: `{len(data['structured_context'].sources)}`",
            f"- tables: `{len(data['structured_context'].tables)}`",
            f"- key_values: `{len(data['structured_context'].key_values)}`",
            f"- maintenance_entries: `{len(data['structured_context'].maintenance_entries)}`",
            "",
            "Context diagnostics:",
            json_block(data["structured_context"].diagnostics),
            "",
        ]
    )
    for index, table in enumerate(data["structured_context"].tables, start=1):
        lines.extend(
            [
                f"### Structured Table {index}",
                f"- table_kind: `{table.table_kind}`",
                f"- table_category: `{table.table_category}`",
                f"- headers: `{table.headers}`",
                f"- column_roles: `{table.column_roles}`",
                f"- row_count: `{len(table.rows)}`",
                "",
            ]
        )
        for row in table.rows[:5]:
            lines.append(f"- `{row.cells}`")
        lines.append("")
    if data["structured_context"].maintenance_entries:
        lines.append("### Maintenance Entries")
        lines.append("")
        for entry in data["structured_context"].maintenance_entries[:20]:
            lines.append(
                f"- task=`{entry.task}` interval=`{entry.interval}` component=`{entry.component}` notes=`{entry.notes}`"
            )
        lines.append("")
    if data["structured_context"].key_values:
        lines.append("### Key Values")
        lines.append("")
        for item in data["structured_context"].key_values[:30]:
            lines.append(
                f"- source={item.source_number} key=`{item.key}` value=`{preview_text(item.value, 160, empty_fallback='')}`"
            )
        lines.append("")
    lines.extend(
        [
            "## Prompt Context Bundle",
            "",
            f"- appendix_source_numbers: `{data['prompt_bundle'].appendix_source_numbers}`",
            "",
            "Prompt bundle diagnostics:",
            json_block(data["prompt_bundle"].diagnostics),
            "",
            "## Structured Evidence Payload",
            "",
            text_block(data["structured_payload"]),
            "",
            "## Deterministic Renderer Decision",
            "",
            json_block(data["deterministic_summary"]),
            "",
        ]
    )
    if include_prompt:
        lines.extend(["## Full Prompt", "", text_block(data["prompt"]), ""])
    else:
        lines.extend(
            [
                "## Prompt Preview",
                "",
                text_block(preview_text(data["prompt"], 3000, empty_fallback="")),
                "",
            ]
        )
    if data["generated_answer"] is not None:
        lines.extend(
            [
                "## Final Answer",
                "",
                f"- model: `{data['generated_answer'].model_name}`",
                f"- prompt_version: `{data['generated_answer'].prompt_version}`",
                "",
                text_block(data["generated_answer"].answer_text),
                "",
                "Diagnostics:",
                json_block(data["generated_answer"].diagnostics),
                "",
            ]
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    session = None
    services = None
    try:
        from src.application.agent_runtime.bootstrap.agent_service_builder import (
            build_agent_services,
        )
        from src.bootstrap.startup import bootstrap_application
        from src.infrastructure.db.base import Base
        from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded
        from src.infrastructure.db.schema_management import ensure_database_schema
        from src.infrastructure.db.session import SessionLocal, engine

        bootstrap_application()
        ensure_database_schema(engine)
        session = SessionLocal()
        document_id, document_name = resolve_document(
            session,
            document=args.document,
            document_id=args.document_id,
        )
        output_path = args.output.resolve() if args.output else default_output_path(args.question, document_name)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print_status(f"Document resolved: {document_name} ({document_id})")
        print_status("Building QA services...")
        services = build_agent_services(
            session,
            enable_generation=True,
            enable_llm_planning=False,
            enable_llm_research_planning=False,
        )
        qa_workflow = services.qa_workflow
        pipeline = qa_workflow._answer_generation_pipeline
        print_status("Analyzing question...")
        route, analyzed_query, analyzed_intent = qa_workflow._router.decide(
            question=args.question,
            top_k=5,
            document_id=document_id,
        )
        if route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION:
            raise ValueError("Question routed to document exploration, not retrieval QA.")
        print_status("Running retrieval workflow...")
        workflow_result = services.retrieval_workflow.run(analyzed_query)
        print_status("Applying context guardrails...")
        approved_chunks, context_blocking = pipeline._context_guardrail_chain.run(
            retrieved_chunks=workflow_result.final_chunks,
            query_text=args.question,
            document_id=document_id,
        )
        if context_blocking is not None:
            raise ValueError(context_blocking.safe_user_message or "Blocked by context guardrail.")
        rejected_ids = {chunk.chunk_id for chunk in workflow_result.final_chunks} - {
            chunk.chunk_id for chunk in approved_chunks
        }
        print_status("Preparing final evidence...")
        prepared_chunks = pipeline._structured_fact_joiner._final_evidence_preparer.prepare(
            query=analyzed_query,
            chunks=approved_chunks,
        )
        print_status("Resolving structured evidence...")
        structured_bundle = pipeline._structured_evidence_merger.merge(
            request=QuestionAnsweringRequest(question=args.question, document_id=document_id),
            analyzed_query=analyzed_query,
            workflow_result=workflow_result,
        )
        print_status("Building structured answer context...")
        join_result = pipeline._structured_fact_joiner.join(
            approved_chunks=approved_chunks,
            analyzed_query=analyzed_query,
            question=args.question,
            resolved_identifiers=list(structured_bundle.identifiers),
            resolved_structured_entities=list(structured_bundle.structured_entities),
        )
        answer_service = pipeline._answer_generation_service
        request = AnswerGenerationRequest(
            question=args.question,
            context_chunks=join_result.chunks,
            query_intent=analyzed_intent.value,
            retrieval_intent=analyzed_intent.value,
            chunk_type_preferences=list(analyzed_query.chunk_types),
            route=QuestionAnsweringRoute.RETRIEVAL_QA.value,
            resolved_identifiers=join_result.resolved_identifiers,
            resolved_structured_entities=join_result.resolved_structured_entities,
            structured_context=join_result.structured_context,
            answer_intent_decision=join_result.intent_decision,
        )
        resolved_request, _ = answer_service.request_resolver.resolve(request)
        print_status("Building answer prompt...")
        prompt = answer_service.prompt_builder.build(resolved_request)
        prompt_bundle = answer_service.prompt_builder.last_context_bundle
        structured_payload = answer_service.prompt_builder.structured_evidence_payload_serializer.serialize(
            prompt_bundle
        )
        deterministic_result = answer_service.deterministic_renderer_dispatcher.render(
            question=resolved_request.question,
            answer_intent=resolved_request.answer_intent,
            show_raw_evidence=resolved_request.show_raw_evidence,
            structured_context=resolved_request.structured_context,
            resolved_identifiers=resolved_request.resolved_identifiers,
            resolved_structured_entities=resolved_request.resolved_structured_entities,
        )
        generated_answer = None
        if args.run_llm:
            print_status("Running final answer generation...")
            generated_answer = answer_service.generate(resolved_request)
        report = build_report(
            {
                "question": args.question,
                "document_id": document_id,
                "document_name": document_name,
                "route": route.value,
                "analyzed_query": analyzed_query,
                "workflow_result": workflow_result,
                "approved_chunks": approved_chunks,
                "rejected_chunks": list(rejected_ids),
                "prepared_chunks": prepared_chunks,
                "structured_bundle": structured_bundle,
                "structured_context": resolved_request.structured_context,
                "resolved_request": resolved_request,
                "prompt_bundle": prompt_bundle,
                "structured_payload": structured_payload,
                "prompt": prompt,
                "deterministic_summary": (
                    {
                        "renderer_name": deterministic_result.renderer_name,
                        "model_name": deterministic_result.model_name,
                        "diagnostics": deterministic_result.diagnostics,
                        "answer_preview": preview_text(deterministic_result.answer_text, 1200, empty_fallback=""),
                    }
                    if deterministic_result is not None
                    else {"renderer_name": None, "llm_required": True}
                ),
                "generated_answer": generated_answer,
            },
            include_prompt=args.include_prompt,
        )
        output_path.write_text(report, encoding="utf-8")
        print_status(f"Markdown report written: {output_path}")
        print(output_path)
        return 0
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        if services is not None:
            close = getattr(services.qdrant_client, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    pass
        if session is not None:
            session.close()


if __name__ == "__main__":
    raise SystemExit(main())
