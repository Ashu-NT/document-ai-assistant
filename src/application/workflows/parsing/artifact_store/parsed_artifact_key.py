from __future__ import annotations

import hashlib
from dataclasses import dataclass

# Bump whenever the on-disk artifact layout/content (manifest fields,
# document.json shape, reconstruction contract) changes in a way that makes
# previously published artifacts unusable. Bumping this changes every
# artifact's cache_key, so old artifacts are simply never looked up again
# (they are not migrated or deleted).
PARSED_ARTIFACT_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class ParsedArtifactKey:
    """Identity of a cacheable parsed-document artifact.

    Two parses land on the same canonical artifact iff every field here is
    equal: same source bytes, same parser, same conversion configuration,
    same on-disk artifact schema. `conversion_fingerprint` is an opaque
    value supplied by the parser (see `ParserPort`-adjacent
    `resolve_conversion_fingerprint`) - this key never inspects or
    constructs parser-specific configuration itself.
    """

    source_sha256: str
    parser_name: str
    parser_version: str | None
    conversion_fingerprint: str
    schema_version: int = PARSED_ARTIFACT_SCHEMA_VERSION

    @property
    def cache_key(self) -> str:
        canonical = "|".join(
            [
                str(self.schema_version),
                self.source_sha256,
                self.parser_name,
                self.parser_version or "",
                self.conversion_fingerprint,
            ]
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
