from src.application.evaluation.retrieval.benchmarking import (
    RetrievalBenchmarkCase,
    RetrievalBenchmarkReport,
)
from src.application.evaluation.retrieval.evaluators.benchmarking import (
    RetrievalBenchmarkEvaluator,
)


class ChunkQualityEvaluator:
    def __init__(
        self,
        *,
        retrieval_benchmark_evaluator: RetrievalBenchmarkEvaluator | None = None,
    ) -> None:
        self.retrieval_benchmark_evaluator = (
            retrieval_benchmark_evaluator or RetrievalBenchmarkEvaluator()
        )

    def evaluate(
        self,
        workflow,
        benchmark_cases: list[RetrievalBenchmarkCase],
    ) -> RetrievalBenchmarkReport:
        return self.retrieval_benchmark_evaluator.evaluate(
            workflow,
            benchmark_cases,
        )
