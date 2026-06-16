# Maintenance AI Assistant — Repository Architecture

## Purpose

This document defines the final enterprise-style Python repository structure for the **Local AI Maintenance Document Assistant**.

The system ingests technical PDF documents, parses them with Docling, converts them into a structured document graph, classifies the document type, extracts maintenance knowledge, builds section-based chunks, enriches chunks with generated questions, stores structured metadata in SQLAlchemy/Alembic-backed database storage, stores vectors in Qdrant, and answers user questions through guarded hybrid RAG and agentic workflows.

Core goals:

- Maintainability: every folder has one clear responsibility.
- Scalability: infrastructure can be swapped, for example SQLite to PostgreSQL.
- Testability: domain, application, infrastructure, ingestion, retrieval, and guardrails can be tested independently.
- Flexibility: LLMs, embedding models, classifiers, OCR engines, vector stores, and workflows are behind contracts.

---

## Final Repository Structure

```text
maintenance_ai_assistant/
│
├── pyproject.toml
├── README.md
├── .env
├── .env.example
├── .gitignore
│
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── data/
│   ├── input/
│   ├── samples/
│   └── fixtures/
│
├── outputs/
│   ├── parsed/
│   ├── images/
│   ├── logs/
│   ├── exports/
│   └── evaluation/
│
├── qdrant_data/
│
├── docs/
│   ├── architecture.md
│   ├── ingestion_flow.md
│   ├── database_schema.md
│   ├── rag_design.md
│   ├── langgraph_workflows.md
│   └── evaluation_plan.md
│
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── validation/
│   │   ├── ingestion/
│   │   ├── classification/
│   │   ├── extraction/
│   │   ├── retrieval/
│   │   ├── agent/
│   │   ├── tools/
│   │   ├── guardrails/
│   │   ├── memory/
│   │   └── workflows/
│   │
│   ├── integration/
│   │   ├── db/
│   │   ├── qdrant/
│   │   ├── ollama/
│   │   ├── ingestion/
│   │   └── retrieval/
│   │
│   └── e2e/
│       ├── test_ingest_document.py
│       ├── test_extract_maintenance.py
│       └── test_ask_question.py
│
└── src/
    │
    ├── cli/
    │   ├── main.py
    │   ├── ingest_command.py
    │   ├── query_command.py
    │   ├── extract_command.py
    │   └── eval_command.py
    │
    ├── config/
    │   ├── settings.py
    │   └── logging.py
    │
    ├── shared/
    │   ├── ids.py
    │   ├── time.py
    │   ├── hashing.py
    │   ├── exceptions.py
    │   └── constants.py
    │
    ├── domain/
    │   ├── enums.py
    │   ├── metadata.py
    │   ├── document_models.py
    │   ├── extraction_models.py
    │   ├── memory_models.py
    │   └── event_models.py
    │
    ├── application/
    │   │
    │   ├── contracts/
    │   │   ├── document_repository.py
    │   │   ├── extraction_repository.py
    │   │   ├── memory_repository.py
    │   │   ├── vector_store.py
    │   │   ├── llm_provider.py
    │   │   ├── embedding_provider.py
    │   │   ├── document_classifier.py
    │   │   ├── reranker.py
    │   │   ├── ocr_provider.py
    │   │   ├── event_bus.py
    │   │   ├── workflow_runner.py
    │   │   └── tool.py
    │   │
    │   ├── events/
    │   │   ├── common/
    │   │   │   ├── event_bus.py
    │   │   │   ├── event_dispatcher.py
    │   │   │   ├── event_handler.py
    │   │   │   └── event_result.py
    │   │   ├── ingestion/
    │   │   │   ├── ingestion_events.py
    │   │   │   └── ingestion_event_handlers.py
    │   │   ├── classification/
    │   │   │   ├── classification_events.py
    │   │   │   └── classification_event_handlers.py
    │   │   ├── extraction/
    │   │   │   ├── extraction_events.py
    │   │   │   └── extraction_event_handlers.py
    │   │   ├── retrieval/
    │   │   │   ├── retrieval_events.py
    │   │   │   └── retrieval_event_handlers.py
    │   │   └── finalization/
    │   │       ├── final_result_events.py
    │   │       └── final_result_event_handlers.py
    │   │
    │   ├── validation/
    │   │   ├── common/
    │   │   │   ├── validation_result.py
    │   │   │   ├── validation_error.py
    │   │   │   └── validation_context.py
    │   │   ├── ingestion/
    │   │   │   ├── document_validator.py
    │   │   │   ├── element_validator.py
    │   │   │   ├── section_validator.py
    │   │   │   ├── chunk_validator.py
    │   │   │   ├── asset_validator.py
    │   │   │   └── ingestion_validator.py
    │   │   ├── classification/
    │   │   │   ├── classification_validator.py
    │   │   │   └── classification_schema_validator.py
    │   │   ├── extraction/
    │   │   │   ├── extraction_validator.py
    │   │   │   ├── maintenance_task_validator.py
    │   │   │   ├── spare_part_validator.py
    │   │   │   └── equipment_info_validator.py
    │   │   ├── retrieval/
    │   │   │   ├── retrieval_result_validator.py
    │   │   │   ├── retrieved_chunk_validator.py
    │   │   │   └── citation_validator.py
    │   │   └── finalization/
    │   │       ├── final_answer_validator.py
    │   │       ├── final_result_validator.py
    │   │       └── final_output_validator.py
    │   │
    │   ├── ingestion/
    │   │   ├── pipeline/
    │   │   │   ├── ingest_pipeline.py
    │   │   │   ├── ingest_service.py
    │   │   │   ├── ingest_context.py
    │   │   │   └── ingest_result.py
    │   │   ├── parsing/
    │   │   │   ├── docling_parser.py
    │   │   │   ├── docling_normalizer.py
    │   │   │   └── reading_order_sorter.py
    │   │   ├── builders/
    │   │   │   ├── section_builder.py
    │   │   │   ├── section_mapper.py
    │   │   │   ├── asset_builder.py
    │   │   │   ├── picture_mapper.py
    │   │   │   └── document_graph_builder.py
    │   │   ├── chunking/
    │   │   │   ├── chunk_builder.py
    │   │   │   ├── chunk_type_classifier.py
    │   │   │   └── identifier_extractor.py
    │   │   ├── enrichment/
    │   │   │   ├── question_generation_service.py
    │   │   │   └── enriched_text_builder.py
    │   │   └── hashing/
    │   │       ├── file_hash_service.py
    │   │       └── content_hash_service.py
    │   │
    │   ├── classification/
    │   │   ├── pipeline/
    │   │   │   ├── classification_pipeline.py
    │   │   │   ├── classification_service.py
    │   │   │   └── classification_result.py
    │   │   ├── features/
    │   │   │   ├── document_feature_builder.py
    │   │   │   ├── title_feature_extractor.py
    │   │   │   ├── section_feature_extractor.py
    │   │   │   └── keyword_feature_extractor.py
    │   │   ├── rules/
    │   │   │   ├── document_type_rules.py
    │   │   │   └── confidence_rules.py
    │   │   └── schemas/
    │   │       └── classification_schema.py
    │   │
    │   ├── extraction/
    │   │   ├── pipeline/
    │   │   │   ├── extraction_pipeline.py
    │   │   │   ├── extraction_service.py
    │   │   │   ├── extraction_context.py
    │   │   │   └── extraction_result.py
    │   │   ├── maintenance/
    │   │   │   ├── maintenance_task_extractor.py
    │   │   │   ├── maintenance_interval_extractor.py
    │   │   │   ├── safety_note_extractor.py
    │   │   │   └── maintenance_schema.py
    │   │   ├── spare_parts/
    │   │   │   ├── spare_part_extractor.py
    │   │   │   ├── spare_part_table_parser.py
    │   │   │   └── spare_part_schema.py
    │   │   ├── equipment/
    │   │   │   ├── manufacturer_extractor.py
    │   │   │   ├── model_number_extractor.py
    │   │   │   └── equipment_schema.py
    │   │   └── schemas/
    │   │       └── extraction_schema.py
    │   │
    │   ├── retrieval/
    │   │   ├── pipeline/
    │   │   │   ├── retrieval_pipeline.py
    │   │   │   ├── retrieval_service.py
    │   │   │   ├── retrieval_context.py
    │   │   │   └── retrieval_result.py
    │   │   ├── query_analysis/
    │   │   │   ├── query_analyzer.py
    │   │   │   ├── query_type_classifier.py
    │   │   │   ├── identifier_detector.py
    │   │   │   └── query_rewriter.py
    │   │   ├── retrievers/
    │   │   │   ├── dense_retriever.py
    │   │   │   ├── keyword_retriever.py
    │   │   │   ├── sql_retriever.py
    │   │   │   └── hybrid_retriever.py
    │   │   ├── ranking/
    │   │   │   ├── result_merger.py
    │   │   │   ├── reranker.py
    │   │   │   └── score_normalizer.py
    │   │   ├── filters/
    │   │   │   ├── metadata_filter_builder.py
    │   │   │   ├── document_type_filter.py
    │   │   │   └── chunk_type_filter.py
    │   │   └── answering/
    │   │       ├── answer_service.py
    │   │       ├── context_builder.py
    │   │       ├── citation_builder.py
    │   │       └── answer_result.py
    │   │
    │   ├── agent/
    │   │   ├── runtime/
    │   │   │   ├── agent_runtime.py
    │   │   │   ├── agent_state.py
    │   │   │   ├── agent_context.py
    │   │   │   └── agent_result.py
    │   │   ├── planning/
    │   │   │   ├── intent_router.py
    │   │   │   ├── tool_selector.py
    │   │   │   └── agent_policy.py
    │   │   └── registry/
    │   │       ├── tool_registry.py
    │   │       ├── tool_call.py
    │   │       ├── tool_result.py
    │   │       └── tool_schema.py
    │   │
    │   ├── tools/
    │   │   ├── retrieval/
    │   │   │   ├── retrieve_chunks_tool.py
    │   │   │   ├── search_identifier_tool.py
    │   │   │   └── get_chunk_tool.py
    │   │   ├── document/
    │   │   │   ├── get_document_tool.py
    │   │   │   ├── list_documents_tool.py
    │   │   │   └── get_document_sections_tool.py
    │   │   ├── extraction/
    │   │   │   ├── extract_tasks_tool.py
    │   │   │   ├── extract_spare_parts_tool.py
    │   │   │   └── extract_equipment_info_tool.py
    │   │   └── answering/
    │   │       └── answer_with_context_tool.py
    │   │
    │   ├── guardrails/
    │   │   ├── common/
    │   │   │   ├── guardrail_result.py
    │   │   │   ├── guardrail_context.py
    │   │   │   └── guardrail_severity.py
    │   │   ├── evidence/
    │   │   │   ├── evidence_guardrail.py
    │   │   │   └── evidence_thresholds.py
    │   │   ├── citations/
    │   │   │   ├── citation_guardrail.py
    │   │   │   └── citation_policy.py
    │   │   ├── schemas/
    │   │   │   ├── schema_guardrail.py
    │   │   │   └── schema_validation_result.py
    │   │   ├── confidence/
    │   │   │   ├── confidence_guardrail.py
    │   │   │   └── confidence_policy.py
    │   │   ├── actions/
    │   │   │   ├── action_guardrail.py
    │   │   │   └── allowed_actions.py
    │   │   └── safety/
    │   │       ├── maintenance_safety_guardrail.py
    │   │       └── human_review_policy.py
    │   │
    │   ├── memory/
    │   │   ├── short_term/
    │   │   │   ├── conversation_memory.py
    │   │   │   ├── graph_memory.py
    │   │   │   └── memory_state.py
    │   │   ├── long_term/
    │   │   │   ├── document_memory.py
    │   │   │   ├── identifier_memory.py
    │   │   │   └── memory_service.py
    │   │   └── retrieval/
    │   │       ├── memory_retriever.py
    │   │       └── memory_context_builder.py
    │   │
    │   ├── workflows/
    │   │   ├── common/
    │   │   │   ├── graph_state.py
    │   │   │   ├── graph_result.py
    │   │   │   ├── workflow_context.py
    │   │   │   └── workflow_registry.py
    │   │   ├── ingestion/
    │   │   │   ├── ingestion_graph.py
    │   │   │   ├── ingestion_state.py
    │   │   │   ├── ingestion_nodes.py
    │   │   │   ├── ingestion_edges.py
    │   │   │   └── ingestion_router.py
    │   │   ├── classification/
    │   │   │   ├── classification_graph.py
    │   │   │   ├── classification_nodes.py
    │   │   │   └── classification_state.py
    │   │   ├── extraction/
    │   │   │   ├── extraction_graph.py
    │   │   │   ├── extraction_nodes.py
    │   │   │   └── extraction_state.py
    │   │   ├── retrieval/
    │   │   │   ├── retrieval_graph.py
    │   │   │   ├── retrieval_nodes.py
    │   │   │   └── retrieval_state.py
    │   │   └── agent/
    │   │       ├── agent_graph.py
    │   │       ├── agent_nodes.py
    │   │       ├── agent_router.py
    │   │       ├── agent_state.py
    │   │       └── agent_checkpoint.py
    │   │
    │   └── evaluation/
    │       ├── datasets/
    │       │   └── eval_dataset_loader.py
    │       ├── metrics/
    │       │   ├── classification_metrics.py
    │       │   ├── retrieval_metrics.py
    │       │   └── extraction_metrics.py
    │       └── runners/
    │           └── evaluation_runner.py
    │
    └── infrastructure/
        ├── db/
        │   ├── base.py
        │   ├── session.py
        │   ├── orm_models.py
        │   ├── repositories/
        │   │   ├── document_repository.py
        │   │   ├── chunk_repository.py
        │   │   ├── ingestion_run_repository.py
        │   │   ├── classification_repository.py
        │   │   ├── extraction_repository.py
        │   │   ├── memory_repository.py
        │   │   ├── identifier_repository.py
        │   │   └── vector_mapping_repository.py
        │   └── unit_of_work.py
        ├── vectorstores/
        │   ├── qdrant_client.py
        │   ├── qdrant_payload_builder.py
        │   └── qdrant_vector_store.py
        ├── embeddings/
        │   └── sentence_transformer_provider.py
        ├── llm/
        │   ├── ollama_provider.py
        │   └── prompts/
        │       ├── document_classifier_prompt.py
        │       ├── chunk_question_prompt.py
        │       ├── chunk_type_prompt.py
        │       ├── extraction_prompt.py
        │       ├── query_rewrite_prompt.py
        │       └── answer_generation_prompt.py
        ├── classifiers/
        │   ├── ollama_document_classifier.py
        │   └── rule_based_document_classifier.py
        ├── rerankers/
        │   ├── simple_score_reranker.py
        │   └── cross_encoder_reranker.py
        └── ocr/
            └── paddle_ocr_provider.py
```

---

# Root-Level Files and Folders

## `pyproject.toml`

Project configuration for packaging, dependencies, formatting, linting, and testing.

Should contain:

- Project name and version.
- Python version requirement.
- Dependencies such as SQLAlchemy, Alembic, Docling, Qdrant client, Typer, Pydantic, LangGraph, SentenceTransformers, and Ollama client library or HTTP client.
- Development dependencies such as pytest, ruff, mypy.
- CLI entry point, for example `maintenance-ai = "src.cli.main:app"` if packaging is configured that way.

## `README.md`

Project overview and quick start guide.

Should contain:

- What the project does.
- Installation instructions.
- How to run ingestion.
- How to ask questions.
- How to run tests.
- Current MVP scope.
- Out-of-scope features.

## `.env`

Local developer environment variables.

Should contain actual local values, but must not be committed.

Example:

```env
DATABASE_URL=sqlite:///./maintenance_ai.db
QDRANT_PATH=./qdrant_data
QDRANT_COLLECTION=maintenance_chunks
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

## `.env.example`

Template for required environment variables.

Should be committed.

## `.gitignore`

Ignore generated and local files.

Should include:

```text
.env
__pycache__/
*.pyc
.venv/
maintenance_ai.db
qdrant_data/
outputs/
```

---

# Alembic

## `alembic.ini`

Alembic configuration file.

Should point to the `alembic/` folder and be configured so `alembic/env.py` loads the database URL from `src/config/settings.py`.

## `alembic/env.py`

Alembic environment setup.

Should:

- Import `Base` from `src/infrastructure/db/base.py`.
- Import ORM models from `src/infrastructure/db/orm_models.py`.
- Load database URL from settings.
- Set `target_metadata = Base.metadata`.

## `alembic/script.py.mako`

Alembic migration template.

Usually generated by Alembic.

## `alembic/versions/`

Stores migration files.

Each migration should represent a database schema change.

---

# Data and Outputs

## `data/input/`

Raw files users want to ingest.

Example:

```text
pump_manual.pdf
water_treatment_datasheet.pdf
```

## `data/samples/`

Small sample PDFs used for demo and development.

## `data/fixtures/`

Test fixtures.

Should contain stable sample inputs and expected outputs.

## `outputs/parsed/`

Debug exports from Docling normalization.

Can contain:

- Parsed JSON snapshots.
- Markdown exports.
- Normalized element dumps.

## `outputs/images/`

Extracted image assets from PDFs.

Should store images by document ID.

Example:

```text
outputs/images/doc_001/pic_001.png
```

## `outputs/logs/`

Runtime logs.

## `outputs/exports/`

Generated CSV, JSON, or Markdown outputs for extracted tasks and spare parts.

## `outputs/evaluation/`

Evaluation reports and metric outputs.

## `qdrant_data/`

Local Qdrant storage path when using embedded/local Qdrant.

---

# Documentation

## `docs/architecture.md`

High-level system architecture.

Should explain:

- Domain/application/infrastructure separation.
- Ingestion pipeline.
- RAG architecture.
- Agent architecture.
- Guardrails.

## `docs/ingestion_flow.md`

Detailed ingestion flow.

Should document:

1. Create IngestionRun
2. Calculate File Hash
3. Check File Duplicate
4. Parse PDF
5. Normalize Elements
6. Calculate Content Hash
7. Check Content Duplicate
8. Build Sections
9. Extract Assets
10. Classify Document
11. Build Chunks
12. Extract Identifiers
13. Generate Questions
14. Build Embedding Text
15. Store SQL
16. Store Qdrant
17. Save Vector Mapping
18. Mark Success

## `docs/database_schema.md`

Database schema explanation.

Should document:

- Documents table.
- Elements table.
- Sections table.
- Chunks table.
- Assets tables.
- Generated questions table.
- Identifiers table.
- Ingestion runs table.
- Vector mapping table.

## `docs/rag_design.md`

Hybrid RAG design.

Should explain:

- Dense retrieval.
- Keyword retrieval.
- SQL retrieval.
- Result merging.
- Reranking.
- Guarded answer generation.

## `docs/langgraph_workflows.md`

LangGraph workflow documentation.

Should explain:

- Ingestion graph.
- Retrieval graph.
- Agent graph.
- State objects.
- Nodes and edges.

## `docs/evaluation_plan.md`

Evaluation strategy.

Should include:

- Classification accuracy.
- Extraction precision/recall.
- Retrieval hit rate.
- Grounded answer rate.
- Citation validity.
- Latency.

---

# Tests

## `tests/unit/`

Unit tests for isolated functions and classes.

Should not require external services.

## `tests/integration/`

Tests involving SQLite, Qdrant, Ollama, or full ingestion components.

## `tests/e2e/`

End-to-end tests that simulate realistic user flows.

Example:

- Ingest document.
- Extract maintenance tasks.
- Ask question.
- Validate answer has citations.

---

# `src/cli/`

CLI entry points.

This layer should only parse command-line input and call application services.

It should not contain business logic, SQLAlchemy code, Qdrant logic, or LLM prompts.

## `main.py`

Main Typer or argparse application.

Should:

- Register CLI commands.
- Initialize logging.
- Load settings.

Example commands:

```bash
maintenance-ai ingest data/input/manual.pdf
maintenance-ai ask "What are the annual maintenance tasks?"
maintenance-ai extract --doc-id doc_001
maintenance-ai eval
```

## `ingest_command.py`

CLI command for document ingestion.

Should:

- Accept file path.
- Call `IngestService`.
- Print result: document ID, duplicate status, chunk count, run status.

## `query_command.py`

CLI command for user questions.

Should:

- Accept a natural-language query.
- Call retrieval or agent service.
- Print answer and citations.

## `extract_command.py`

CLI command for structured extraction.

Should:

- Run maintenance task extraction.
- Run spare part extraction.
- Export results if requested.

## `eval_command.py`

CLI command for evaluation.

Should:

- Load evaluation dataset.
- Run evaluation pipeline.
- Print metrics.

---

# `src/config/`

Configuration layer.

## `settings.py`

Central settings file.

Should use Pydantic Settings or similar.

Should contain:

- `DATABASE_URL`
- `QDRANT_PATH`
- `QDRANT_COLLECTION`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `EMBEDDING_MODEL`
- chunk size settings
- retrieval top-k settings

This is the file you update when switching from SQLite to PostgreSQL.

## `logging.py`

Logging configuration.

Should define:

- log level
- log format
- file logging path
- console logging

---

# `src/shared/`

Shared helpers used across the codebase.

This folder should not contain business logic.

## `ids.py`

ID generation helpers.

Should provide functions like:

```python
new_id("doc")
new_id("chunk")
new_id("run")
```

## `time.py`

UTC time helper.

Should provide:

```python
utc_now()
```

## `hashing.py`

Hash utilities.

Should contain:

- SHA256 file hash.
- SHA256 content hash.
- text normalization for content hashing.

## `exceptions.py`

Project-specific exceptions.

Examples:

- `DocumentAlreadyExistsError`
- `ParsingError`
- `ClassificationError`
- `RetrievalError`
- `GuardrailViolationError`

## `constants.py`

Shared constants.

Examples:

- default chunk size
- default overlap size
- default top-k retrieval value
- supported document extensions

---

# `src/domain/`

Pure domain models.

Rules:

- No SQLAlchemy.
- No Docling imports.
- No Qdrant imports.
- No Ollama imports.
- No external infrastructure logic.

## `enums.py`

Domain enums.

Should include:

- `DocumentType`
- `ChunkType`
- `ElementType`
- `IdentifierType`
- `IngestionStatus`
- `ExtractionStatus`
- `RetrievalMode`

Important distinction:

```text
DocumentType = what kind of document is this?
ChunkType = what kind of content is inside this chunk?
```

Example:

```text
DocumentType.MAINTENANCE_MANUAL
ChunkType.MAINTENANCE_INTERVAL
```

## `metadata.py`

Reusable metadata objects.

Should contain:

- `SourceLocation`: page, bbox, source reference.
- `AuditMetadata`: created_at, updated_at, created_by.
- `ParserMetadata`: parser name, version, raw source type.
- `ModelProcessingMetadata`: model name, prompt version, confidence.

## `document_models.py`

Core document graph models.

Should contain:

- `ParsedDocument`
- `CanonicalElement`
- `DocumentSection`
- `DocumentChunk`
- `GeneratedQuestion`
- `Identifier`
- `TableAsset`
- `PictureAsset`
- `ChunkVector`
- `IngestionRun`

Important rules:

- Elements are source units.
- Sections reference elements.
- Chunks are retrieval units.
- Questions belong to chunks.
- Pictures and tables are assets.

## `extraction_models.py`

Structured extraction domain models.

Should contain:

- `MaintenanceTask`
- `MaintenanceInterval`
- `SparePart`
- `EquipmentInfo`
- `ManufacturerInfo`
- `SafetyNote`

These are the extracted business facts.

## `memory_models.py`

Memory-related domain models.

Should contain:

- conversation memory item
- short-term memory state
- long-term memory reference
- memory retrieval result

## `event_models.py`

Domain event base models.

Should contain:

- base event model
- event metadata
- event type enum

---

# `src/application/contracts/`

Application interfaces.

The application layer depends on these contracts, not on concrete infrastructure.

Infrastructure implements these contracts.

## `document_repository.py`

Repository contract for document storage.

Should define methods like:

- `create_ingestion_run()`
- `find_by_file_hash()`
- `find_by_content_hash()`
- `save_document_graph()`
- `save_chunks()`
- `get_document()`

## `extraction_repository.py`

Contract for storing extracted maintenance data.

Should define:

- save maintenance tasks
- save spare parts
- save equipment info
- get extracted facts by document/component

## `memory_repository.py`

Contract for long-term memory persistence.

Should define:

- save conversation memory
- load memory by session
- save document memory references

## `vector_store.py`

Contract for vector database operations.

Should define:

- `upsert_chunks()`
- `search()`
- `delete_by_document_id()`

## `llm_provider.py`

Contract for LLM generation.

Should define:

- `generate(prompt)`
- optionally `generate_json(prompt, schema)`

## `embedding_provider.py`

Contract for embeddings.

Should define:

- `embed_text(text)`
- `embed_batch(texts)`

## `document_classifier.py`

Contract for document classification.

Should define:

- `classify(document_features)`

## `reranker.py`

Contract for reranking retrieved results.

Should define:

- `rerank(query, results)`

## `ocr_provider.py`

Contract for OCR.

Should define:

- `extract_text_from_image(image_path)`

## `event_bus.py`

Contract for publishing application events.

Should define:

- `publish(event)`
- `subscribe(event_type, handler)`

## `workflow_runner.py`

Contract for running workflows.

Can be implemented by LangGraph or simpler custom runners.

## `tool.py`

Base contract for agent tools.

Should define:

- tool name
- input schema
- output schema
- execute method

---

# `src/application/events/`

Application events.

Events make the system easier to extend without coupling modules together.

Example:

- document ingested
- document classified
- chunks generated
- extraction completed
- retrieval completed

## `events/common/event_bus.py`

Application-level event bus abstraction or simple in-memory event bus.

## `events/common/event_dispatcher.py`

Dispatches events to registered handlers.

## `events/common/event_handler.py`

Base event handler contract.

## `events/common/event_result.py`

Represents event handling result.

## `events/ingestion/ingestion_events.py`

Ingestion events.

Should include:

- `IngestionStarted`
- `FileDuplicateDetected`
- `ContentDuplicateDetected`
- `DocumentParsed`
- `ChunksBuilt`
- `VectorsStored`
- `IngestionCompleted`
- `IngestionFailed`

## `events/ingestion/ingestion_event_handlers.py`

Handlers for ingestion events.

Can log events, update metrics, or trigger follow-up processing.

## `events/classification/classification_events.py`

Classification events.

Should include:

- `DocumentClassificationStarted`
- `DocumentClassified`
- `DocumentClassificationFailed`

## `events/classification/classification_event_handlers.py`

Handlers for classification events.

## `events/extraction/extraction_events.py`

Extraction events.

Should include:

- `ExtractionStarted`
- `MaintenanceTasksExtracted`
- `SparePartsExtracted`
- `ExtractionCompleted`
- `ExtractionFailed`

## `events/extraction/extraction_event_handlers.py`

Handlers for extraction events.

## `events/retrieval/retrieval_events.py`

Retrieval events.

Should include:

- `QueryReceived`
- `QueryAnalyzed`
- `ChunksRetrieved`
- `AnswerGenerated`
- `RetrievalFailed`

## `events/retrieval/retrieval_event_handlers.py`

Handlers for retrieval events.

## `events/finalization/final_result_events.py`

Final result events.

Used when a user-facing answer or export is completed.

## `events/finalization/final_result_event_handlers.py`

Handlers for final result events.

---

# `src/application/validation/`

Validation is separate from guardrails.

Validation checks object correctness.

Guardrails check safety, evidence, and runtime policy.

## `validation/common/validation_result.py`

Shared validation result object.

Should include:

- `is_valid`
- errors
- warnings

## `validation/common/validation_error.py`

Validation error structure.

Should contain:

- field
- message
- severity
- code

## `validation/common/validation_context.py`

Context passed to validators.

## `validation/ingestion/document_validator.py`

Validates `ParsedDocument`.

Checks:

- document ID exists
- file path exists
- page count is valid
- document has elements

## `validation/ingestion/element_validator.py`

Validates `CanonicalElement`.

Checks:

- element ID exists
- element type is valid
- page numbers are valid
- parent section reference is valid when assigned

## `validation/ingestion/section_validator.py`

Validates `DocumentSection`.

Checks:

- section title exists
- page range is valid
- element IDs exist
- parent section references are valid

## `validation/ingestion/chunk_validator.py`

Validates `DocumentChunk`.

Checks:

- chunk has text
- chunk has source element IDs
- chunk has page references
- chunk type is valid

## `validation/ingestion/asset_validator.py`

Validates table and picture assets.

Checks:

- asset ID exists
- asset belongs to document
- image path exists for pictures
- table markdown exists for tables

## `validation/ingestion/ingestion_validator.py`

Full ingestion graph validator.

Runs all ingestion validators together.

## `validation/classification/classification_validator.py`

Validates classification result.

Checks:

- document type is valid
- confidence is within range
- classifier output is not empty

## `validation/classification/classification_schema_validator.py`

Validates LLM classification JSON schema.

## `validation/extraction/extraction_validator.py`

Validates extraction result as a whole.

## `validation/extraction/maintenance_task_validator.py`

Validates maintenance tasks.

Checks:

- task title exists
- interval is present if available
- source chunk ID exists
- task requires review flag is set

## `validation/extraction/spare_part_validator.py`

Validates spare parts.

Checks:

- part number format
- description
- source reference

## `validation/extraction/equipment_info_validator.py`

Validates manufacturer, model, and equipment information.

## `validation/retrieval/retrieval_result_validator.py`

Validates retrieval result.

Checks:

- retrieved chunks exist
- scores exist
- metadata is complete

## `validation/retrieval/retrieved_chunk_validator.py`

Validates each retrieved chunk.

## `validation/retrieval/citation_validator.py`

Validates citation metadata.

## `validation/finalization/final_answer_validator.py`

Validates generated answer.

Checks:

- answer is not empty
- answer has citations for technical claims
- answer does not exceed allowed action scope

## `validation/finalization/final_result_validator.py`

Validates the final result object.

## `validation/finalization/final_output_validator.py`

Validates final CLI/API output formatting.

---

# `src/application/ingestion/`

Ingestion transforms a PDF into a document graph, chunks, questions, vectors, and stored metadata.

## `ingestion/pipeline/ingest_pipeline.py`

Coordinates the full ingestion pipeline.

Should implement the flow:

1. Create IngestionRun
2. Calculate File Hash
3. Check File Duplicate
4. Parse PDF
5. Normalize Elements
6. Calculate Content Hash
7. Check Content Duplicate
8. Build Sections
9. Extract Assets
10. Classify Document
11. Build Chunks
12. Extract Identifiers
13. Generate Questions
14. Build Embedding Text
15. Store SQL
16. Store Qdrant
17. Save Vector Mapping
18. Mark Success

## `ingestion/pipeline/ingest_service.py`

Public application service.

Called by CLI or future API.

Should accept file path and return `IngestResult`.

## `ingestion/pipeline/ingest_context.py`

State object passed through the ingestion pipeline.

Should hold:

- file path
- file hash
- content hash
- document ID
- raw Docling document
- parsed document
- chunks
- generated questions
- vector mappings
- ingestion run ID

## `ingestion/pipeline/ingest_result.py`

Return object for ingestion.

Should include:

- success status
- document ID
- run ID
- duplicate flag
- number of chunks
- error message if failed

## `ingestion/parsing/docling_parser.py`

Calls Docling and returns the raw Docling document.

Should not normalize, chunk, save, or classify.

## `ingestion/parsing/docling_normalizer.py`

Converts Docling typed collections into domain `CanonicalElement` objects.

Should normalize:

- texts
- tables
- pictures
- groups
- key-value items
- form items
- code items
- formulas

## `ingestion/parsing/reading_order_sorter.py`

Sorts canonical elements by source order.

Sorting should consider:

- page
- bounding box y-coordinate
- bounding box x-coordinate
- Docling reading order if available

## `ingestion/builders/section_builder.py`

Builds `DocumentSection` objects from title and section header elements.

## `ingestion/builders/section_mapper.py`

Assigns `parent_section_id` to canonical elements.

This is what links elements back to their section.

## `ingestion/builders/asset_builder.py`

Builds `TableAsset` and `PictureAsset` from table and picture elements.

## `ingestion/builders/picture_mapper.py`

Links pictures to:

- captions
- nearby text
- section
- page
- bbox

## `ingestion/builders/document_graph_builder.py`

Final assembler and relationship checker.

Should ensure:

- sections reference valid elements
- elements reference valid sections
- chunks can later reference valid elements
- assets are linked correctly

## `ingestion/chunking/chunk_builder.py`

Builds retrieval chunks from sections.

Default rule:

```text
1 section ≈ 1 chunk
```

If section is too large, split with overlap.

## `ingestion/chunking/chunk_type_classifier.py`

Assigns chunk content type.

Examples:

- overview
- maintenance procedure
- maintenance interval
- spare parts table
- safety warning
- troubleshooting
- technical specification

## `ingestion/chunking/identifier_extractor.py`

Extracts exact identifiers.

Should use regex and rules first.

Examples:

- part numbers
- model numbers
- serial numbers
- drawing numbers
- component codes

## `ingestion/enrichment/question_generation_service.py`

Uses LLM to generate possible questions each chunk can answer.

Important rule:

Questions must only be answerable from the chunk.

## `ingestion/enrichment/enriched_text_builder.py`

Builds final text used for embeddings.

Should combine:

- section path
- chunk text
- table markdown
- picture captions
- OCR text
- generated questions
- identifiers

## `ingestion/hashing/file_hash_service.py`

Calculates raw file SHA256 hash before parsing.

Used for exact duplicate detection.

## `ingestion/hashing/content_hash_service.py`

Calculates normalized content hash after parsing.

Used to detect same content in regenerated PDFs.

---

# `src/application/classification/`

Document classification subsystem.

## `classification/pipeline/classification_pipeline.py`

Coordinates classification steps.

Should:

- build document features
- run classifier
- validate result
- apply confidence rules

## `classification/pipeline/classification_service.py`

Public classification service.

Called by ingestion pipeline.

## `classification/pipeline/classification_result.py`

Classification result object.

Should include:

- document type
- confidence
- rationale
- classifier name
- model name

## `classification/features/document_feature_builder.py`

Builds classification input features from parsed document.

Should combine:

- title
- first pages
- section headers
- keywords
- table names

## `classification/features/title_feature_extractor.py`

Extracts title-based signals.

## `classification/features/section_feature_extractor.py`

Extracts section header signals.

Example:

- maintenance
- spare parts
- certificate
- specification

## `classification/features/keyword_feature_extractor.py`

Extracts keyword signals.

## `classification/rules/document_type_rules.py`

Rule-based fallback classifier.

Example:

If many sections contain “spare parts”, classify as spare parts catalog.

## `classification/rules/confidence_rules.py`

Confidence thresholds.

Should define when to accept, reject, or mark classification uncertain.

## `classification/schemas/classification_schema.py`

Pydantic schema for LLM classifier output.

---

# `src/application/extraction/`

Structured maintenance knowledge extraction.

## `extraction/pipeline/extraction_pipeline.py`

Coordinates extraction workflows.

Should call maintenance, spare parts, and equipment extractors.

## `extraction/pipeline/extraction_service.py`

Public extraction service.

Called by CLI, tools, or workflows.

## `extraction/pipeline/extraction_context.py`

Extraction pipeline state.

Should contain:

- document ID
- chunks
- classification result
- extracted tasks
- extracted spare parts
- validation results

## `extraction/pipeline/extraction_result.py`

Final extraction result.

## `extraction/maintenance/maintenance_task_extractor.py`

Extracts maintenance tasks from chunks.

Should output structured `MaintenanceTask` objects.

## `extraction/maintenance/maintenance_interval_extractor.py`

Extracts maintenance intervals.

Examples:

- every 1000 hours
- monthly
- annually

## `extraction/maintenance/safety_note_extractor.py`

Extracts safety warnings and caution notes.

## `extraction/maintenance/maintenance_schema.py`

Pydantic schema for maintenance extraction output.

## `extraction/spare_parts/spare_part_extractor.py`

Extracts spare parts from text and tables.

## `extraction/spare_parts/spare_part_table_parser.py`

Deterministic parser for spare parts tables.

Should handle columns such as:

- Part No.
- P/N
- Description
- Quantity
- Manufacturer

## `extraction/spare_parts/spare_part_schema.py`

Pydantic schema for spare part extraction.

## `extraction/equipment/manufacturer_extractor.py`

Extracts manufacturer information.

## `extraction/equipment/model_number_extractor.py`

Extracts model and equipment numbers.

## `extraction/equipment/equipment_schema.py`

Pydantic schema for equipment info.

## `extraction/schemas/extraction_schema.py`

Shared extraction schema definitions.

---

# `src/application/retrieval/`

Hybrid retrieval and RAG answer generation.

## `retrieval/pipeline/retrieval_pipeline.py`

Coordinates retrieval flow.

Steps:

- analyze query
- detect identifiers
- build filters
- run SQL/keyword/dense retrieval
- merge results
- rerank
- build context
- generate answer
- validate citations

## `retrieval/pipeline/retrieval_service.py`

Public retrieval service.

Used by tools and CLI.

## `retrieval/pipeline/retrieval_context.py`

Retrieval state object.

## `retrieval/pipeline/retrieval_result.py`

Structured retrieval result.

## `retrieval/query_analysis/query_analyzer.py`

Analyzes the user query.

Should identify:

- intent
- likely document type
- likely chunk type
- identifiers
- whether query needs exact search or semantic search

## `retrieval/query_analysis/query_type_classifier.py`

Classifies query type.

Examples:

- maintenance question
- spare part question
- document lookup
- manufacturer lookup
- safety question

## `retrieval/query_analysis/identifier_detector.py`

Detects exact technical identifiers in user query.

Examples:

- P/N
- Part No.
- serial numbers
- model codes

## `retrieval/query_analysis/query_rewriter.py`

Rewrites or expands queries.

Example:

```text
part no → part number → P/N
service → maintenance → replace
```

## `retrieval/retrievers/dense_retriever.py`

Vector retrieval using Qdrant.

## `retrieval/retrievers/keyword_retriever.py`

Keyword or BM25 retrieval.

Useful for exact technical terms.

## `retrieval/retrievers/sql_retriever.py`

Structured SQL retrieval.

Used for:

- part numbers
- extracted tasks
- manufacturers
- document metadata

## `retrieval/retrievers/hybrid_retriever.py`

Combines dense, keyword, and SQL retrieval.

## `retrieval/ranking/result_merger.py`

Merges results from multiple retrievers.

## `retrieval/ranking/reranker.py`

Reranks retrieved chunks.

Can use simple scoring or cross-encoder reranking.

## `retrieval/ranking/score_normalizer.py`

Normalizes scores from different retrieval methods.

## `retrieval/filters/metadata_filter_builder.py`

Builds filters for vector search.

## `retrieval/filters/document_type_filter.py`

Filters by document type.

## `retrieval/filters/chunk_type_filter.py`

Filters by chunk type.

## `retrieval/answering/answer_service.py`

Generates final user-facing answer.

Should use LLM only after retrieval.

## `retrieval/answering/context_builder.py`

Builds prompt context from retrieved chunks.

## `retrieval/answering/citation_builder.py`

Builds citations from metadata.

Important: citations should come from metadata, not from LLM imagination.

## `retrieval/answering/answer_result.py`

Structured final answer object.

---

# `src/application/agent/`

Agent runtime and planning.

The agent coordinates user requests and tools.

The LLM should not directly execute tools. Python executes tools through the registry.

## `agent/runtime/agent_runtime.py`

Runs the agent loop.

Should:

- receive user query
- create agent state
- route intent
- select tools
- execute tools
- apply guardrails
- return final answer

## `agent/runtime/agent_state.py`

Mutable state for one agent run.

## `agent/runtime/agent_context.py`

Context shared across the agent runtime.

## `agent/runtime/agent_result.py`

Final agent output.

## `agent/planning/intent_router.py`

Maps user intent to workflow/tool path.

## `agent/planning/tool_selector.py`

Selects allowed tool based on intent.

## `agent/planning/agent_policy.py`

Defines policy rules.

Examples:

- allowed tools
- blocked actions
- max tool calls
- human-review requirements

## `agent/registry/tool_registry.py`

Registers tools by name.

## `agent/registry/tool_call.py`

Represents a tool call request.

## `agent/registry/tool_result.py`

Represents tool execution result.

## `agent/registry/tool_schema.py`

Tool input/output schemas.

---

# `src/application/tools/`

Agent-callable tools.

Tools wrap application services.

They should not directly use SQLAlchemy or Qdrant unless through services/contracts.

## `tools/retrieval/retrieve_chunks_tool.py`

Tool for retrieving chunks.

Uses retrieval service.

## `tools/retrieval/search_identifier_tool.py`

Tool for exact identifier search.

Used for part numbers, model numbers, and serial numbers.

## `tools/retrieval/get_chunk_tool.py`

Tool for loading a chunk by ID.

## `tools/document/get_document_tool.py`

Tool for document metadata lookup.

## `tools/document/list_documents_tool.py`

Tool for listing ingested documents.

## `tools/document/get_document_sections_tool.py`

Tool for getting sections of a document.

## `tools/extraction/extract_tasks_tool.py`

Tool for extracting maintenance tasks.

## `tools/extraction/extract_spare_parts_tool.py`

Tool for extracting spare parts.

## `tools/extraction/extract_equipment_info_tool.py`

Tool for extracting manufacturer/model/equipment data.

## `tools/answering/answer_with_context_tool.py`

Tool for generating a grounded answer from retrieved context.

---

# `src/application/guardrails/`

Guardrails enforce safety, reliability, and source-grounding.

Guardrails are different from validation.

Validation checks object correctness.

Guardrails check runtime policy and safety.

## `guardrails/common/guardrail_result.py`

Common result object.

Should include:

- allowed
- severity
- message
- violations

## `guardrails/common/guardrail_context.py`

Context passed to guardrails.

## `guardrails/common/guardrail_severity.py`

Severity enum.

Examples:

- info
- warning
- block

## `guardrails/evidence/evidence_guardrail.py`

Ensures technical answers have retrieved evidence.

## `guardrails/evidence/evidence_thresholds.py`

Defines minimum retrieval score or evidence count.

## `guardrails/citations/citation_guardrail.py`

Ensures citations are present.

## `guardrails/citations/citation_policy.py`

Defines citation rules.

Example:

Every technical answer must include document, section, page, and chunk reference.

## `guardrails/schemas/schema_guardrail.py`

Validates LLM outputs against Pydantic schemas.

## `guardrails/schemas/schema_validation_result.py`

Result object for schema validation.

## `guardrails/confidence/confidence_guardrail.py`

Checks confidence thresholds.

## `guardrails/confidence/confidence_policy.py`

Defines threshold rules.

## `guardrails/actions/action_guardrail.py`

Controls which actions/tools are allowed.

Blocks unsafe operations.

## `guardrails/actions/allowed_actions.py`

Defines allowed and blocked actions.

Allowed:

- retrieve
- extract
- summarize
- answer

Blocked:

- create work order
- delete documents
- write to CMMS
- make final maintenance decision

## `guardrails/safety/maintenance_safety_guardrail.py`

Maintenance-specific safety rules.

Should mark extracted tasks as draft/requires human review.

## `guardrails/safety/human_review_policy.py`

Defines when human review is required.

---

# `src/application/memory/`

Memory layer.

Memory is external to the LLM.

## `memory/short_term/conversation_memory.py`

Stores current conversation turns.

## `memory/short_term/graph_memory.py`

Stores LangGraph workflow state memory.

## `memory/short_term/memory_state.py`

Short-term memory state object.

## `memory/long_term/document_memory.py`

Long-term memory related to documents.

## `memory/long_term/identifier_memory.py`

Long-term memory for exact identifiers.

## `memory/long_term/memory_service.py`

Memory application service.

## `memory/retrieval/memory_retriever.py`

Retrieves memory items.

## `memory/retrieval/memory_context_builder.py`

Builds memory context for prompts.

---

# `src/application/workflows/`

LangGraph workflow definitions.

LangGraph belongs in application because it orchestrates business workflows.

## `workflows/common/graph_state.py`

Base graph state definitions.

## `workflows/common/graph_result.py`

Common graph result object.

## `workflows/common/workflow_context.py`

Shared workflow context.

## `workflows/common/workflow_registry.py`

Registry for available graphs.

## `workflows/ingestion/ingestion_graph.py`

LangGraph graph for ingestion.

## `workflows/ingestion/ingestion_state.py`

State object for ingestion graph.

## `workflows/ingestion/ingestion_nodes.py`

Node functions for ingestion steps.

Examples:

- calculate file hash
- parse PDF
- normalize elements
- build chunks
- store vectors

## `workflows/ingestion/ingestion_edges.py`

Defines graph edges.

## `workflows/ingestion/ingestion_router.py`

Conditional routing.

Example:

If duplicate detected, skip parsing.

## `workflows/classification/classification_graph.py`

LangGraph classification workflow.

## `workflows/classification/classification_nodes.py`

Classification graph nodes.

## `workflows/classification/classification_state.py`

Classification graph state.

## `workflows/extraction/extraction_graph.py`

LangGraph extraction workflow.

## `workflows/extraction/extraction_nodes.py`

Extraction graph nodes.

## `workflows/extraction/extraction_state.py`

Extraction graph state.

## `workflows/retrieval/retrieval_graph.py`

LangGraph retrieval workflow.

## `workflows/retrieval/retrieval_nodes.py`

Retrieval graph nodes.

## `workflows/retrieval/retrieval_state.py`

Retrieval graph state.

## `workflows/agent/agent_graph.py`

LangGraph ReAct-style agent graph.

## `workflows/agent/agent_nodes.py`

Agent graph nodes.

Examples:

- analyze query
- select tool
- execute tool
- check evidence
- generate answer

## `workflows/agent/agent_router.py`

Conditional routing for agent graph.

## `workflows/agent/agent_state.py`

Agent graph state.

## `workflows/agent/agent_checkpoint.py`

Checkpoint support for graph state.

---

# `src/application/evaluation/`

Evaluation framework.

## `evaluation/datasets/eval_dataset_loader.py`

Loads evaluation datasets.

Dataset examples:

- questions
- expected answers
- expected page references
- expected document type
- expected extracted fields

## `evaluation/metrics/classification_metrics.py`

Metrics for document classification.

## `evaluation/metrics/retrieval_metrics.py`

Metrics for retrieval.

Examples:

- hit rate
- top-k accuracy
- citation validity

## `evaluation/metrics/extraction_metrics.py`

Metrics for extracted tasks and spare parts.

Examples:

- precision
- recall
- field-level accuracy

## `evaluation/runners/evaluation_runner.py`

Runs evaluation and writes reports.

---

# `src/infrastructure/`

Concrete external implementations.

Infrastructure implements application contracts.

The application should not depend directly on infrastructure.

---

## `infrastructure/db/`

SQLAlchemy + Alembic database implementation.

## `infrastructure/db/base.py`

SQLAlchemy declarative base.

## `infrastructure/db/session.py`

Central database engine and session factory.

This is where `DATABASE_URL` is used.

Switching SQLite to PostgreSQL should mostly require changing `.env` and this infrastructure layer.

## `infrastructure/db/orm_models.py`

SQLAlchemy ORM models.

Should include tables for:

- documents
- ingestion runs
- elements
- sections
- chunks
- tables
- pictures
- generated questions
- identifiers
- classifications
- extractions
- memory
- vector mappings

## `infrastructure/db/repositories/document_repository.py`

SQLAlchemy implementation of document repository contract.

## `infrastructure/db/repositories/chunk_repository.py`

SQLAlchemy chunk repository.

## `infrastructure/db/repositories/ingestion_run_repository.py`

SQLAlchemy ingestion run repository.

## `infrastructure/db/repositories/classification_repository.py`

SQLAlchemy classification repository.

## `infrastructure/db/repositories/extraction_repository.py`

SQLAlchemy extraction repository.

## `infrastructure/db/repositories/memory_repository.py`

SQLAlchemy memory repository.

## `infrastructure/db/repositories/identifier_repository.py`

SQLAlchemy identifier repository.

## `infrastructure/db/repositories/vector_mapping_repository.py`

Stores mapping between local chunks and Qdrant point IDs.

## `infrastructure/db/unit_of_work.py`

Transaction boundary manager.

Should coordinate repository commits and rollbacks.

---

## `infrastructure/vectorstores/`

Vector database implementation.

## `vectorstores/qdrant_client.py`

Creates Qdrant client.

## `vectorstores/qdrant_payload_builder.py`

Builds Qdrant payloads from chunks.

Payload should include:

- document ID
- chunk ID
- document type
- chunk type
- section path
- page references
- identifiers

## `vectorstores/qdrant_vector_store.py`

Implements vector store contract using Qdrant.

---

## `infrastructure/embeddings/`

Embedding model implementations.

## `sentence_transformer_provider.py`

Implements embedding provider using SentenceTransformers.

Should support:

- single text embedding
- batch embedding

---

## `infrastructure/llm/`

LLM implementations and prompts.

## `llm/ollama_provider.py`

Implements LLM provider using Ollama.

Should support:

- generate text
- generate JSON
- timeout handling
- retry handling

## `llm/prompts/document_classifier_prompt.py`

Prompt for document classification.

## `llm/prompts/chunk_question_prompt.py`

Prompt for generated questions per chunk.

## `llm/prompts/chunk_type_prompt.py`

Prompt for chunk type classification if LLM-based.

## `llm/prompts/extraction_prompt.py`

Prompt for structured extraction.

## `llm/prompts/query_rewrite_prompt.py`

Prompt for query rewriting.

## `llm/prompts/answer_generation_prompt.py`

Prompt for answer generation from retrieved context.

---

## `infrastructure/classifiers/`

Concrete document classifier implementations.

## `ollama_document_classifier.py`

LLM-based document classifier.

## `rule_based_document_classifier.py`

Rule-based fallback classifier.

---

## `infrastructure/rerankers/`

Concrete reranker implementations.

## `simple_score_reranker.py`

Simple reranker using weighted retrieval scores.

## `cross_encoder_reranker.py`

Cross-encoder reranker implementation.

Optional for MVP.

---

## `infrastructure/ocr/`

OCR implementations.

## `paddle_ocr_provider.py`

OCR provider for image/drawing text extraction.

Should extract labels from drawings and figures.

---

# Architectural Rules

## Dependency Direction

```text
Domain ← Application ← Infrastructure
```

Rules:

1. Domain imports nothing from application or infrastructure.
2. Application imports domain and contracts.
3. Infrastructure imports application contracts and implements them.
4. CLI calls application services only.
5. SQLAlchemy must stay inside infrastructure/db.
6. Qdrant must stay inside infrastructure/vectorstores.
7. Ollama must stay inside infrastructure/llm or infrastructure/classifiers.
8. LangGraph workflows belong in application/workflows.

---

# Ingestion Flow Ownership

```text
1. Create IngestionRun
   infrastructure/db/repositories/ingestion_run_repository.py

2. Calculate File Hash
   application/ingestion/hashing/file_hash_service.py

3. Check File Duplicate
   infrastructure/db/repositories/document_repository.py

4. Parse PDF
   application/ingestion/parsing/docling_parser.py

5. Normalize Elements
   application/ingestion/parsing/docling_normalizer.py

6. Calculate Content Hash
   application/ingestion/hashing/content_hash_service.py

7. Check Content Duplicate
   infrastructure/db/repositories/document_repository.py

8. Build Sections
   application/ingestion/builders/section_builder.py

9. Extract Assets
   application/ingestion/builders/asset_builder.py

10. Classify Document
   application/classification/pipeline/classification_service.py

11. Build Chunks
   application/ingestion/chunking/chunk_builder.py

12. Extract Identifiers
   application/ingestion/chunking/identifier_extractor.py

13. Generate Questions
   application/ingestion/enrichment/question_generation_service.py

14. Build Embedding Text
   application/ingestion/enrichment/enriched_text_builder.py

15. Store SQL
   infrastructure/db/repositories/

16. Store Qdrant
   infrastructure/vectorstores/qdrant_vector_store.py

17. Store Vector Mapping
   infrastructure/db/repositories/vector_mapping_repository.py

18. Mark Success
   infrastructure/db/repositories/ingestion_run_repository.py
```

---

# Implementation Phases

## Phase 1 — Foundation

Build:

- config
- shared
- domain
- SQLAlchemy base/session/models
- Alembic setup

## Phase 2 — Ingestion Graph

Build:

- file hash
- Docling parser
- normalizer
- section builder
- chunk builder
- SQLite storage

## Phase 3 — Qdrant

Build:

- embedding provider
- Qdrant client
- Qdrant vector store
- vector mapping repository

## Phase 4 — Classification

Build:

- document features
- rule-based classifier
- Ollama classifier
- classification validation

## Phase 5 — Enrichment

Build:

- generated questions
- enriched embedding text
- identifier extraction

## Phase 6 — Retrieval

Build:

- query analysis
- SQL retriever
- dense retriever
- hybrid retriever
- citation builder

## Phase 7 — Extraction

Build:

- maintenance task extraction
- spare part extraction
- equipment info extraction

## Phase 8 — Agent + Guardrails

Build:

- tool registry
- agent runtime
- action guardrail
- evidence guardrail
- citation guardrail

## Phase 9 — LangGraph

Build:

- ingestion graph
- retrieval graph
- agent graph

## Phase 10 — Evaluation

Build:

- evaluation dataset
- metrics
- evaluation runner

---

# Final Notes

This architecture is intentionally larger than the 3-week MVP implementation.

For the capstone, implement only the core path first:

```text
PDF → Docling → Canonical Elements → Sections → Chunks → SQLite → Qdrant → RAG Answer
```

Then add:

```text
classification → identifiers → generated questions → extraction → guardrails → LangGraph
```

The full structure is designed so the project can grow without becoming a monolithic script.
