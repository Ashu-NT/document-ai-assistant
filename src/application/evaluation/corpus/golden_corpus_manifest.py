from pathlib import Path
from typing import Sequence

from src.application.evaluation.corpus.golden_document_manifest_entry import (
    GoldenDocumentManifestEntry,
)
from src.application.evaluation.corpus.resolved_golden_document import (
    GoldenDocumentAvailability,
    ResolvedGoldenDocument,
)
from src.application.workflows.ingestion.hashing.file_hash_service import (
    compute_file_hash,
)
from src.config.settings import golden_corpus_settings
from src.domain.common import DocumentType
from src.shared.exceptions import SchemaValidationError

# The approved Phase 1 golden corpus (10 documents; see
# outputs/architecture/golden_evaluation_corpus_architecture_investigation.md
# section 6 and the approved-decisions message that confirmed it). Aliases
# are the SAME aliases already used for these documents in
# TestDoc/retrieval_truth_set.md, so this manifest never introduces a second
# identity vocabulary for the same files. `relative_path` is relative to
# `golden_corpus_settings.root_path` (TestDoc/ by default). `expected_type`
# values are reused from that same file's own human-reviewed "Expected
# Type" corpus-inventory column, not fabricated here. `expected_sha256`
# values were computed directly against the real files present in this
# corpus at authoring time.
_DEFAULT_ENTRIES: tuple[GoldenDocumentManifestEntry, ...] = (
    GoldenDocumentManifestEntry(
        alias="manual_fwc12",
        relative_path="19P006-31-FWC12-5-1-0_Manual.pdf",
        category="manual",
        expected_document_type=DocumentType.MANUAL,
        expected_sha256="708f50744466ccc60d874467b63003421e6d13eb5e86d38e69635b2b9a9dec35",
        notes="Long manual: TOC, nested sections, maintenance tables, procedures, spare parts, troubleshooting. Richest existing structural/retrieval coverage in the corpus.",
    ),
    GoldenDocumentManifestEntry(
        alias="manual_bauer_mv320_compressor",
        relative_path="01 Operating Manual High Pressure Compressors MV320 20251125.pdf",
        category="manual",
        expected_document_type=DocumentType.MANUAL,
        expected_sha256="bbb226d4aa6969ecec21e94fbf908bca9a57b23a3a1294aedca1893da3bd3d06",
        notes="Different vendor/structure from manual_fwc12: safety, technical data, installation, commissioning, troubleshooting, maintenance.",
    ),
    GoldenDocumentManifestEntry(
        alias="datasheet_mk311xxx",
        relative_path="DN25 - DN80_MK311xxx.pdf",
        category="datasheet",
        expected_document_type=DocumentType.DATASHEET,
        expected_sha256="1481f98b7dc1e4f07a28567212aeaeced10f9448c374ad7ea462ba8b936feb39",
        notes="Table-heavy: bilingual specs, order-code table, dimensions, material list.",
    ),
    GoldenDocumentManifestEntry(
        alias="datasheet_deck_fillers",
        relative_path="Deck-fillers_datasheet.pdf",
        category="datasheet",
        expected_document_type=DocumentType.DATASHEET,
        expected_sha256="cd304a12ead6de83a9e934e7fc7374075dd3ef4b0e487f5dbd23a4bfeed492af",
        notes="Image/drawing-heavy: detail drawings, dimension table, installation/maintenance instructions.",
    ),
    GoldenDocumentManifestEntry(
        alias="certificate_hoses_ham2423501",
        relative_path="0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501.pdf",
        category="certificate",
        expected_document_type=DocumentType.CERTIFICATE,
        expected_sha256="64f0ee8bac148f965b17155ade6a758b1744289646009e4fce3400a9db4f1158",
        notes="Single certificate, identifier-heavy fields (certificate number, serials, pressure).",
    ),
    GoldenDocumentManifestEntry(
        alias="certificate_mtu_engine_set_ham2152268",
        relative_path="Reg - 18 MTU_Engine_Set_20V4000M53B_SN_528106066_528106062_Certificate_HAM_2152268_2152275.pdf",
        category="certificate",
        expected_document_type=DocumentType.CERTIFICATE,
        expected_sha256="28e25caefafac8a795e1a31a5a87e757536d56fa5beecc7580299c7941344c17",
        notes="Two Lloyd's Register certificates in one PDF - multi-certificate packet, distinct shape from certificate_hoses_ham2423501.",
    ),
    GoldenDocumentManifestEntry(
        alias="report_transformer_d4000240",
        relative_path="P.N.2022-40405 D4000240 T.REPORT.pdf",
        category="engineering_report",
        expected_document_type=DocumentType.REPORT,
        expected_sha256="b9da2994dd7544f9cedb052b3cac3a3e25d5c6bdfdc412f5342bbf36c10ed4af",
        notes="Scanned/OCR transformer test report - closes the parsing-performance-thresholds OCR calibration gap.",
    ),
    GoldenDocumentManifestEntry(
        alias="report_man_shop_test_8351446",
        relative_path="preliminary_report_8351446.pdf",
        category="engineering_report",
        expected_document_type=DocumentType.REPORT,
        expected_sha256="3d7418ab324ec4687a49be88067ad05b66c895df2723ba939fc09b8996a1a8fb",
        notes="Structured, text-native performance-data report - contrast to report_transformer_d4000240.",
    ),
    GoldenDocumentManifestEntry(
        alias="report_pressure_transmitter",
        relative_path="Pressure transmitter.pdf",
        category="procedure_like",
        expected_document_type=DocumentType.REPORT,
        expected_sha256="ec82b50a4c31bd697a6dce27888dd817cc62aca3ad1616b83e8508b20e631506",
        notes="Inspection report + operating instructions + safety instructions packet. Closest real analogue to an SOP/procedure document; DocumentType has no SOP value (approved decision 2), so this is classified as REPORT.",
    ),
    GoldenDocumentManifestEntry(
        alias="report_vedder_maintenance",
        relative_path="99_Vedder_Maintenance Reports.pdf",
        category="procedure_like",
        expected_document_type=DocumentType.REPORT,
        expected_sha256="193504db71f77d5da76127f20a692bb4904e495528b22c1e33522f5ab95e9272",
        notes="Maintenance-procedure/checklist-flavored content, distinct shape from report_pressure_transmitter. DocumentType has no SOP value (approved decision 2), so this is classified as REPORT.",
    ),
)


class GoldenCorpusManifest:
    def __init__(
        self,
        entries: Sequence[GoldenDocumentManifestEntry],
        *,
        root_dir: Path | None = None,
    ) -> None:
        self._entries = tuple(entries)
        self._by_alias = {entry.alias: entry for entry in self._entries}
        if len(self._by_alias) != len(self._entries):
            raise SchemaValidationError(
                "Golden corpus manifest contains duplicate aliases.",
                details={"aliases": [entry.alias for entry in self._entries]},
            )
        self._root_dir = root_dir if root_dir is not None else golden_corpus_settings.root_path

    @classmethod
    def default(cls) -> "GoldenCorpusManifest":
        return cls(_DEFAULT_ENTRIES)

    @property
    def entries(self) -> tuple[GoldenDocumentManifestEntry, ...]:
        return self._entries

    @property
    def root_dir(self) -> Path:
        return self._root_dir

    def entry(self, alias: str) -> GoldenDocumentManifestEntry:
        try:
            return self._by_alias[alias]
        except KeyError as exc:
            raise SchemaValidationError(
                "Unknown golden corpus document alias.",
                details={
                    "alias": alias,
                    "known_aliases": sorted(self._by_alias),
                },
            ) from exc

    def resolve(self, alias: str) -> ResolvedGoldenDocument:
        entry = self.entry(alias)
        absolute_path = self._root_dir / entry.relative_path

        if not absolute_path.is_file():
            return ResolvedGoldenDocument(
                entry=entry,
                absolute_path=absolute_path,
                availability=GoldenDocumentAvailability.MISSING,
                actual_sha256=None,
            )

        actual_sha256 = compute_file_hash(absolute_path)
        if entry.expected_sha256 is not None and actual_sha256 != entry.expected_sha256:
            availability = GoldenDocumentAvailability.HASH_MISMATCH
        else:
            availability = GoldenDocumentAvailability.AVAILABLE

        return ResolvedGoldenDocument(
            entry=entry,
            absolute_path=absolute_path,
            availability=availability,
            actual_sha256=actual_sha256,
        )

    def resolve_all(self) -> list[ResolvedGoldenDocument]:
        return [self.resolve(entry.alias) for entry in self._entries]


__all__ = ["GoldenCorpusManifest"]
