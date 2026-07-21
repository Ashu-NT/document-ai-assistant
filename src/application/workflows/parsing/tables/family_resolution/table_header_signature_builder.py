from src.application.workflows.parsing.tables.structure.table_header_path_builder import (
    TableHeaderPathBuilder,
)
from src.domain.assets import TableAsset


class TableHeaderSignatureBuilder:
    def __init__(
        self,
        *,
        header_path_builder: TableHeaderPathBuilder | None = None,
    ) -> None:
        self.header_path_builder = header_path_builder or TableHeaderPathBuilder()

    def build(self, table: TableAsset) -> str | None:
        paths = self.build_paths(table)
        if not paths:
            return None
        return "|".join(" > ".join(path) for path in paths if path)

    def build_display_signature(self, table: TableAsset) -> str | None:
        """Human-readable signature with a uniform umbrella title
        stripped. For persisted/displayed metadata only - matching logic
        must use the lossless `build`/`build_paths` instead, since two
        unrelated tables can share a generic deeper header once their
        one distinguishing title is thrown away.
        """
        paths = self.build_umbrella_collapsed_paths(table)
        if not paths:
            return None
        return "|".join(" > ".join(path) for path in paths if path)

    def build_paths(self, table: TableAsset) -> tuple[tuple[str, ...], ...]:
        """Full header paths, umbrella title included. This is the
        lossless signature used for exact/fuzzy matching - dropping the
        umbrella here would let two unrelated tables that merely share a
        generic deeper header (e.g. "Parameter | Value") collapse onto
        the same signature once their distinguishing title is stripped.
        """
        return self.header_path_builder.build_paths(table)

    def build_umbrella_collapsed_paths(
        self, table: TableAsset
    ) -> tuple[tuple[str, ...], ...]:
        """Header paths with a uniform umbrella title stripped. Only safe
        to use for matching two tables whose umbrella titles are already
        confirmed compatible (see `umbrella_text`) - otherwise this is the
        lossy view that can make unrelated tables look identical.
        """
        return self.header_path_builder.build_umbrella_collapsed_paths(table)

    def umbrella_text(self, table: TableAsset) -> str | None:
        return self.header_path_builder.umbrella_text(table)
