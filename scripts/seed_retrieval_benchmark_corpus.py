from __future__ import annotations

"""
Seed the retrieval benchmark corpus with the existing workflow chain only.

Usage:
    python scripts/seed_retrieval_benchmark_corpus.py
    python scripts/seed_retrieval_benchmark_corpus.py --truth-set TestDoc/retrieval_truth_set.md
"""

import argparse
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

for import_root in (PROJECT_ROOT, SRC_ROOT):
    import_root_text = str(import_root)
    if import_root_text not in sys.path:
        sys.path.insert(0, import_root_text)

from qdrant_client import QdrantClient  # noqa: E402
from qdrant_client.models import Distance, VectorParams  # noqa: E402

from src.application.evaluation.retrieval import (  # noqa: E402
    DEFAULT_RETRIEVAL_TRUTH_SET_PATH,
    RetrievalBenchmarkCorpusSeeder,
)
from src.application.services.ai import (  # noqa: E402
    EmbeddingService,
    LLMService,
)
from src.application.services.classification import ClassificationService  # noqa: E402
from src.application.services.document import (  # noqa: E402
    DocumentLookupService,
    DocumentRegistrationService,
    DuplicateDetectionService,
)
from src.application.services.question_generation import (  # noqa: E402
    QuestionGenerationService,
)
from src.application.validation.classification import (  # noqa: E402
    ChunkClassificationValidator,
    DocumentClassificationValidator,
)
from src.application.validation.document import DocumentGraphValidator  # noqa: E402
from src.application.workflows.classification import (  # noqa: E402
    ChunkClassificationWorkflow,
    ChunkTypeClassificationWorkflow,
    DocumentClassificationWorkflow,
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.embedding import EmbeddingWorkflow  # noqa: E402
from src.application.workflows.parsing import ParsingWorkflow  # noqa: E402
from src.application.workflows.parsing.ocr import (  # noqa: E402
    build_parsing_ocr_runtime,
)
from src.application.workflows.parsing.builders import (  # noqa: E402
    DocumentGraphBuilder,
    SectionBuilder,
)
from src.application.workflows.parsing.normalizers import (  # noqa: E402
    DoclingDocumentNormalizer,
)
from src.bootstrap.startup import bootstrap_application  # noqa: E402
from src.config.paths import ensure_directory, resolve_project_path  # noqa: E402
from src.config.settings import (  # noqa: E402
    docling_settings,
    embedding_settings,
    llm_settings,
    ocr_settings,
    qdrant_settings,
    storage_settings,
)
from src.infrastructure.ai.embeddings import create_embedding_provider  # noqa: E402
from src.infrastructure.ai.llm import OllamaLLMProvider  # noqa: E402
from src.infrastructure.db.base import Base  # noqa: E402
from src.infrastructure.db.orm_models import __all__ as _orm_models_loaded  # noqa: E402,F401
from src.infrastructure.db.session import SessionLocal, engine  # noqa: E402
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork  # noqa: E402
from src.infrastructure.parsing.docling import DoclingParser  # noqa: E402
from src.infrastructure.retrieval.vector import QdrantVectorStore  # noqa: E402
from src.shared.ids import IdGenerator  # noqa: E402


@dataclass(slots=True)
class CorpusSeederRuntime:
    seeder: RetrievalBenchmarkCorpusSeeder
    qdrant_client: QdrantClient | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Seed the retrieval benchmark corpus using the existing parsing, "
            "classification, chunk finalization, question generation, and "
            "embedding workflows."
        )
    )
    parser.add_argument(
        "--truth-set",
        default=str(DEFAULT_RETRIEVAL_TRUTH_SET_PATH),
        help="Optional truth-set markdown path.",
    )
    parser.add_argument(
        "--input-dir",
        help=(
            "Optional directory containing the benchmark PDFs. "
            "Defaults to the truth-set parent directory."
        ),
    )
    parser.add_argument(
        "--output",
        help=(
            "Optional manifest output path. Defaults to "
            "outputs/evaluation/retrieval/benchmark_corpus_manifest.json"
        ),
    )
    parser.add_argument(
        "--force-reparse",
        action="store_true",
        help=(
            "Reparse and replace full persisted document graphs when an input file "
            "already exists instead of reusing the stored graph."
        ),
    )
    return parser.parse_args()


def print_status(message: str) -> None:
    print(f"[seed-retrieval-corpus] {message}", flush=True)


def print_runtime_ocr_configuration() -> None:
    print_status(
        "Docling pipeline: "
        f"pdf_backend={docling_settings.pdf_backend}, "
        f"device={docling_settings.accelerator_device}, "
        f"images_scale={docling_settings.images_scale}, "
        f"table_structure={docling_settings.enable_table_structure}, "
        f"num_threads={docling_settings.num_threads}, "
        f"layout_batch_size={docling_settings.layout_batch_size}, "
        f"table_batch_size={docling_settings.table_batch_size}"
    )
    print_status(
        "Docling OCR: "
        f"enabled={docling_settings.enable_ocr}, "
        f"engine={docling_settings.ocr_engine}, "
        f"batch_size={docling_settings.ocr_batch_size}"
    )
    print_status(
        "Provider OCR: "
        f"enabled={ocr_settings.enabled}, "
        f"provider={ocr_settings.provider}"
    )
    print_status(
        "OCR fallback: "
        f"asset={ocr_settings.asset_enabled}, "
        f"page_fallback={ocr_settings.page_fallback_enabled}, "
        f"region_fallback={ocr_settings.region_fallback_enabled}, "
        f"trace={ocr_settings.trace_enabled}"
    )


def resolve_path(value: str | None) -> Path | None:
    if value is None:
        return None
    return resolve_project_path(value).expanduser().resolve()


def default_output_path() -> Path:
    return (
        storage_settings.evaluation_output_path
        / "retrieval"
        / "benchmark_corpus_manifest.json"
    ).resolve()


def create_qdrant_client() -> QdrantClient:
    if qdrant_settings.mode.lower() == "local":
        return QdrantClient(path=str(qdrant_settings.storage_path))

    return QdrantClient(
        host=qdrant_settings.host,
        port=qdrant_settings.port,
    )


def ensure_qdrant_collection(client: QdrantClient) -> None:
    if client.collection_exists(qdrant_settings.collection):
        return

    client.create_collection(
        collection_name=qdrant_settings.collection,
        vectors_config=VectorParams(
            size=embedding_settings.dimensions,
            distance=resolve_distance(qdrant_settings.vector_distance),
        ),
    )


def resolve_distance(value: str) -> Distance:
    normalized = value.strip().lower()
    mapping = {
        "cosine": Distance.COSINE,
        "dot": Distance.DOT,
        "euclid": Distance.EUCLID,
        "manhattan": Distance.MANHATTAN,
    }
    return mapping.get(normalized, Distance.COSINE)


def build_parsing_workflow(
    *,
    id_generator: IdGenerator,
) -> tuple[ParsingWorkflow, DocumentGraphBuilder]:
    ocr_runtime = build_parsing_ocr_runtime(id_generator=id_generator)
    section_builder = SectionBuilder(id_generator)
    document_graph_builder = DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=section_builder,
    )
    workflow = ParsingWorkflow(
        parser=DoclingParser(),
        normalizer=DoclingDocumentNormalizer(),
        document_graph_builder=document_graph_builder,
        id_generator=id_generator,
        document_graph_validator=DocumentGraphValidator(),
        canonical_element_ocr_enricher=ocr_runtime.canonical_element_ocr_enricher,
        page_ocr_fallback_workflow=ocr_runtime.page_ocr_fallback_workflow,
    )
    return workflow, document_graph_builder


def build_corpus_seeder() -> CorpusSeederRuntime:
    bootstrap_application()
    Base.metadata.create_all(engine)

    id_generator = IdGenerator()
    parsing_workflow, document_graph_builder = build_parsing_workflow(
        id_generator=id_generator,
    )

    session = SessionLocal()
    uow = SqlAlchemyUnitOfWork(session)
    llm_service = LLMService(
        OllamaLLMProvider(
            base_url=llm_settings.ollama_base_url,
            default_model=llm_settings.general_llm,
        )
    )
    embedding_provider = create_embedding_provider()
    qdrant_client = create_qdrant_client()
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        mapping_repository=uow.vector_mappings,
        collection_name=qdrant_settings.collection,
        embedding_model=embedding_settings.model_name,
        query_embedding_provider=embedding_provider,
        document_repository=uow.documents,
    )
    ensure_qdrant_collection(vector_store.client)

    document_repository = uow.documents
    classification_repository = uow.classifications
    document_graph_validator = DocumentGraphValidator()
    document_validator = DocumentClassificationValidator()
    chunk_validator = ChunkClassificationValidator()
    document_lookup_service = DocumentLookupService(document_repository)
    document_registration_service = DocumentRegistrationService(
        document_repository=document_repository,
        document_graph_validator=document_graph_validator,
    )

    classification_service = ClassificationService(
        classification_repository=classification_repository,
        document_classification_validator=document_validator,
        chunk_classification_validator=chunk_validator,
    )
    chunk_classification_workflow = ChunkClassificationWorkflow(
        llm_service=llm_service,
        classification_service=classification_service,
        chunk_classification_validator=chunk_validator,
        id_generator=id_generator,
    )

    return CorpusSeederRuntime(
        seeder=RetrievalBenchmarkCorpusSeeder(
            parsing_workflow=parsing_workflow,
            document_registration_service=document_registration_service,
            duplicate_detection_service=DuplicateDetectionService(document_repository),
            document_lookup_service=document_lookup_service,
            classification_service=classification_service,
            document_classification_workflow=DocumentClassificationWorkflow(
                llm_service=llm_service,
                classification_service=classification_service,
                document_classification_validator=document_validator,
                id_generator=id_generator,
            ),
            post_classification_chunk_finalization_workflow=(
                PostClassificationChunkFinalizationWorkflow(
                    document_lookup_service=document_lookup_service,
                    document_registration_service=document_registration_service,
                    classification_service=classification_service,
                    chunk_classification_workflow=chunk_classification_workflow,
                    chunk_type_classification_workflow=ChunkTypeClassificationWorkflow(
                        llm_service=llm_service,
                    ),
                    question_generation_service=QuestionGenerationService(
                        llm_service=llm_service,
                        id_generator=id_generator,
                    ),
                    embedding_workflow=EmbeddingWorkflow(
                        embedding_service=EmbeddingService(embedding_provider),
                        vector_store=vector_store,
                    ),
                    vector_store=vector_store,
                    graph_chunk_builder=document_graph_builder.chunk_builder,
                )
            ),
            unit_of_work=uow,
            embedding_model=embedding_settings.model_name,
            vector_collection=qdrant_settings.collection,
        ),
        qdrant_client=qdrant_client,
    )


def main() -> int:
    args = parse_args()
    runtime: CorpusSeederRuntime | None = None
    seeder: RetrievalBenchmarkCorpusSeeder | None = None
    truth_set_path = resolve_path(args.truth_set)
    input_directory = resolve_path(args.input_dir)
    output_path = resolve_path(args.output) or default_output_path()
    ensure_directory(output_path.parent)

    print_status(f"Truth set path: {truth_set_path}")
    if input_directory is None:
        print_status("Input directory: derived from the truth-set parent directory")
    else:
        print_status(f"Input directory: {input_directory}")
    print_status(f"Manifest output path: {output_path}")
    print_status(
        "Duplicate handling: "
        + (
            "force reparse existing documents"
            if args.force_reparse
            else "reuse existing persisted graphs when file hash matches"
        )
    )
    print_runtime_ocr_configuration()
    print_status("Building corpus seeder runtime...")
    runtime = build_corpus_seeder()
    seeder = runtime.seeder
    print_status("Corpus seeder runtime ready.")

    try:
        print_status("Starting retrieval benchmark corpus seeding...")
        manifest = seeder.seed_corpus(
            truth_set_path=truth_set_path,
            input_directory=input_directory,
            force_reparse_existing=args.force_reparse,
            progress_callback=print_status,
        )
        print_status(
            f"Writing manifest for {manifest.document_count} document(s)..."
        )
        output_path.write_text(
            json.dumps(manifest.to_dict(), indent=2),
            encoding="utf-8",
        )
        print_status("Corpus manifest written successfully.")
    except Exception:
        unit_of_work = getattr(seeder, "unit_of_work", None)
        if unit_of_work is not None:
            unit_of_work.rollback()
        traceback.print_exc()
        return 1
    finally:
        unit_of_work = getattr(seeder, "unit_of_work", None)
        session = getattr(unit_of_work, "session", None)
        if session is not None:
            session.close()
        close_quietly(getattr(runtime, "qdrant_client", None))

    print(output_path)
    return 0


def close_quietly(resource) -> None:
    if resource is None:
        return

    close = getattr(resource, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            return


if __name__ == "__main__":
    raise SystemExit(main())
