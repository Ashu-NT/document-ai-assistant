import json


class ExtractionChunkCoverageMapper:
    @staticmethod
    def dump_chunk_ids(values: list[str]) -> str:
        return json.dumps(list(values))

    @staticmethod
    def load_chunk_ids(raw_value: str | None) -> list[str]:
        if not raw_value:
            return []

        try:
            loaded = json.loads(raw_value)
        except json.JSONDecodeError:
            return []

        if not isinstance(loaded, list):
            return []

        return [str(value) for value in loaded if str(value)]
