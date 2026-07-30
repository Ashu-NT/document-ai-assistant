import pytest

from tests.integration.db._test_extraction_repository_part1 import *  # noqa: F401,F403
from tests.integration.db._test_extraction_repository_part2 import *  # noqa: F401,F403

# Extraction-family rows (extraction_results.document_id, and every entity's
# source_chunk_id) are now enforced FKs to documents/chunks, so a real
# "doc_001"/"chunk_001" row must exist before sample_extraction_result (and
# friends) can be inserted.
pytestmark = pytest.mark.usefixtures("seeded_document_and_chunk")
