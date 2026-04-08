"""
Chunking-Strategien als abstrakte und konkrete Klassen.

Jede Strategie kann entscheiden, ob sie auf einen Text anwendbar ist,
und ihn dann entsprechend aufteilen. Das eliminiert die wiederholte
Fallback-Logik aus dem ursprünglichen Code.
"""

from abc import ABC, abstractmethod
from typing import List
import re

from rag_studienordnung_assistent.chunking import patterns


class ChunkingStrategy(ABC):

    @abstractmethod
    def can_apply(self, text: str) -> bool:
        pass

    @abstractmethod
    def split(self, text: str) -> List[str]:
        pass


class SemesterStrategy(ChunkingStrategy):


    def can_apply(self, text: str) -> bool:
        semester_pattern = patterns.SEMESTER_PATTERNS["semester_marker"]["pattern"]
        threshold = patterns.SEMESTER_PATTERNS["semester_marker"]["threshold"]

        matches = re.findall(semester_pattern, text)
        return len(matches) >= threshold

    def split(self, text: str) -> List[str]:
        """Teilt Text nach Semester-Markierungen"""
        semester_split_pattern = patterns.SEMESTER_PATTERNS["semester_split_point"]["pattern"]
        parts = [part.strip() for part in re.split(semester_split_pattern, text) if part.strip()]
        return parts if len(parts) > 1 else []


class AppendixStrategy(ChunkingStrategy):
    """
    Strategie für Anhang/Abschnitt-basiertes Splitting.

    Erkennt Patterns wie:
    - "Anlage 1"
    - "Studienplanübersicht"
    - "Modulübersicht"
    - "Wahlpflichtmodule"
    """

    def can_apply(self, text: str) -> bool:
        appendix_pattern = patterns.APPENDIX_PATTERNS["appendix_marker"]["pattern"]
        parts = [part.strip() for part in re.split(appendix_pattern, text) if part.strip()]
        return len(parts) > 1

    def split(self, text: str) -> List[str]:
        appendix_pattern = patterns.APPENDIX_PATTERNS["appendix_marker"]["pattern"]
        parts = [part.strip() for part in re.split(appendix_pattern, text) if part.strip()]
        return parts if len(parts) > 1 else []


class TableStrategy(ChunkingStrategy):

    TABLE_HEURISTIC_THRESHOLD = 3

    def _is_table_like_line(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False

        patterns = [
            r"^[A-Z]{1,3}\d{2,}[a-zA-Z]?\b",  # z. B. B11, WP14
            r"^\d{1,2}\s+[A-ZÄÖÜa-zäöüß]",    # z. B. 13 Grundlegende Konzepte
            r"^[A-ZÄÖÜa-zäöüß].*\b\d+\b.*\b\d+\b",  # mehrere numerische Spalten
        ]

        return any(re.search(pattern, stripped) for pattern in patterns)

    def can_apply(self, text: str) -> bool:
        lines = [line for line in text.split("\n") if line.strip()]
        if len(lines) < 3:
            return False

        table_like_lines = sum(1 for line in lines if self._is_table_like_line(line))
        return table_like_lines >= self.TABLE_HEURISTIC_THRESHOLD

    def split(self, text: str) -> List[str]:
        return []


class LengthStrategy(ChunkingStrategy):

    def can_apply(self, text: str) -> bool:
        return True

    def split(self, text: str) -> List[str]:

        return []


class StrategyChain:

    def __init__(self, strategies: List[ChunkingStrategy] = None):
        if strategies is None:
            strategies = [
                SemesterStrategy(),
                AppendixStrategy(),
                TableStrategy(),
                LengthStrategy(),
            ]
        self.strategies = strategies

    def find_applicable_strategy(self, text: str) -> ChunkingStrategy:
        for strategy in self.strategies:
            if strategy.can_apply(text):
                return strategy

        return self.strategies[-1]

