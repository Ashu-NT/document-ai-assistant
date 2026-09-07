from src.application.workflows.parsing.builders.chunking.builders.chunk_type.chunk_type_resolver import (
    ChunkTypeResolver,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    common_path_prefix,
)
from src.application.workflows.parsing.builders.chunking.policies.section_merge.section_semantics import (
    is_introductory_title,
    section_semantic_family,
    titles_share_topic,
)


class SectionMergePolicy:
    """Decides whether two adjacent section fragments may share one chunk.

    A merge is only ever allowed along one of two paths, and only when the
    combined content fits the token budget and there's no hard semantic
    conflict between the two sections:

    - sibling merge: same parent section, AND a real positive compatibility
      signal (shared title topic today). Sharing a coarse content family
      (e.g. two different legal clauses) is checked earlier only as a hard
      veto when families *differ* -- matching families alone is never
      sufficient to merge, just as differing families alone is enough to
      block it.
    - intro refinement: the earlier fragment is a genuine ancestor of the
      later one AND is itself introductory (background/overview-style),
      AND is short enough to still read as scene-setting rather than
      substantial content of its own.

    Numbering (e.g. two sections both being numbered) is deliberately never
    treated as a compatibility signal on its own -- it says nothing about
    whether the two sections' content is actually related. When neither
    path's conditions are met, sections are kept separate (the conservative
    default).
    """

    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        min_section_text_length: int,
        same_topic_merge_tokens: int | None = None,
        intro_context_tokens: int | None = None,
        chunk_type_resolver: ChunkTypeResolver | None = None,
    ) -> None:
        self.text_splitter = text_splitter
        self.min_section_text_length = min_section_text_length
        self.chunk_type_resolver = chunk_type_resolver or ChunkTypeResolver()
        computed_small_section_tokens = max(
            self.min_section_text_length * 3,
            int(self.text_splitter.max_chunk_tokens * 0.3),
        )
        computed_intro_context_tokens = max(
            self.min_section_text_length * 4,
            int(self.text_splitter.max_chunk_tokens * 0.45),
        )
        self.small_section_tokens = same_topic_merge_tokens or computed_small_section_tokens
        self.intro_context_tokens = (
            intro_context_tokens or computed_intro_context_tokens
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

        if not previous_path or not next_path:
            return current_tokens >= self.small_section_tokens

        if previous_path == next_path:
            return False

        if not self._paths_are_related(previous_path, next_path):
            return True

        combined_tokens = current_tokens + next_fragment.token_count
        if combined_tokens > self.text_splitter.max_chunk_tokens:
            return True

        if not self.chunk_type_resolver.are_semantically_compatible(
            current_fragments=current_fragments,
            next_fragment=next_fragment,
        ):
            return True

        previous_title = previous_fragment.section_title or previous_path[-1]
        next_title = next_fragment.section_title or next_path[-1]

        if self._has_hard_family_conflict(previous_title, next_title):
            return True

        if self._is_valid_intro_refinement(
            previous_fragment=previous_fragment,
            next_fragment=next_fragment,
            previous_title=previous_title,
            current_tokens=current_tokens,
        ):
            return False

        if self._is_valid_sibling_merge(
            previous_fragment=previous_fragment,
            next_fragment=next_fragment,
            previous_title=previous_title,
            next_title=next_title,
        ):
            return False

        return True

    @staticmethod
    def _has_hard_family_conflict(
        previous_title: str,
        next_title: str,
    ) -> bool:
        previous_family = section_semantic_family(previous_title)
        next_family = section_semantic_family(next_title)
        if previous_family is None or next_family is None:
            return False
        return previous_family != next_family

    def _is_valid_intro_refinement(
        self,
        *,
        previous_fragment: ChunkFragment,
        next_fragment: ChunkFragment,
        previous_title: str,
        current_tokens: int,
    ) -> bool:
        if not self._path_is_ancestor(
            previous_fragment.section_path,
            next_fragment.section_path,
        ):
            return False

        if current_tokens > self.intro_context_tokens:
            return False

        return is_introductory_title(previous_title)

    @staticmethod
    def _is_valid_sibling_merge(
        *,
        previous_fragment: ChunkFragment,
        next_fragment: ChunkFragment,
        previous_title: str,
        next_title: str,
    ) -> bool:
        # Sharing a semantic family (checked earlier, as a hard veto when
        # families differ) is necessary but never sufficient on its own --
        # two siblings of the same broad family with no other relationship
        # (e.g. two unrelated legal clauses) are exactly the "uncertain"
        # case the conservative default is for. A real positive signal
        # (shared title topic today) is required to actually merge.
        if not SectionMergePolicy._shares_parent(previous_fragment, next_fragment):
            return False

        return titles_share_topic(previous_title, next_title)

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
