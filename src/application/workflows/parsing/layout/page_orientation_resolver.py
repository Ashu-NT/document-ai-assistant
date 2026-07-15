class PageOrientationResolver:
    def resolve(
        self,
        *,
        page_width: float | None,
        page_height: float | None,
    ) -> str | None:
        if (
            page_width is None
            or page_height is None
            or page_width <= 0
            or page_height <= 0
        ):
            return None
        if abs(page_width - page_height) <= min(page_width, page_height) * 0.05:
            return "square"
        if page_width > page_height:
            return "landscape"
        return "portrait"
