from __future__ import annotations

"""
Small, hand-authored golden set for answer-quality measurement (Phase 0 of the
answer-quality-and-output enterprise hardening plan; see
`outputs/architecture/answer_quality_and_output_enterprise_hardening_plan.md`,
Section 7 / Phase 0).

Unlike `RetrievalBenchmarkCase` (which only records *expected retrieval
targets* -- document/section/page/chunk -- and never an expected answer),
each `GoldenAnswerCase` below carries an expected answer, the factual claims
that answer must cover, and a loose citation hint, so a real generated answer
can be graded against it by an independent LLM-as-judge pass
(`scripts/run_answer_quality_judge.py`).

This is intentionally a plain Python dataclass fixture rather than a markdown
file. The retrieval truth set (`TestDoc/retrieval_truth_set.md`) uses markdown
because it is a large (122-case), hand-maintained document meant to be read
and reviewed by non-engineers alongside the five source PDFs it targets, and
`TestDoc/` itself is gitignored (see
`tests/unit/application/evaluation/retrieval/benchmarking/loaders/test_retrieval_truth_set_loader.py`).
This golden set is much smaller, is authored directly against the
already-seeded, real corpus in `data/maintenance_ai.db`, and has no
counterpart markdown/PDF pairing to keep in sync -- a plain Python literal
(matching `RetrievalBenchmarkCase`'s dataclass-fixture style) is simpler to
review and version here.

Every `document_title` below is a real, currently-ingested document title
(see the `documents` table), and every `expected_answer` /
`expected_claims` entry is grounded in real extracted rows inspected directly
from `maintenance_tasks`, `specifications`, `procedures`, `identifiers`,
`spare_parts`, and `safety_warnings` for that document -- not invented
content -- so a real end-to-end run of the QA pipeline against the seeded
corpus can actually be graded against these cases.
"""

from dataclasses import dataclass, field

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


@dataclass(slots=True)
class GoldenAnswerCase:
    case_id: str
    document_title: str
    question: str
    expected_answer: str
    expected_claims: list[str] = field(default_factory=list)
    expected_citation_hint: str | None = None
    expected_intent: AnswerIntent | None = None
    notes: str | None = None


def load_golden_answer_cases() -> list[GoldenAnswerCase]:
    """Returns a fresh copy of the hand-authored golden answer set."""

    return list(_GOLDEN_ANSWER_CASES)


_GOLDEN_ANSWER_CASES: tuple[GoldenAnswerCase, ...] = (
    GoldenAnswerCase(
        case_id="AQ-001",
        document_title="19P006-31-FWC12-5-1-0_Manual",
        question=(
            "What safety steps must be followed before installing or "
            "operating the FWC12 equipment?"
        ),
        expected_answer=(
            "Read the operation instructions before installation, start-up, "
            "operation, or maintenance. Lock out power following the ship's "
            "isolation procedures before opening the plant, and disconnect "
            "all electrical components before disassembly. Guards and "
            "covers must be replaced, and put back in place, only after the "
            "plant has been secured and locked out and before restarting it."
        ),
        expected_claims=[
            "Read the operating instructions before installation, start-up, operation, or maintenance",
            "Lock out power per the ship's isolation procedures before opening the plant",
            "Disconnect all electrical components before disassembly",
            "Replace guards/covers only after securing and locking out, before restart",
        ],
        expected_citation_hint="the 'Install and operate equipment' safety procedure (around page 9)",
        expected_intent=AnswerIntent.PROCEDURE_STEPS,
    ),
    GoldenAnswerCase(
        case_id="AQ-002",
        document_title="19P006-31-FWC12-5-1-0_Manual",
        question="What are the tank capacity and pump capacity of the FWC12 system?",
        expected_answer=(
            "The FWC12 has a tank capacity of 1,200 L and a pump capacity of "
            "max 16,000 L/hr, with a dewatering capacity of max 20,000 L/hr."
        ),
        expected_claims=[
            "Tank capacity is 1,200 L",
            "Pump capacity is max 16,000 L/hr",
            "Dewatering capacity is max 20,000 L/hr",
        ],
        expected_citation_hint="the Technical Data specification table (around page 12)",
        expected_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-003",
        document_title="19P006-31-FWC12-5-1-0_Manual",
        question="What are the steps to shut down the FWC12?",
        expected_answer=(
            "Make sure all personnel know the shutdown procedure and safety "
            "protocols, electrically isolate the equipment and lock out the "
            "local isolator to prevent accidental activation, flush "
            "bio-residues from the pumps and pipelines, and isolate the "
            "equipment to prevent unintended contact with process streams."
        ),
        expected_claims=[
            "Ensure personnel are aware of the shutdown procedure and safety protocols",
            "Electrically isolate the equipment and lock out the local isolator",
            "Flush bio-residues from the pumps and pipelines",
            "Isolate the equipment to prevent unintended contact with process streams",
        ],
        expected_citation_hint="the 'Shutdown FWC12' procedure (around page 9)",
        expected_intent=AnswerIntent.PROCEDURE_STEPS,
    ),
    GoldenAnswerCase(
        case_id="AQ-004",
        document_title="19P006-31-FWC12-5-1-0_Manual",
        question="What do the caution, warning, and biohazard symbols mean in the FWC12 manual?",
        expected_answer=(
            "The caution symbol marks information that, if not followed, "
            "may lead to minor damage or injury. The warning (electrical "
            "hazard) symbol marks information that, if not followed, could "
            "lead to health hazards, injury, or death. The biohazard symbol "
            "marks information that, if not followed, could lead to illness "
            "or death."
        ),
        expected_claims=[
            "Caution symbol: non-compliance may lead to minor damage or injury",
            "Warning/electrical hazard symbol: non-compliance could lead to health hazards, injury, or death",
            "Biohazard symbol: non-compliance could lead to illness or death",
        ],
        expected_citation_hint="the safety symbol legend near the front of the manual (around page 7)",
        expected_intent=AnswerIntent.SAFETY_WARNINGS,
    ),
    GoldenAnswerCase(
        case_id="AQ-005",
        document_title="19P006-31-FWC12-5-1-0_Manual",
        question=(
            "What is the model number of the food waste collection system, "
            "and what drawing/part number identifier is referenced for it?"
        ),
        expected_answer=(
            "The system's model number is FWC12, and it is referenced under "
            "drawing/part number DRG-5001."
        ),
        expected_claims=[
            "Model number is FWC12",
            "Drawing/part number identifier is DRG-5001",
        ],
        expected_citation_hint="the model/identifier reference on the equipment nameplate or cover page",
        expected_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    ),
    GoldenAnswerCase(
        case_id="AQ-006",
        document_title="PURO 30-OWNERS MANUAL-HM13378-ROS213",
        question=(
            "What routine maintenance checks are described for the PURO 30's "
            "electrical equipment and cartridge filters?"
        ),
        expected_answer=(
            "For the electrical equipment and control box, check all "
            "terminal connectors for tightness. For the cartridge filters, "
            "check the feed water pressure gauge. The installation should "
            "also be checked for leaks."
        ),
        expected_claims=[
            "Check all terminal connectors for tightness (electrical equipment / control box)",
            "Check the feed water pressure gauge (cartridge filters)",
            "Check the installation for leaks",
        ],
        expected_citation_hint="the maintenance checklist section (around pages 19-21)",
        expected_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-007",
        document_title="PURO 30-OWNERS MANUAL-HM13378-ROS213",
        question="What spare filter parts are listed for the PURO 30 water maker's housings?",
        expected_answer=(
            "Listed spare parts include a BW O-Ring Set (2), replacement "
            "o-rings for the housing; a Prefilter Element 10BB/BW05, a "
            "prefilter cartridge for 10-inch housings; and a Prefilter "
            "Element 10BB/BW20, a prefilter cartridge for 20-inch housings."
        ),
        expected_claims=[
            "BW O-Ring Set (2) - replacement o-rings for the housing",
            "Prefilter Element 10BB/BW05 - prefilter cartridge for 10-inch housings",
            "Prefilter Element 10BB/BW20 - prefilter cartridge for 20-inch housings",
        ],
        expected_citation_hint="the spare parts list table",
        expected_intent=AnswerIntent.TABLE_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-008",
        document_title="SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211",
        question="What is the model number and electrical rating of this water softener?",
        expected_answer=(
            "The model is SOFTENER 9500 / 1350, with an electrical rating "
            "of 24V-50Hz or 24V-60Hz (other ratings available on request)."
        ),
        expected_claims=[
            "Model number is SOFTENER 9500 / 1350",
            "Electrical rating is 24V-50Hz or 24V-60Hz",
        ],
        expected_citation_hint="the model/specification block (around pages 1 and 29)",
        expected_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-009",
        document_title="SOFTENER 9500-OWNERS MANUAL-HM13378-SOF211",
        question="What is the dosemeter time-per-impulse setting, and what regeneration steps follow it?",
        expected_answer=(
            "The DS9648 dosemeter's time per impulse is set to 2.6 seconds. "
            "The regeneration cycle that follows includes a backwash step "
            "and a slow rinse step."
        ),
        expected_claims=[
            "Dosemeter (DS9648) time per impulse is set to 2.6 sec",
            "Regeneration cycle includes a backwash step",
            "Regeneration cycle includes a slow rinse step",
        ],
        expected_citation_hint="the dosemeter/regeneration cycle steps (around pages 12-14)",
        expected_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-010",
        document_title="01 Operating Manual High Pressure Compressors MV320 20251125",
        question="What safety warning applies when servicing the MV320 compressor's hydraulic filter?",
        expected_answer=(
            "The hydraulic line must be depressurized before removing the "
            "filter housing, to avoid injury from pressurized fluid."
        ),
        expected_claims=[
            "Depressurize the hydraulic line before removing the filter housing",
            "Purpose is to avoid injury from pressurized fluid",
        ],
        expected_citation_hint="the danger/caution warning near the filter maintenance instructions (around page 15)",
        expected_intent=AnswerIntent.SAFETY_WARNINGS,
    ),
    GoldenAnswerCase(
        case_id="AQ-011",
        document_title="01 Operating Manual High Pressure Compressors MV320 20251125",
        question="What maintenance compliance requirements does the MV320 manual state?",
        expected_answer=(
            "The manual requires compliance with the manual and "
            "installation instructions, and compliance with the "
            "maintenance intervals and fulfilment of the maintenance works."
        ),
        expected_claims=[
            "Compliance with the manual and installation instructions is required",
            "Compliance with maintenance intervals and fulfilment of maintenance works is required",
        ],
        expected_citation_hint="the maintenance compliance section (around page 15)",
        expected_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-012",
        document_title="DN25 - DN80_MK311xxx",
        question="What is the pressure rating of the MK series 2-way wafer-type ball valve?",
        expected_answer=(
            "The MK series 2-way wafer-type ball valve (full bore) is rated "
            "PN16 / PN40."
        ),
        expected_claims=[
            "Pressure rating is PN16 / PN40",
            "Valve type is a 2-way wafer-type ball valve, full bore",
        ],
        expected_citation_hint="the valve specification table (around page 1)",
        expected_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-013",
        document_title="Pressure transmitter",
        question=(
            "Which manufacturer and model are referenced for this pressure "
            "transmitter, and what communication protocol does it use?"
        ),
        expected_answer=(
            "The transmitter is the Endress+Hauser Cerabar M "
            "(PMC51, PMP51, PMP55 variants), which supports HART "
            "communication for process pressure measurement."
        ),
        expected_claims=[
            "Manufacturer is Endress+Hauser",
            "Model is Cerabar M (PMC51 / PMP51 / PMP55)",
            "Supports HART communication",
        ],
        expected_citation_hint="the device identification section (around pages 3, 6-7)",
        expected_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    ),
    GoldenAnswerCase(
        case_id="AQ-014",
        document_title="Pressure transmitter",
        question=(
            "Does the manual give exact pressure ratings for gases, "
            "vapors, and liquids for the Cerabar M diaphragm seal?"
        ),
        expected_answer=(
            "No -- the manual does not specify exact pressure ratings for "
            "gases, vapors, or liquids, and the diaphragm seal's pressure "
            "rating is likewise not specified in the text."
        ),
        expected_claims=[
            "Pressure rating for gases is not specified in the text",
            "Pressure rating for vapors is not specified in the text",
            "Pressure rating for liquids is not specified in the text",
            "Diaphragm seal pressure rating is not specified in the text",
        ],
        expected_citation_hint="the pressure rating rows for the diaphragm seal (around pages 10-11)",
        expected_intent=AnswerIntent.SPECIFICATION_SUMMARY,
        notes=(
            "Deliberately a 'no fabricated specifics' check -- a good "
            "answer should say the rating isn't given, not invent a number."
        ),
    ),
    GoldenAnswerCase(
        case_id="AQ-015",
        document_title="0762 0050 CER 1612 H.A.Schroeder Flexible Hoses HAM2423501",
        question="What certificate number and part numbers appear on this flexible hoses certificate?",
        expected_answer=(
            "The certificate number is LR425, covering part numbers "
            "SL060323, SL060324, SL060018, and SL062164."
        ),
        expected_claims=[
            "Certificate number is LR425",
            "Part numbers include SL060323, SL060324, SL060018, and SL062164",
        ],
        expected_citation_hint="the certificate identifier / part number table (around pages 2 and 6)",
        expected_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    ),
    GoldenAnswerCase(
        case_id="AQ-016",
        document_title="Rule Pump cut-sheet",
        question="What information does the Rule Next Generation bilge pump cut-sheet give for comparing pump models?",
        expected_answer=(
            "It lists, per model, the nominal GPH/LPH rating, model number, "
            "volts, amps at 12V and 13.6V, ports, check-valve status, and "
            "hose diameter. Some models have a dual-voltage option, "
            "indicated by adding '24' to the model number."
        ),
        expected_claims=[
            "Lists nominal GPH/LPH rating, model number, volts, and amps at 12V/13.6V per pump",
            "Lists ports, check-valve status, and hose diameter per pump",
            "A dual-voltage option is indicated by adding '24' to the model number",
        ],
        expected_citation_hint="the bilge pump comparison table (around page 2)",
        expected_intent=AnswerIntent.GENERAL,
    ),
    GoldenAnswerCase(
        case_id="AQ-017",
        document_title="Volvo Penta D6-440 DPI cut-sheet",
        question="What are the engine displacement, configuration, and dry weight of the Volvo Penta D6-440 DPI?",
        expected_answer=(
            "The engine displaces 5.50 L (335.6 in3) in an in-line 6 "
            "configuration, turbocharged with an aftercooler and "
            "compressor, and has a dry weight with DPI of 790 kg (1742 lb)."
        ),
        expected_claims=[
            "Displacement is 5.50 L (335.6 in3)",
            "Configuration is in-line 6, turbo with aftercooler and compressor",
            "Dry weight with DPI is 790 kg (1742 lb)",
        ],
        expected_citation_hint="the engine specification table (around page 1)",
        expected_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    ),
    GoldenAnswerCase(
        case_id="AQ-018",
        document_title="Volvo Penta D6-440 DPI cut-sheet",
        question="What voltage options and reduction gear ratio are available for the Volvo Penta D6-440 DPI?",
        expected_answer=(
            "It is available in 12V or 24V, with a reduction gear ratio of "
            "1.69:1 and propeller series H2 through H10."
        ),
        expected_claims=[
            "Voltage options are 12V or 24V",
            "Reduction gear ratio is 1.69:1",
            "Propeller series is H2 - H10",
        ],
        expected_citation_hint="the engine electrical/gear specification rows (around page 1)",
        expected_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    ),
)
