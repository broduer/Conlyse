from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..models.intermediate import GameData


class BaseExtractor(ABC):
    """Opens a single replay file and returns a GameData instance."""

    @abstractmethod
    def extract(self, file_path: Path) -> GameData:
        ...

    def extract_safe(self, file_path: Path) -> Optional[GameData]:
        """extract() wrapped with exception handling; returns None on failure."""
        try:
            return self.extract(file_path)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).error("Failed to extract %s: %s", file_path.name, exc)
            return None
