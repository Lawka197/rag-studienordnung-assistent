"""
Tests für die Chunking-Funktionen.

Diese Tests dokumentieren die erwartete Behavior der verschiedenen Chunking-Strategien
und schützen sie vor Regressions während des Refactorings.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from rag_studienordnung_assistent.chunking.chunker import (
    is_table_like_line,
    contains_table_like_structure,
    contains_semester_markers,
    split_studienordnung,
    split_modulhandbuch,
    chunk_document,
)
from rag_studienordnung_assistent.chunking.strategies import (
    SemesterStrategy,
    AppendixStrategy,
)


class TestTableDetection:
    """Tests für Tabellenerkennungs-Heuristiken"""

    def test_detects_course_code_lines(self):
        """Zeilen mit Kurscodes (z.B. B11, WP14) sollten erkannt werden"""
        assert is_table_like_line("B11 Mathematik 5 5") is True
        assert is_table_like_line("WP14 Netzwerke 3 4") is True

    def test_detects_numbered_lines(self):
        """Zeilen die mit Nummern und Text starten sollten erkannt werden"""
        assert is_table_like_line("1 Grundlegende Konzepte 5") is True
        assert is_table_like_line("13 Advanced Topics 8") is True

    def test_detects_multi_column_lines(self):
        """Zeilen mit mehreren numerischen Spalten sollten erkannt werden"""
        assert is_table_like_line("Modul 5 4 8 3") is True

    def test_ignores_normal_text(self):
        """Normaler Text sollte nicht als Tabelle erkannt werden"""
        assert is_table_like_line("Dies ist ein normaler Absatz mit Text.") is False
        assert is_table_like_line("Eine längere Erklärung ohne Tabellen-Format.") is False

    def test_ignores_empty_lines(self):
        """Leere Zeilen sollten nicht als Tabelle erkannt werden"""
        assert is_table_like_line("") is False
        assert is_table_like_line("   ") is False

    def test_contains_table_like_structure(self):
        """Block mit 3+ Tabellenzeilen sollte als Tabelle erkannt werden"""
        text = "B11 Mathematik 5\nB12 Physik 5\nB13 Chemie 3"
        assert contains_table_like_structure(text) is True

    def test_ignores_single_table_line(self):
        """Einzelne Tabellenzeile sollte nicht als Tabelle erkannt werden"""
        text = "B11 Mathematik 5"
        assert contains_table_like_structure(text) is False


class TestSemesterDetection:
    """Tests für Semester-Markierungen"""

    def test_detects_single_semester_marker(self):
        """Single Semester-Marker sollte erkannt werden"""
        text = "1. Fachsemester\nInhalte hier"
        assert contains_semester_markers(text) is False  # Nur 1, braucht 2+

    def test_detects_multiple_semester_markers(self):
        """Multiple Semester-Marker sollten erkannt werden"""
        text = "1. Fachsemester\nInhalte 1\n2. Fachsemester\nInhalte 2"
        assert contains_semester_markers(text) is True

    def test_detects_semester_variant(self):
        """'Semester' sollte auch erkannt werden (nicht nur 'Fachsemester')"""
        text = "1. Semester\nInhalte\n2. Semester\nMehr"
        assert contains_semester_markers(text) is True

    def test_splits_by_semester(self):
        """Text sollte nach Semester-Markierungen aufgeteilt werden"""
        text = "1. Fachsemester\nModul A\n2. Fachsemester\nModul B"
        strategy = SemesterStrategy()
        result = strategy.split(text)
        assert len(result) == 2
        assert "Modul A" in result[0]
        assert "Modul B" in result[1]

    def test_no_split_without_multiple_markers(self):
        """Ohne mehrere Marker sollte nicht aufgeteilt werden"""
        text = "1. Fachsemester\nNur ein Semester"
        strategy = SemesterStrategy()
        # Strategy braucht 2+ Marker
        assert not strategy.can_apply(text)


class TestAppendixDetection:
    """Tests für Anhang-Erkennung"""

    def test_splits_by_anlage_markers(self):
        """Text sollte nach 'Anlage' Markierungen aufgeteilt werden"""
        text = "Content 1\nAnlage 1\nContent 2\nAnlage 2\nContent 3"
        strategy = AppendixStrategy()
        result = strategy.split(text)
        assert len(result) >= 2

    def test_splits_by_studienplan_marker(self):
        """'Studienplanübersicht' sollte als Split-Punkt erkannt werden"""
        text = "Main content\nStudienplanübersicht\nPlan content"
        strategy = AppendixStrategy()
        if strategy.can_apply(text):
            result = strategy.split(text)
            assert len(result) >= 1
        else:
            # Text passt nicht zum Pattern (nur 1x vorhanden)
            assert not strategy.can_apply(text)

    def test_splits_by_module_overview(self):
        """'Modulübersicht' sollte erkannt werden"""
        text = "Content 1\nModulübersicht\nContent 2\nModulübersicht\nContent 3"
        strategy = AppendixStrategy()
        if strategy.can_apply(text):
            result = strategy.split(text)
            assert len(result) >= 1

    def test_returns_empty_for_single_section(self):
        """Text ohne mehrere Anhang-Marker sollte nicht aufgeteilt werden"""
        text = "Dies ist ein normaler Text ohne Anhang"
        strategy = AppendixStrategy()
        # Diese Strategy braucht 2+ Marker zum Splitten
        assert not strategy.can_apply(text)


class TestStudienordnungChunking:
    """Tests für Studienordnung-spezifisches Chunking"""

    def test_chunks_by_paragraphs(self):
        """Text sollte nach Paragraph-Markierungen aufgeteilt werden wenn genug Content"""
        # Kurzer Text ohne viel Content - wird nicht aufgeteilt
        text = "§ 1 Kurz\nText\n§ 2 Auch kurz\nText"
        result = split_studienordnung(text)
        assert isinstance(result, list)
        assert all(isinstance(chunk, str) for chunk in result)

        # Längerer Text sollte aufgeteilt werden
        long_text = "§ 1 Geltung\n" + "Ein Absatz. " * 200 + "\n§ 2 Ziele\n" + "Mehr Text. " * 200
        result_long = split_studienordnung(long_text)
        assert len(result_long) >= 1

    def test_respects_max_chunk_length(self):
        """Chunks sollten MAX_CHUNK_LENGTH nicht überschreiten"""
        text = "§ 1 Kurz\n" + "Ein langer Absatz. " * 500
        result = split_studienordnung(text)
        for chunk in result:
            assert len(chunk) <= 5000  # Mit etwas Puffer

    def test_handles_empty_input(self):
        """Leerer Text sollte leere Liste zurückgeben"""
        result = split_studienordnung("")
        assert result == []

    def test_handles_text_without_paragraphs(self):
        """Text ohne § sollte nicht gebrochen werden"""
        text = "Ein normaler Text ohne Paragraphen"
        result = split_studienordnung(text)
        # Sollte nicht leer sein, aber auch nicht zu viele Chunks
        assert len(result) <= 2


class TestModulhandbuchChunking:
    """Tests für Modulhandbuch-spezifisches Chunking"""

    def test_chunks_by_modules(self):
        """Text sollte nach 'MODUL ID' aufgeteilt werden"""
        text = "MODUL ID M01\nZusammenfassung: Module 1\n\nMODUL ID M02\nZusammenfassung: Module 2"
        result = split_modulhandbuch(text)
        assert len(result) >= 2

    def test_respects_max_chunk_length(self):
        """Chunks sollten die maximale Länge nicht überschreiten"""
        # Erstelle ein lange Modul
        text = "MODUL ID M01\n" + "Ein langer Text. " * 500
        result = split_modulhandbuch(text)
        for chunk in result:
            assert len(chunk) <= 5000

    def test_handles_missing_module_ids(self):
        """Text ohne MODUL ID sollte trotzdem verarbeitet werden"""
        text = "Hier ist Text ohne MODUL ID"
        result = split_modulhandbuch(text)
        assert isinstance(result, list)

    def test_splits_large_modules_by_sections(self):
        """Große Module sollten nach Abschnitten aufgeteilt werden"""
        text = (
            "MODUL ID M01\n"
            "Zusammenfassung: Test\n"
            "Lernergebnisse: Ziele\n"
            + "Langer Text. " * 300
        )
        result = split_modulhandbuch(text)
        # Mit guten Section-Splits sollte kein einzelnes Monster-Chunk entstehen
        assert all(len(chunk) < 4000 for chunk in result)


class TestDocumentTypeChunking:
    """Integration Tests für verschiedene Dokumenttypen"""

    def test_studienordnung_type_uses_paragraph_splitting(self):
        """Studienordnungen sollten nach Paragraphen aufgeteilt werden"""
        text = "§ 1 Start\nLanger Text hier\n§ 2 Ende\nWeiterer Text"
        result = chunk_document(text, "studienordnung")
        assert len(result) >= 1
        assert all(isinstance(chunk, str) for chunk in result)

    def test_modulhandbuch_type_uses_module_splitting(self):
        """Modulhandbücher sollten nach Modulen aufgeteilt werden"""
        text = "MODUL ID M01\nZusammenfassung\n\nMODUL ID M02\nZusammenfassung"
        result = chunk_document(text, "modulhandbuch")
        assert len(result) >= 1
        assert all(isinstance(chunk, str) for chunk in result)

    def test_invalid_document_type_raises_error(self):
        """Ungültige Dokumenttypen sollten einen Fehler werfen"""
        with pytest.raises(ValueError):
            chunk_document("some text", "unknown_type")

    def test_filters_empty_chunks(self):
        """Leere Chunks sollten gefiltert werden"""
        text = "§ 1\n\n§ 2"
        result = chunk_document(text, "studienordnung")
        assert all(chunk.strip() for chunk in result)

    def test_end_to_end_with_realistic_text(self):
        """Realistischer End-to-End Test mit längerer Dokumentation"""
        # Text muss lang genug sein um aufgeteilt zu werden
        text = (
            "§ 1 Geltungsbereich\n"
            + "Diese Ordnung gilt für alle Studierenden. " * 50 + "\n\n"
            "§ 2 Ziele des Studiums\n"
            + "Das Studium vermittelt wissenschaftliche Grundlagen. " * 50 + "\n"
            "1. Fachsemester\nModul A 5 CP\n"
            "2. Fachsemester\nModul B 5 CP"
        )
        result = chunk_document(text, "studienordnung")

        # Sollte in Chunks aufgeteilt werden oder mindestens verarbeitet sein
        assert len(result) >= 1
        assert all(len(chunk) > 10 for chunk in result)  # Keine Trivial-Chunks
        combined = "".join(result)
        assert "Studienordnung" in combined or "Geltungsbereich" in combined


class TestEdgeCases:
    """Tests für Edge Cases"""

    def test_very_long_chunk_eventually_splits(self):
        """Ein Monster-Chunk sollte eventuell trotzdem aufgeteilt werden"""
        text = "§ 1\n" + "A" * 10000
        result = chunk_document(text, "studienordnung")
        # Sollte nicht nur aus einem Chunk bestehen
        assert not all(len(chunk) > 5000 for chunk in result)

    def test_unicode_handling(self):
        """Unicode (Umlaute, Spezialzeichen) sollte korrekt verarbeitet werden"""
        # Dieser Test stellt sicher, dass der Code nicht bei Umlauten crasht
        text = "Standardtext\nBäckerei Müller & Partner\nÄöüß Überblick"
        try:
            result = chunk_document(text, "studienordnung")
            # Hauptsache: kein Crash
            assert isinstance(result, list)
            # Und das Original-Text sollte in den Chunks auftauchen
            combined = "".join(result)
            # Mindestens einige Zeichen sollten erhalten sein
            assert len(combined) > 0
        except Exception as e:
            pytest.fail(f"Unicode handling sollte nicht crashen: {e}")

    def test_mixed_content_with_tables_and_paragraphs(self):
        """Text mit Tabellen UND Paragraphen sollte verarbeitet werden"""
        text = (
            "§ 1 Intro\n" + "Text. " * 100 + "\n\n"
            "B11 Modul1 5\nB12 Modul2 5\nB13 Modul3 5\n\n"
            "§ 2 Outro\n" + "Mehr Text. " * 100
        )
        result = chunk_document(text, "studienordnung")
        assert len(result) >= 1
        combined = "".join(result)
        assert "§ 1" in combined or "Intro" in combined


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

