from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.application.validation.common.validation_result import ValidationResult

T = TypeVar("T")


class Validator(ABC, Generic[T]):
    @abstractmethod
    def validate(self, value: T) -> ValidationResult:
        ...