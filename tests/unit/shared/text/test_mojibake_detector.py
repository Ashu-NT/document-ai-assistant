from pathlib import Path

from src.shared.text.mojibake_detector import iter_python_files, scan_paths_for_mojibake


def test_scan_flags_a_file_containing_a_mojibake_marker(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.py"
    bad_file.write_text(
        'MESSAGE = "This is fine, but this partâ€”here is garbled."\n',
        encoding="utf-8",
    )

    matches = scan_paths_for_mojibake([bad_file])

    assert len(matches) == 1
    assert matches[0].file_path == bad_file
    assert matches[0].line_number == 1


def test_scan_does_not_flag_a_clean_file_with_a_real_em_dash(tmp_path: Path) -> None:
    clean_file = tmp_path / "clean.py"
    clean_file.write_text(
        'MESSAGE = "This uses a real em-dash — not mojibake."\n',
        encoding="utf-8",
    )

    matches = scan_paths_for_mojibake([clean_file])

    assert matches == []


def test_iter_python_files_returns_empty_list_for_a_missing_directory(tmp_path: Path) -> None:
    assert iter_python_files(tmp_path / "does_not_exist") == []


def test_iter_python_files_finds_py_files_recursively(tmp_path: Path) -> None:
    (tmp_path / "nested").mkdir()
    (tmp_path / "top.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "nested" / "inner.py").write_text("y = 2\n", encoding="utf-8")
    (tmp_path / "not_python.txt").write_text("ignore me\n", encoding="utf-8")

    files = iter_python_files(tmp_path)

    assert {f.name for f in files} == {"top.py", "inner.py"}
