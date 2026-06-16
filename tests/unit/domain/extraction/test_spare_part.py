def test_spare_part_has_part_number(sample_spare_part) -> None:
    assert sample_spare_part.has_part_number()