from tests.unit.application.workflows.parsing.builders.chunking._test_chunk_type_resolver_support import *  # noqa: F401,F403

def test_chunk_type_resolver_detects_interval_content_without_explicit_interval_title() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Overview & Maintenance",
                section_path=[
                    "7 Components",
                    "7.1 Macerators",
                    "Overview & Maintenance",
                ],
                text=(
                    "Cleaning after daily use. Preventive maintenance 1 first after 1 month "
                    "then after 1 year and 3 yearly. Wear replacement after approx. "
                    "9000 operating hours."
                ),
            )
        ]
    )

    assert chunk_type == ChunkType.MAINTENANCE_INTERVAL

def test_chunk_type_resolver_detects_interval_table_under_generic_path() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Sensor List",
                section_path=[
                    "7 Components",
                    "7.1 Macerators",
                    "Sensor List",
                ],
                text=(
                    "| Maintenance Intervals | Description | Interval | Refers to |\n"
                    "| Cleaning after daily use | Inspect cutters | Daily | Cutter set |"
                ),
                table_ids=["table_004"],
            )
        ]
    )

    assert chunk_type == ChunkType.MAINTENANCE_INTERVAL

def test_chunk_type_resolver_does_not_let_alarm_warning_ancestor_override_local_maintenance() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Maintenance Procedure",
                section_path=[
                    "6 Alarm and Warning Conditions",
                    "6.1 Maintenance",
                    "Maintenance Procedure",
                ],
                text=(
                    "Conduct routine inspection on the pump and connected parts to check "
                    "for a perfect seal. Check all support bearings and if necessary "
                    "replace them."
                ),
            )
        ]
    )

    assert chunk_type == ChunkType.MAINTENANCE_PROCEDURE

def test_chunk_type_resolver_detects_alarm_conditions_as_safety_warning() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Alarm Conditions",
                section_path=[
                    "6 Alarm and Warning Conditions",
                    "6.1 Alarm Conditions",
                ],
                text=(
                    "Alarm relay R5 will remain energized until the reset pushbutton "
                    "is pressed. The unit will shut down immediately when the low "
                    "pressure switch fault occurs."
                ),
            )
        ]
    )

    assert chunk_type == ChunkType.SAFETY_WARNING

def test_chunk_type_resolver_avoids_certification_false_positive_from_short_marker_substrings() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="System Introduction",
                section_path=[
                    "3 System Introduction",
                    "3.3 What it Does",
                ],
                text=(
                    "The FWC system is designed to collect food waste from attached "
                    "macerator stations and transfer the slurry to the dewatering press."
                ),
            )
        ]
    )

    assert chunk_type != ChunkType.CERTIFICATION_INFO
    assert chunk_type == ChunkType.GENERAL

def test_section_merge_policy_flushes_on_conflicting_semantic_sections() -> None:
    policy = SectionMergePolicy(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=220, chunk_overlap=20),
        min_section_text_length=20,
    )
    current_fragment = make_fragment(
        section_id="sec_intro",
        section_title="Procedure",
        section_path=["Manual", "Procedure"],
        text="Follow the procedure to service the assembly.",
        token_count=40,
    )
    next_fragment = make_fragment(
        section_id="sec_specs",
        section_title="Electrical Specifications",
        section_path=["Manual", "Procedure", "Electrical Specifications"],
        text="Operating limits: 24 V, 3 A, 50 Hz.",
        token_count=24,
        parent_section_id="sec_intro",
        table_ids=["table_001"],
    )

    should_flush = policy.should_flush_on_section_change(
        current_fragments=[current_fragment],
        next_fragment=next_fragment,
    )

    assert should_flush is True

def test_atex_section_title_resolves_to_certification_info() -> None:
    """A section whose title contains 'atex' must resolve to CERTIFICATION_INFO."""
    resolver = ChunkTypeResolver()
    fragment = make_fragment(
        section_title="ATEX / IECEx Approval",
        section_path=["Manufacturer's Certificates", "ATEX / IECEx Approval"],
        text=(
            "Ex II 2G Ex ia IIC T4 Gb. Certificate IECEx DEK 14.0052X. "
            "The device may be used in zone 1 and zone 2 hazardous areas."
        ),
    )
    result = ChunkTypeResolver().resolve(fragments=[fragment])
    assert result == ChunkType.CERTIFICATION_INFO, (
        "ATEX section title must resolve to CERTIFICATION_INFO"
    )

def test_iecex_section_title_resolves_to_certification_info() -> None:
    """A section whose title contains 'iecex' must resolve to CERTIFICATION_INFO."""
    fragment = make_fragment(
        section_title="IECEx Certificate Details",
        section_path=["Certificates", "IECEx Certificate Details"],
        text="IECEx certificate number IECEx DEK 14.0052X is valid for zone 1.",
    )
    result = ChunkTypeResolver().resolve(fragments=[fragment])
    assert result == ChunkType.CERTIFICATION_INFO

def test_approval_section_title_resolves_to_certification_info() -> None:
    """A section whose title contains 'approval' must resolve to CERTIFICATION_INFO."""
    fragment = make_fragment(
        section_title="Approval Information",
        section_path=["Manufacturer's Certificates", "Approval Information"],
        text="CE conformity declaration. Approved per applicable directives.",
    )
    result = ChunkTypeResolver().resolve(fragments=[fragment])
    assert result == ChunkType.CERTIFICATION_INFO

def test_chunk_type_resolver_preserves_standalone_troubleshooting_table_type() -> None:
    # Simulates TableFragmentBuilder.table_chunk_type() output for a table
    # whose parser-assigned TableCategory was TROUBLESHOOTING_TABLE, but
    # whose rendered text is too sparse to hit the keyword-signal threshold
    # on its own -- the classifier's verdict must not be second-guessed.
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Data",
                text="| A | B |\n| 1 | 2 |",
                chunk_type=ChunkType.TROUBLESHOOTING,
                standalone=True,
            )
        ]
    )

    assert chunk_type == ChunkType.TROUBLESHOOTING

def test_chunk_type_resolver_preserves_standalone_maintenance_interval_table_type() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Data",
                text="| A | B |\n| 1 | 2 |",
                chunk_type=ChunkType.MAINTENANCE_INTERVAL,
                standalone=True,
            )
        ]
    )

    assert chunk_type == ChunkType.MAINTENANCE_INTERVAL

def test_chunk_type_resolver_preserves_standalone_operation_instruction_table_type() -> None:
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Data",
                text="| A | B |\n| 1 | 2 |",
                chunk_type=ChunkType.OPERATION_INSTRUCTION,
                standalone=True,
            )
        ]
    )

    assert chunk_type == ChunkType.OPERATION_INSTRUCTION

def test_chunk_type_resolver_still_downgrades_non_standalone_weak_troubleshooting_signal() -> None:
    # Guards the other direction: the standalone gate must still matter --
    # a non-table-derived fragment that merely carries a TROUBLESHOOTING
    # chunk_type with no real signal in its text should still fall back to
    # keyword scoring (and lose, since there's no marker text here at all).
    resolver = ChunkTypeResolver()

    chunk_type = resolver.resolve(
        fragments=[
            make_fragment(
                section_title="Data",
                text="| A | B |\n| 1 | 2 |",
                chunk_type=ChunkType.TROUBLESHOOTING,
                standalone=False,
            )
        ]
    )

    assert chunk_type == ChunkType.GENERAL
