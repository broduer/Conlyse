from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..models.intermediate import GameData

Out = TypeVar("Out")


class BaseAggregator(ABC, Generic[Out]):
    """Takes the full list of extracted GameData and produces an aggregate output."""

    @abstractmethod
    def aggregate(self, games: list[GameData]) -> Out:
        ...
