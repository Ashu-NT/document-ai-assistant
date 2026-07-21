from __future__ import annotations

import re

from src.application.langgraph.planning.models.execution_plan import ExecutionPlan
from src.application.langgraph.planning.models.plan_step_factory import (
    build_document_resolution_steps,
    build_execution_plan,
    build_plan_step,
)
from src.shared.ids import IdGenerator

_IDENTIFIER_VALUE_RE = re.compile(
    r"\b([A-Z]{1,5}-?\d{1,6}[A-Z0-9-]*|\d{3,}[A-Z0-9-]+|DN\s*\d+)\b"
)
_IDENTIFIER_TERM_RE = re.compile(
    r"\b(?:part\s*(?:number|no\.?)|p/?n\.?|serial\s*(?:number|no\.?)|s/?n\.?|"
    r"model\s*(?:number|no\.?)|order\s*code|drawing\s*(?:number|no\.?)|"
    r"tag\s*(?:number|no\.?)?|certificate\s*(?:number|no\.?)|component\s*code|"
    r"manufacturer|supplier|made\s*by|manufactured\s*by)\b",
    re.IGNORECASE,
)


def extract_identifier_value(normalized_input: str) -> str | None:
    match = _IDENTIFIER_VALUE_RE.search(normalized_input.upper())
    return match.group(0).replace(" ", "") if match else None


def has_identifier_term(normalized_input: str) -> bool:
    return bool(_IDENTIFIER_TERM_RE.search(normalized_input))


def _identifier_type_from_input(normalized_input: str) -> str | None:
    lower = normalized_input.lower()
    if re.search(r"\bpart\s*(?:number|no\.?)\b|\bp/?n\.?\b", lower):
        return "part_number"
    if re.search(r"\bserial\s*(?:number|no\.?)\b|\bs/?n\.?\b", lower):
        return "serial_number"
    if re.search(r"\bmodel\s*(?:number|no\.?)\b", lower):
        return "model_number"
    if re.search(r"\bcertificate\s*(?:number|no\.?)?\b|\bcert\b", lower):
        return "certificate_number"
    if re.search(r"\bdrawing\s*(?:number|no\.?)\b", lower):
        return "drawing_number"
    if re.search(r"\border\s*code\b|\bcomponent\s*code\b", lower):
        return "component_code"
    if re.search(r"\bmanufacturer\b|\bsupplier\b|\bmade\s*by\b|\bmanufactured\s*by\b", lower):
        return "manufacturer_name"
    return None


def build_identifier_plan(
    id_generator: IdGenerator,
    *,
    normalized_input: str,
    identifier_value: str | None,
    document_query: str | None,
    document_id: str | None,
    document_title: str | None,
) -> ExecutionPlan:
    identifier_type = _identifier_type_from_input(normalized_input)
    retrieve_args: dict[str, object] = {}
    if identifier_value:
        retrieve_args["identifier_value"] = identifier_value
    if identifier_type:
        retrieve_args["identifier_type"] = identifier_type
    if document_id:
        retrieve_args["document_id"] = document_id

    plan_steps = build_document_resolution_steps(
        id_generator, document_query=document_query, document_id=document_id
    )
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="retrieve_identifiers",
            description="Look up identifiers matching the requested value or type.",
            output_key="identifier_hits",
            args=retrieve_args,
        )
    )

    if "maintenance" in normalized_input:
        plan_steps.append(
            build_plan_step(
                id_generator,
                tool_name="retrieve_chunks",
                description="Retrieve maintenance procedure chunks linked to this identifier.",
                output_key="context_chunks",
                args={
                    "query_text": f"{identifier_value or 'identifier'} maintenance replacement procedure",
                    "chunk_types": ["maintenance_procedure"],
                    **({"document_id": document_id} if document_id else {}),
                },
                depends_on=["identifier_hits"],
            )
        )
    elif "specification" in normalized_input or "spec" in normalized_input:
        plan_steps.append(
            build_plan_step(
                id_generator,
                tool_name="retrieve_chunks",
                description="Retrieve technical specification chunks linked to this identifier.",
                output_key="context_chunks",
                args={
                    "query_text": f"{identifier_value or 'identifier'} technical specification",
                    "chunk_types": ["technical_specification"],
                    **({"document_id": document_id} if document_id else {}),
                },
                depends_on=["identifier_hits"],
            )
        )
    elif "context" in normalized_input or "where" in normalized_input or "used" in normalized_input:
        plan_steps.append(
            build_plan_step(
                id_generator,
                tool_name="retrieve_chunks",
                description="Retrieve chunks providing context for this identifier.",
                output_key="context_chunks",
                args={
                    "query_text": f"{identifier_value or 'identifier'} context usage",
                    **({"document_id": document_id} if document_id else {}),
                },
                depends_on=["identifier_hits"],
            )
        )

    last_output = plan_steps[-1].output_key
    plan_steps.append(
        build_plan_step(
            id_generator,
            tool_name="answer_question",
            description="Answer the identifier query using the retrieved evidence.",
            output_key="answer",
            input_key=last_output if last_output != "identifier_hits" else None,
            args={"question": normalized_input},
            depends_on=[last_output],
        )
    )

    return build_execution_plan(
        id_generator,
        goal=normalized_input,
        steps=plan_steps,
        reason="Detected an identifier lookup request requiring structured identifier retrieval.",
        requires_document=bool(document_id or document_query),
        document_id=document_id,
        document_title=document_title or document_query,
        diagnostics={
            "plan_kind": "identifier_lookup",
            "identifier_value": identifier_value,
            "identifier_type": identifier_type,
        },
    )
