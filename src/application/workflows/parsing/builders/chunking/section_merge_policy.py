from src.application.workflows.parsing.builders.chunking.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.chunking_utils import (
    common_path_prefix,
)
from src.application.workflows.parsing.builders.chunking.section_semantics import (
    is_introductory_title,
    is_task_like_title,
    titles_share_topic,
)


class SectionMergePolicy:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        min_section_text_length: int,
    ) -> None:
        self.text_splitter = text_splitter
        self.min_section_text_length = min_section_text_length
        self.soft_chunk_tokens = max(
            int(self.text_splitter.max_chunk_tokens * 0.85),
            self.text_splitter.max_chunk_tokens - 30,
        )
        self.small_section_tokens = max(
            self.min_section_text_length * 3,
            int(self.text_splitter.max_chunk_tokens * 0.3),
        )
        self.intro_context_tokens = max(
            self.min_section_text_length * 4,
            int(self.text_splitter.max_chunk_tokens * 0.45),
        )

    def should_flush_on_section_change(
        self,
        *,
        current_fragments: list[ChunkFragment],
        next_fragment: ChunkFragment,
    ) -> bool:
        previous_fragment = current_fragments[-1]
        previous_path = previous_fragment.section_path
        next_path = next_fragment.section_path
        current_tokens = self._fragments_token_count(current_fragments)
        combined_tokens = current_tokens + next_fragment.token_count
        tail_tokens = self._tail_section_token_count(current_fragments)

        if not previous_path or not next_path:
            return current_tokens >= self.small_section_tokens

        if previous_path == next_path:
            return False

        if not self._paths_are_related(previous_path, next_path):
            return True

        previous_title = previous_fragment.section_title or previous_path[-1]
        next_title = next_fragment.section_title or next_path[-1]
        if combined_tokens <= self.text_splitter.max_chunk_tokens:
            if self._should_merge_intro_with_child(
                previous_fragment=previous_fragment,
                next_fragment=next_fragment,
                current_tokens=current_tokens,
                previous_title=previous_title,
                next_title=next_title,
            ):
                return False

            if self._should_merge_same_topic_sections(
                previous_fragment=previous_fragment,
                next_fragment=next_fragment,
                previous_title=previous_title,
                next_title=next_title,
            ):
                return False

            if (
                self._shares_parent(previous_fragment, next_fragment)
                and (
                    is_task_like_title(previous_title)
                    or is_task_like_title(next_title)
                )
                and tail_tokens <= self.small_section_tokens
                and next_fragment.token_count <= self.intro_context_tokens
            ):
                return False

        if previous_fragment.section_level <= 1 or next_fragment.section_level <= 1:
            return True

        if current_tokens >= self.soft_chunk_tokens:
            return True

        if self._shares_parent(previous_fragment, next_fragment):
            if (
                is_task_like_title(previous_title)
                and is_task_like_title(next_title)
            ):
                return tail_tokens >= self.intro_context_tokens

            return True

        if self._path_is_ancestor(previous_path, next_path) or self._path_is_ancestor(
            next_path,
            previous_path,
        ):
            return tail_tokens >= self.intro_context_tokens

        return True

    def _should_merge_intro_with_child(
        self,
        *,
        previous_fragment: ChunkFragment,
        next_fragment: ChunkFragment,
        current_tokens: int,
        previous_title: str,
        next_title: str,
    ) -> bool:
        if current_tokens > self.intro_context_tokens:
            return False

        if not self._path_is_ancestor(previous_fragment.section_path, next_fragment.section_path):
            return False

        return (
            is_introductory_title(previous_title)
            or is_task_like_title(next_title)
            or current_tokens <= self.small_section_tokens
        )

    @staticmethod
    def _should_merge_same_topic_sections(
        *,
        previous_fragment: ChunkFragment,
        next_fragment: ChunkFragment,
        previous_title: str,
        next_title: str,
    ) -> bool:
        if titles_share_topic(previous_title, next_title):
            return True

        if not (
            is_task_like_title(previous_title)
            and is_task_like_title(next_title)
        ):
            return False

        return (
            previous_fragment.parent_section_id is not None
            and previous_fragment.parent_section_id == next_fragment.parent_section_id
        )

    @staticmethod
    def _shares_parent(
        previous_fragment: ChunkFragment,
        next_fragment: ChunkFragment,
    ) -> bool:
        return (
            previous_fragment.parent_section_id is not None
            and previous_fragment.parent_section_id == next_fragment.parent_section_id
        )

    @staticmethod
    def _paths_are_related(
        previous_path: list[str],
        next_path: list[str],
    ) -> bool:
        common_path = common_path_prefix([previous_path, next_path])
        return bool(common_path and common_path[0] == previous_path[0])

    @staticmethod
    def _path_is_ancestor(
        candidate_ancestor: list[str],
        candidate_descendant: list[str],
    ) -> bool:
        if len(candidate_ancestor) >= len(candidate_descendant):
            return False

        return candidate_descendant[: len(candidate_ancestor)] == candidate_ancestor

    @staticmethod
    def _fragments_token_count(fragments: list[ChunkFragment]) -> int:
        return sum(fragment.token_count for fragment in fragments)

    @staticmethod
    def _tail_section_token_count(fragments: list[ChunkFragment]) -> int:
        if not fragments:
            return 0

        section_id = fragments[-1].section_id
        total = 0
        for fragment in reversed(fragments):
            if fragment.section_id != section_id:
                break
            total += fragment.token_count

        return total
