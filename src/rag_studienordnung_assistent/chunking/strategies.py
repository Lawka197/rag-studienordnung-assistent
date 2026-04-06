"""
Chunking-Strategien als abstrakte und konkrete Klassen.

Jede Strategie kann entscheiden, ob sie auf einen Text anwendbar ist,
und ihn dann entsprechend aufteilen. Das eliminiert die wiederholte
Fallback-Logik aus dem ursprünglichen Code.

Nutzt zentrale Patterns aus patterns.py.
"""

from abc import ABC, abstractmethod
from typing import List
import re

from rag_studienordnung_assistent.chunking import patterns


class ChunkingStrategy(ABC):
    """
    Basis-Interface für alle Chunking-Strategien.

    Eine Strategie kann:
    1. Prüfen, ob sie auf einen Text anwendbar ist (can_apply)
    2. Den Text entsprechend aufteilen (split)
    """

    @abstractmethod
    def can_apply(self, text: str) -> bool:
        """
        Prüft, ob diese Strategie auf den Text anwendbar ist.

        Args:
            text: Der zu überprüfende Text

        Returns:
            True wenn Strategie anwendbar, False sonst
        """
        pass

    @abstractmethod
    def split(self, text: str) -> List[str]:
        """
        Teilt den Text nach dieser Strategie auf.

        Args:
            text: Der zu teilende Text

        Returns:
            Liste von Chunks, oder leere Liste wenn Split nicht möglich
        """
        pass


class SemesterStrategy(ChunkingStrategy):
    """
    Strategie für Semester/Fachsemester-basiertes Splitting.

    Erkannt Patterns wie:
    - "1. Fachsemester"
    - "2. Semester"
    etc.

    Nutzt Patterns aus patterns.py.
    """

    def can_apply(self, text: str) -> bool:
        """Text muss 2+ Semester-Marker enthalten"""
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

    Erkannt Patterns wie:
    - "Anlage 1"
    - "Studienplanübersicht"
    - "Modulübersicht"
    - "Wahlpflichtmodule"
    etc.

    Nutzt Patterns aus patterns.py.
    """

    def can_apply(self, text: str) -> bool:
        """Text muss 2+ Anhang-Marker enthalten"""
        appendix_pattern = patterns.APPENDIX_PATTERNS["appendix_marker"]["pattern"]
        parts = [part.strip() for part in re.split(appendix_pattern, text) if part.strip()]
        return len(parts) > 1

    def split(self, text: str) -> List[str]:
        """Teilt Text nach Anhang-Markierungen"""
        appendix_pattern = patterns.APPENDIX_PATTERNS["appendix_marker"]["pattern"]
        parts = [part.strip() for part in re.split(appendix_pattern, text) if part.strip()]
        return parts if len(parts) > 1 else []


class TableStrategy(ChunkingStrategy):
    """
    Strategie für Tabellen-basiertes Splitting.

    Erkannt tabellenartige Zeilen und teilt entsprechend auf.
    Diese Strategie wird in split_table_like_block implementiert.
    """

    TABLE_HEURISTIC_THRESHOLD = 3  # Mindestens 3 Tabellenzeilen

    def _is_table_like_line(self, line: str) -> bool:
        """Heuristik für tabellenartige Zeilen"""
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
        """Text muss 3+ Tabellenzeilen enthalten"""
        lines = [line for line in text.split("\n") if line.strip()]
        if len(lines) < 3:
            return False

        table_like_lines = sum(1 for line in lines if self._is_table_like_line(line))
        return table_like_lines >= self.TABLE_HEURISTIC_THRESHOLD

    def split(self, text: str) -> List[str]:
        """
        Teilt tabellenartige Blöcke.

        Diese Implementierung ist hier ein Placeholder,
        da die volle split_table_like_block Logik komplexer ist.
        Sie wird von der Hauptfunktion direkt aufgerufen.
        """
        return []


class LengthStrategy(ChunkingStrategy):
    """
    Fallback-Strategie für Längenbases Splitting.

    Dies ist die letzte Strategie die immer anwendbar ist,
    falls keine spezialisierte Strategie funktioniert hat.
    """

    def can_apply(self, text: str) -> bool:
        """Diese Strategie ist immer anwendbar (Fallback)"""
        return True

    def split(self, text: str) -> List[str]:
        """
        Diese Methode wird nicht direkt verwendet,
        da split_by_length die volle Logik enthält.
        """
        return []


class StrategyChain:
    """
    Orchestriert mehrere Chunking-Strategien in einer definierten Reihenfolge.

    Die Kette versucht jede Strategie nacheinander:
    1. Semester-Strategie
    2. Anhang-Strategie
    3. Tabellen-Strategie
    4. Längen-Strategie (Fallback)

    Diese Klasse eliminiert die wiederholte "if can_apply -> split" Logik.
    """

    def __init__(self, strategies: List[ChunkingStrategy] = None):
        """
        Initialisiert die Strategy Chain.

        Args:
            strategies: Liste von Strategien in Anwendungsreihenfolge.
                       Falls None, wird die Standard-Reihenfolge verwendet.
        """
        if strategies is None:
            strategies = [
                SemesterStrategy(),
                AppendixStrategy(),
                TableStrategy(),
                LengthStrategy(),
            ]
        self.strategies = strategies

    def find_applicable_strategy(self, text: str) -> ChunkingStrategy:
        """
        Findet die erste anwendbare Strategie für den Text.

        Args:
            text: Der zu analysierende Text

        Returns:
            Die erste Strategie die can_apply(text) == True zurückgibt
        """
        for strategy in self.strategies:
            if strategy.can_apply(text):
                return strategy

        # Sollte nicht vorkommen da LengthStrategy immer True zurückgibt
        return self.strategies[-1]  # Fallback zur letzten Strategie

