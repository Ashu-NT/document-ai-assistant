from __future__ import annotations

from tests.unit.cli_scripts._test_cli_scripts_part1 import _load_script


def _mod():
    return _load_script("report_text_corruption_candidates")


# --- find_long_alpha_runs ---------------------------------------------------


def test_find_long_alpha_runs_returns_empty_for_short_text():
    mod = _mod()
    assert mod.find_long_alpha_runs("short words here", min_run_length=20) == []


def test_find_long_alpha_runs_excludes_digits_and_hyphens():
    # A dense identifier like this must never contribute a qualifying run --
    # this is the exact false-positive shape a prior, rejected heuristic used
    # to misfire on.
    mod = _mod()
    runs = mod.find_long_alpha_runs(
        "Part number 6ES7131-6BF00-0CA0-somewhatlongsuffixhere",
        min_run_length=20,
    )
    assert runs == ["somewhatlongsuffixhere"]


def test_find_long_alpha_runs_finds_merged_phrase():
    mod = _mod()
    text = "Wecertifythattheresultfromtestsonthematerialitself compliewiththtermsofthordr"
    runs = mod.find_long_alpha_runs(text, min_run_length=20)
    assert len(runs) == 2


# --- is_corruption_candidate -------------------------------------------------


def test_is_corruption_candidate_false_for_single_long_compound_word():
    # A real, correctly-spelled German compound noun is legitimate content,
    # not corruption -- one long run alone must not trip the candidate gate.
    mod = _mod()
    text = "Jeder Buchstabe wird umlaufend einen Versiegelungskehlnaht bekommen."
    assert not mod.is_corruption_candidate(
        text, min_run_length=20, min_run_count=3
    )


def test_is_corruption_candidate_true_for_repeated_merged_phrases():
    mod = _mod()
    text = (
        "Installation plans and operating manuals should be supplied to the ship "
        "Alistorplanshouldbedisplayedshowingthespacescovered "
        "includeprovisionsforaflowtestofeachsectionatleastannuallytocheck "
        "forpossiblecloggingordeteriorationinthedischargepiping"
    )
    assert mod.is_corruption_candidate(text, min_run_length=20, min_run_count=3)


# --- scan_chunk_rows ---------------------------------------------------------


def test_scan_chunk_rows_flags_only_matching_rows():
    mod = _mod()
    rows = [
        (
            "chunk_1",
            "doc_a",
            "aaaaaaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbb cccccccccccccccccccc",
            1,
            1,
        ),
        ("chunk_2", "doc_a", "ordinary short sentence", 2, 2),
    ]
    candidates = mod.scan_chunk_rows(rows, min_run_length=20, min_run_count=3)
    assert [c.chunk_id for c in candidates] == ["chunk_1"]
    assert candidates[0].run_count == 3
    assert candidates[0].page_start == 1


# --- group_by_document -------------------------------------------------------


def test_group_by_document_sorts_by_flagged_chunk_count_desc():
    mod = _mod()
    candidates = [
        mod.ChunkCandidate("c1", "doc_a", 1, 1, 3, ["x" * 20]),
        mod.ChunkCandidate("c2", "doc_b", 1, 1, 3, ["y" * 20]),
        mod.ChunkCandidate("c3", "doc_b", 2, 2, 3, ["z" * 20]),
    ]
    groups = mod.group_by_document(candidates, {"doc_a": "a.pdf", "doc_b": "b.pdf"})
    assert [g.document_id for g in groups] == ["doc_b", "doc_a"]
    assert groups[0].file_name == "b.pdf"


# --- parse_args ---------------------------------------------------------------


def test_parse_args_defaults():
    mod = _mod()
    args = mod.parse_args([])
    assert args.document_id is None
    assert args.min_run_length == mod.DEFAULT_MIN_RUN_LENGTH
    assert args.min_run_count == mod.DEFAULT_MIN_RUN_COUNT
    assert args.json is False


def test_parse_args_overrides():
    mod = _mod()
    args = mod.parse_args(
        ["--document-id", "doc_123", "--min-run-length", "25", "--min-run-count", "2", "--json"]
    )
    assert args.document_id == "doc_123"
    assert args.min_run_length == 25
    assert args.min_run_count == 2
    assert args.json is True
