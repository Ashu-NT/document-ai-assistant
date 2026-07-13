class BooleanMarkerDetector:
    _BOOLEAN_MARKERS = {
        "x",
        "X",
        "1",
        "yes",
        "ok",
        "true",
        "checked",
        "check",
        "*",
        "-",
        "•",
    }

    def is_boolean_marker(self, value: str) -> bool:
        text = value.strip()
        if not text:
            return True
        if text in self._BOOLEAN_MARKERS:
            return True
        return len(text) <= 3 and text.casefold() in {
            marker.casefold() for marker in self._BOOLEAN_MARKERS
        }
