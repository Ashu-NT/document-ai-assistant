from tests.unit.application.workflows.parsing.builders.chunking._test_chunk_type_resolver_support import *  # noqa: F401,F403

@pytest.mark.parametrize(
    ("section_title", "text", "expected_chunk_type", "table_ids"),
    [
        (
            "Maintenance Procedure",
            "Remove the cover, inspect the seal, and reinstall the housing.",
            ChunkType.MAINTENANCE_PROCEDURE,
            None,
        ),
        (
            "Maintenance Schedule",
            "Replace the hydraulic filter every 500 hours.",
            ChunkType.MAINTENANCE_INTERVAL,
            None,
        ),
        (
            "Safety Warnings",
            "Warning: disconnect power before opening the housing.",
            ChunkType.SAFETY_WARNING,
            None,
        ),
        (
            "Troubleshooting",
            "Possible cause: low voltage. Corrective action: verify the supply.",
            ChunkType.TROUBLESHOOTING,
            None,
        ),
        (
            "Electrical Specifications",
            "Operating limits: 24 V, 3 A, 50 Hz.",
            ChunkType.TECHNICAL_SPECIFICATION,
            ["table_001"],
        ),
        (
            "Installation",
            "Install the bracket, align the housing, and secure the bolts.",
            ChunkType.INSTALLATION_INSTRUCTION,
            None,
        ),
        (
            "Operation",
            "Turn on the controller and operate the pump at nominal load.",
            ChunkType.OPERATION_INSTRUCTION,
            None,
        ),
        (
            "Certificate of Conformity",
            "This device complies with IEC 61010 and CE requirements.",
            ChunkType.CERTIFICATION_INFO,
            None,
        ),
    ],
)
def test_chunk_type_resolver_detects_semantic_chunk_types(
    section_title: str,
    text: str,
    expected_chunk_type: ChunkType,
    table_ids: list[str] | None,
) -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title=section_title,
                text=text,
                table_ids=table_ids,
            )
        ]
    )

    assert chunk_type == expected_chunk_type

def test_chunk_type_resolver_keeps_ambiguous_chunks_general() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Overview",
                text="Install and operate the module after setup.",
            )
        ]
    )

    assert chunk_type == ChunkType.GENERAL

def test_chunk_type_resolver_preserves_special_chunk_types() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Assembly View",
                text="Figure: Exploded assembly view.",
                chunk_type=ChunkType.DRAWING_REFERENCE,
            )
        ]
    )

    assert chunk_type == ChunkType.DRAWING_REFERENCE

def test_chunk_type_resolver_prioritizes_spec_table_content_over_safety_path() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Technical Data",
                section_path=[
                    "7 Components",
                    "7.2 Food Waste Press",
                    "Safety Precautions 7.2.1",
                    "Owner / User Responsibility",
                    "General Warnings",
                    "Electrical System Precautions",
                    "Biohazard",
                    "Food Waste Press Description 7.2.2",
                    "Technical Data",
                ],
                text=(
                    "| Press Type | TSP20 |\n"
                    "| Serial Number | 221010004Z507 |\n"
                    "| Drive Type | BF30 |\n"
                    "| Drive Specification | 400V / 50Hz |\n"
                    "| Year of Manufacture | 2020 |"
                ),
                table_ids=["table_001"],
            )
        ]
    )

    assert chunk_type == ChunkType.TECHNICAL_SPECIFICATION

def test_chunk_type_resolver_detects_troubleshooting_table_with_hyphenated_heading() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Trouble-Shooting 7.3.10",
                section_path=[
                    "7 Components",
                    "7.3 Vacuum / Transfer Pump",
                    "Trouble-Shooting 7.3.10",
                ],
                text=(
                    "| Problem | Probable Causes | Potential Remedy |\n"
                    "| The pump will not start | The discharge pressure is too high | Reduce pressure |"
                ),
                table_ids=["table_002"],
            )
        ]
    )

    assert chunk_type == ChunkType.TROUBLESHOOTING

def test_chunk_type_resolver_prioritizes_direct_table_evidence_over_safety_path() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="General Warnings",
                section_path=[
                    "7 Components",
                    "7.3 Vacuum / Transfer Pump",
                    "Safety Precautions 7.3.1",
                    "General Warnings",
                ],
                text=(
                    "| Press Type | TSP20 |\n"
                    "| Serial Number | 221010004Z507 |\n"
                    "| Drive Type | BF30 |\n"
                    "| Specification | 400V / 50Hz |\n"
                    "| Year of Manufacture | 2020 |"
                ),
                table_ids=["table_003"],
            )
        ]
    )

    assert chunk_type == ChunkType.TECHNICAL_SPECIFICATION

def test_chunk_type_resolver_treats_symptom_subsection_inside_troubleshooting_as_troubleshooting() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Machine does not Start and makes no Sound",
                section_path=[
                    "7 Components",
                    "7.1 Macerators",
                    "Trouble Shooting 7.1.10",
                    "Machine does not Start and makes no Sound",
                ],
                text=(
                    "Check that the disposer inlet lid is in place and properly closed. "
                    "Check that the main power isolator is in ON-position."
                ),
            )
        ]
    )

    assert chunk_type == ChunkType.TROUBLESHOOTING

def test_chunk_type_resolver_ignores_polluted_operation_path_inside_troubleshooting() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Disposer starts but there is no flushing water",
                section_path=[
                    "7 Components",
                    "7.1 Macerators",
                    "Commissioning & Shutdown 7.1.8",
                    "Check before Start Up",
                    "Checks during Start Up",
                    "Operation 7.1.9",
                    "Start and stop",
                    "Trouble Shooting 7.1.10",
                    "Disposer Reduces Speed, Stops or does not Start",
                    "Disposer starts but there is no flushing water",
                ],
                text=(
                    "Is the water supply isolation valve open? "
                    "Is a clicking sound heard when activating the water solenoid valve? "
                    "Is the water strainer clogged? Isolate the water supply, open strainer and clean."
                ),
            )
        ]
    )

    assert chunk_type == ChunkType.TROUBLESHOOTING

def test_chunk_type_resolver_detects_lubrication_schedule_as_maintenance_interval() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Lubrication Schedule",
                section_path=[
                    "7 Components",
                    "7.3 Vacuum / Transfer Pump",
                    "7.3.9.2 Lubricating the Shaft Seals",
                    "Lubrication Schedule",
                ],
                text="After every 350 hours of operation. Filling quantity: 2 to 3 strokes per grease nipple.",
            )
        ]
    )

    assert chunk_type == ChunkType.MAINTENANCE_INTERVAL

def test_chunk_type_resolver_detects_oil_change_interval_as_maintenance_interval() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Oil Change Interval",
                section_path=[
                    "7 Components",
                    "7.3 Vacuum / Transfer Pump",
                    "Oil Change Interval",
                ],
                text=(
                    "First oil change after approx. 500 hours or 12 months. "
                    "Subsequent oil change after each 2000 hours or 12 months."
                ),
            )
        ]
    )

    assert chunk_type == ChunkType.MAINTENANCE_INTERVAL
