from __future__ import annotations

from typing import Any


class _LazyIngestionWorkflow:
    """Defers building the full `IngestionWorkflow` until ingest or reingest
    is actually invoked.

    `IngestDocumentTool`/`ReingestDocumentTool` are guardrail-blocked from
    ever being called by the planner (see `PlanPolicy`/`ToolExecutionPolicy`
    blocked tool lists), so eagerly building the parsing/classification/
    extraction pipeline (Docling parser, extraction LLM service, etc.) for
    every agent session would be pure startup cost paid on a path that
    almost never runs. This proxy duck-types the two methods
    `IngestDocumentTool.run`/`ReingestDocumentTool.run` actually call, and is
    shared by both tools so the underlying `IngestionWorkflow` is only ever
    built once regardless of which tool triggers the build.
    """

    def __init__(
        self,
        *,
        unit_of_work: Any,
        vector_store: Any,
        qdrant_client: Any,
        embedding_provider: Any,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._vector_store = vector_store
        self._qdrant_client = qdrant_client
        self._embedding_provider = embedding_provider
        self._ingestion_workflow: Any = None

    def run(self, request: Any) -> Any:
        return self._resolve().run(request)

    def reingest(self, request: Any) -> Any:
        return self._resolve().reingest(request)

    def _resolve(self) -> Any:
        if self._ingestion_workflow is None:
            from src.application.orchestrator.ingestion import (
                build_ingestion_runtime,
            )

            runtime = build_ingestion_runtime(
                unit_of_work=self._unit_of_work,
                vector_store=self._vector_store,
                qdrant_client=self._qdrant_client,
                embedding_provider=self._embedding_provider,
                bootstrap=False,
            )
            self._ingestion_workflow = runtime.ingestion_workflow
        return self._ingestion_workflow
