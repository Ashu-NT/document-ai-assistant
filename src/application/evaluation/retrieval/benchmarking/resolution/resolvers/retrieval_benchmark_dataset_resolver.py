from src.application.evaluation.retrieval.benchmarking.corpus.models import (
    RetrievalBenchmarkCorpusDocument,
    RetrievalBenchmarkCorpusManifest,
)
from src.application.evaluation.retrieval.benchmarking.datasets import (
    RetrievalBenchmarkDataset,
)
from src.application.evaluation.retrieval.benchmarking.models import (
    RetrievalBenchmarkCase,
)
from src.application.evaluation.retrieval.benchmarking.resolution.models import (
    RetrievalBenchmarkResolutionDiagnostic,
)
from src.application.evaluation.retrieval.benchmarking.resolution.resolvers.retrieval_benchmark_case_resolver import (
    RetrievalBenchmarkCaseResolver,
)
from src.application.services.document import DocumentLookupService
from src.domain.document import DocumentGraph
from src.shared.activity import ActivityContext
from src.shared.exceptions import SchemaValidationError


class RetrievalBenchmarkDatasetResolver:
    def __init__(
        self,
        *,
        document_lookup_service: DocumentLookupService,
        case_resolver: RetrievalBenchmarkCaseResolver | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.case_resolver = case_resolver or RetrievalBenchmarkCaseResolver()

    def resolve_dataset(
        self,
        dataset: RetrievalBenchmarkDataset,
        corpus_manifest: RetrievalBenchmarkCorpusManifest,
        *,
        activity_context: ActivityContext | None = None,
    ) -> RetrievalBenchmarkDataset:
        graph_cache: dict[str, DocumentGraph] = {}
        resolved_cases: list[RetrievalBenchmarkCase] = []
        diagnostics: list[RetrievalBenchmarkResolutionDiagnostic] = []

        manifest_documents_by_alias = {
            document.document_alias: document
            for document in corpus_manifest.documents
        }
        manifest_documents_by_file_name = {
            document.file_name: document
            for document in corpus_manifest.documents
        }

        for benchmark_case in dataset.cases:
            manifest_document, manifest_diagnostic = self._resolve_manifest_document(
                benchmark_case=benchmark_case,
                manifest_documents_by_alias=manifest_documents_by_alias,
                manifest_documents_by_file_name=manifest_documents_by_file_name,
            )
            if manifest_diagnostic is not None:
                diagnostics.append(manifest_diagnostic)
                continue

            document_graph = self._load_document_graph(
                manifest_document.document_id,
                graph_cache=graph_cache,
                activity_context=activity_context,
            )
            if document_graph is None:
                diagnostics.append(
                    RetrievalBenchmarkResolutionDiagnostic(
                        case_id=benchmark_case.case_id,
                        document_alias=benchmark_case.expected_document_alias,
                        file_name=benchmark_case.expected_file_name,
                        message="Final persisted document graph could not be loaded.",
                        details={
                            "document_id": manifest_document.document_id,
                        },
                    )
                )
                continue

            resolved_case, diagnostic = self.case_resolver.try_resolve_case(
                benchmark_case,
                document_graph,
            )
            if diagnostic is not None:
                diagnostics.append(diagnostic)
                continue

            if resolved_case.query is not None:
                resolved_case.query.document_id = manifest_document.document_id

            resolved_cases.append(resolved_case)

        if diagnostics:
            raise SchemaValidationError(
                "One or more retrieval benchmark cases could not be resolved to final chunk IDs.",
                details={
                    "unresolved_case_ids": [
                        diagnostic.case_id
                        for diagnostic in diagnostics
                    ],
                    "diagnostics": [
                        diagnostic.to_dict()
                        for diagnostic in diagnostics
                    ],
                },
            )

        return RetrievalBenchmarkDataset(
            source_path=dataset.source_path,
            cases=resolved_cases,
            identifier_subset_definition=dataset.identifier_subset_definition,
            semantic_procedure_subset_definition=(
                dataset.semantic_procedure_subset_definition
            ),
        )

    def _resolve_manifest_document(
        self,
        *,
        benchmark_case: RetrievalBenchmarkCase,
        manifest_documents_by_alias: dict[str, RetrievalBenchmarkCorpusDocument],
        manifest_documents_by_file_name: dict[str, RetrievalBenchmarkCorpusDocument],
    ) -> tuple[
        RetrievalBenchmarkCorpusDocument | None,
        RetrievalBenchmarkResolutionDiagnostic | None,
    ]:
        alias = benchmark_case.expected_document_alias
        file_name = benchmark_case.expected_file_name
        alias_document = (
            manifest_documents_by_alias.get(alias)
            if alias is not None
            else None
        )
        file_document = (
            manifest_documents_by_file_name.get(file_name)
            if file_name is not None
            else None
        )

        if alias_document is None and file_document is None:
            return None, RetrievalBenchmarkResolutionDiagnostic(
                case_id=benchmark_case.case_id,
                document_alias=alias,
                file_name=file_name,
                message="Benchmark case could not be mapped to a seeded document.",
                details={
                    "expected_alias": alias,
                    "expected_file_name": file_name,
                },
            )

        if alias_document is not None and file_name is not None:
            if alias_document.file_name != file_name:
                return None, RetrievalBenchmarkResolutionDiagnostic(
                    case_id=benchmark_case.case_id,
                    document_alias=alias,
                    file_name=file_name,
                    message="Benchmark case alias and file name point to different seeded documents.",
                    details={
                        "alias_document_file_name": alias_document.file_name,
                        "expected_file_name": file_name,
                    },
                )

        if (
            alias_document is not None
            and file_document is not None
            and alias_document.document_id != file_document.document_id
        ):
            return None, RetrievalBenchmarkResolutionDiagnostic(
                case_id=benchmark_case.case_id,
                document_alias=alias,
                file_name=file_name,
                message="Benchmark case alias and file name resolved to different document IDs.",
                details={
                    "alias_document_id": alias_document.document_id,
                    "file_document_id": file_document.document_id,
                },
            )

        return alias_document or file_document, None

    def _load_document_graph(
        self,
        document_id: str,
        *,
        graph_cache: dict[str, DocumentGraph],
        activity_context: ActivityContext | None = None,
    ) -> DocumentGraph | None:
        cached_graph = graph_cache.get(document_id)
        if cached_graph is not None:
            return cached_graph

        document_graph = self.document_lookup_service.get_document_graph(
            document_id,
            activity_context=activity_context,
        )
        if document_graph is not None:
            graph_cache[document_id] = document_graph
        return document_graph
