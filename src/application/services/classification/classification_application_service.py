from src.application.services.classification.classification_service import (
    ClassificationService,
)


class ClassificationApplicationService:
    def __init__(self, classification: ClassificationService) -> None:
        self.classification = classification