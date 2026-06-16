def test_extraction_result_has_results(sample_extraction_result) -> None:
    assert sample_extraction_result.has_results()


def test_extraction_result_counts_tasks(sample_extraction_result) -> None:
    assert sample_extraction_result.task_count() == 1


def test_extraction_result_counts_spare_parts(sample_extraction_result) -> None:
    assert sample_extraction_result.spare_part_count() == 1