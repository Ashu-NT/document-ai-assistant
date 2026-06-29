from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalRetryPolicy:
    max_retries: int = 1
    increase_top_k_on_retry: bool = True
    retry_top_k_increment: int = 5
    preserve_initial_chunks: bool = True
    deduplicate_by_chunk_id: bool = True
    max_merged_chunks: int = 12
