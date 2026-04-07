import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from rag_studienordnung_assistent.chunking.chunker import (
    normalize_newlines,
    remove_footers,
    fix_hyphenation,
    normalize_whitespace,
    preprocess_text,
)


class TestNormalizeNewlines:

    def test_converts_crlf_to_lf(self):
        text = "Hallo\r\nWelt"
        result = normalize_newlines(text)
        assert result == "Hallo\nWelt"

    def test_converts_cr_to_lf(self):
        text = "Hallo\rWelt"
        result = normalize_newlines(text)
        assert result == "Hallo\nWelt"

    def test_replaces_special_unicode_spaces(self):
        text = "Hallo\xa0Welt\u202fTest\u2007Foo\u2009Bar"
        result = normalize_newlines(text)
        assert "\xa0" not in result
        assert "\u202f" not in result
        assert "\u2007" not in result
        assert "\u2009" not in result
        assert all(c == " " for c in result if c in " \xa0\u202f\u2007\u2009")


class TestRemoveFooters:

    def test_removes_htw_footer_format1(self):
        text = "Seite 5 Amtliches Mitteilungsblatt der HTW Berlin Nr. 1/2023\nHaupttext"
        result = remove_footers(text)
        assert "Seite 5" not in result
        assert "Haupttext" in result

    def test_removes_htw_footer_format2(self):
        text = "Haupttext\nNr. 2/2024 Amtliches Mitteilungsblatt der HTW Berlin Seite 10"
        result = remove_footers(text)
        assert "Nr. 2/2024" not in result
        assert "Haupttext" in result

    def test_removes_modulhandbuch_footer(self):
        text = "Modulhandbuch der HTW Berlin 2023/24\nTexte hier"
        result = remove_footers(text)
        assert "Modulhandbuch der HTW Berlin" not in result
        assert "Texte hier" in result

    def test_preserves_non_footer_text(self):
        text = "Das ist wichtiger Content\nSeite ist ein normales Wort"
        result = remove_footers(text)
        assert "Das ist wichtiger Content" in result
        assert "Seite ist ein normales Wort" in result


class TestFixHyphenation:

    def test_joins_hyphenated_words(self):
        text = "Studienord-\nnung ist wichtig"
        result = fix_hyphenation(text)
        assert "Studienordnung" in result
        assert "-\n" not in result

    def test_handles_hyphen_with_spaces(self):
        text = "Test -\n word"
        result = fix_hyphenation(text)
        assert "Test" in result and "word" in result

    def test_preserves_normal_hyphens(self):
        text = "Haupt-Thema ist wichtig"
        result = fix_hyphenation(text)
        assert "Haupt-Thema" in result

    def test_handles_umlauts(self):
        text = "Gründungs-\nphase\nÄnderungs-\nantrag"
        result = fix_hyphenation(text)
        assert "Gründungsphase" in result
        assert "Änderungsantrag" in result


class TestNormalizeWhitespace:

    def test_removes_multiple_spaces(self):
        text = "Hallo    Welt   Test"
        result = normalize_whitespace(text)
        assert "    " not in result
        assert "Hallo Welt Test" in result

    def test_removes_tabs(self):
        text = "Hallo\t\tWelt"
        result = normalize_whitespace(text)
        assert "\t" not in result
        assert "Hallo Welt" in result

    def test_collapses_multiple_newlines(self):
        text = "Hallo\n\n\n\nWelt"
        result = normalize_whitespace(text)
        assert "\n\n\n" not in result
        assert "Hallo\n\nWelt" in result

    def test_strips_leading_trailing_whitespace(self):
        text = "   Hallo Welt   \n\n"
        result = normalize_whitespace(text)
        assert result == "Hallo Welt"


class TestPreprocessText:

    def test_full_preprocessing_pipeline(self):
        text = (
            "   Hallo\r\nWelt\u202fTest\n\n\n"
            "Studienor-\ndnung ist wichtig\n"
            "Seite 5 Amtliches Mitteilungsblatt der HTW Berlin Nr. 1/2023\n"
            "Mehr  Text   hier"
        )
        result = preprocess_text(text)

        assert "Studienordnung" in result
        assert "\r" not in result
        assert "Seite 5 Amtliches" not in result
        assert "\n\n\n" not in result
        assert "Mehr Text hier" in result

    def test_empty_text(self):
        result = preprocess_text("")
        assert result == ""

    def test_whitespace_only_text(self):
        result = preprocess_text("   \n\n\t\t  ")
        assert result == ""

    def test_preserves_important_structure(self):
        text = "§ 1 Geltungsbereich\n\nAbs. 1 Text hier"
        result = preprocess_text(text)
        assert "§ 1" in result
        assert "Abs. 1 Text hier" in result
        assert "\n\n" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

