from __future__ import annotations

from typing import Any


class StartupBanner:
    def render(
        self,
        *,
        runtime_status,
        selected_document_name: str | None,
        quiet: bool,
        no_examples: bool,
    ) -> str:
        if quiet:
            return ""
        lines = [
            "======================================================================================",
            "Document AI Agent",
            "======================================================================================",
            "",
            "Grounded Enterprise AI for Technical Documentation",
            "",
            "Corpus",
            "------",
            f"Documents       : {getattr(runtime_status, 'document_count', 0)}",
            f"Embedding Index : {getattr(runtime_status, 'embedding_index_status', 'Ready')}",
            f"Model           : {getattr(runtime_status, 'model_name', '-') or '-'}",
        ]
        if selected_document_name:
            lines.append(f"Selected Doc    : {selected_document_name}")
        capabilities = list(getattr(runtime_status, "capabilities", []) or [])
        if capabilities:
            lines.extend(
                [
                    "",
                    "Capabilities",
                    "------------",
                ]
            )
            for capability in capabilities:
                lines.append(f"[ok] {capability}")
        lines.extend(
            [
                "",
                "Quick Start",
                "-----------",
                "/list",
                "/open FWC12",
                "/help",
            ]
        )
        if not no_examples:
            lines.extend(
                [
                    "",
                    "Try asking:",
                    "- What are the maintenance intervals?",
                    "- What is the drive specification?",
                    "- Compare maintenance tasks and specifications.",
                    "- Generate a preventive maintenance report.",
                    "- Find part number A00168.",
                ]
            )
        lines.extend(
            [
                "",
                "==========================================================",
            ]
        )
        return "\n".join(lines)
