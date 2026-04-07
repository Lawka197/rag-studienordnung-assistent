FOOTER_PATTERNS = {
    "htw_footer_format_1": {
        "pattern": r"Seite\s+\d+\s+Amtliches Mitteilungsblatt der HTW Berlin Nr\.\s*\d+/\d+",
        "description": "HTW Berlin Fußzeile Format: 'Seite X Amtliches Mitteilungsblatt der HTW Berlin Nr. Y/Z'",
        "example": "Seite 5 Amtliches Mitteilungsblatt der HTW Berlin Nr. 1/2023",
    },
    "htw_footer_format_2": {
        "pattern": r"Nr\.\s*\d+/\d+\s+Amtliches Mitteilungsblatt der HTW Berlin Seite\s+\d+",
        "description": "HTW Berlin Fußzeile Format: 'Nr. Y/Z Amtliches Mitteilungsblatt der HTW Berlin Seite X'",
        "example": "Nr. 2/2024 Amtliches Mitteilungsblatt der HTW Berlin Seite 10",
    },
    "modulhandbuch_footer": {
        "pattern": r"Modulhandbuch der HTW Berlin\s+\d+/\d+",
        "description": "Modulhandbuch Fußzeile: 'Modulhandbuch der HTW Berlin Y/Z'",
        "example": "Modulhandbuch der HTW Berlin 2023/24",
    },
}

def get_footer_patterns_list() -> list:
    return [info["pattern"] for info in FOOTER_PATTERNS.values()]


HYPHENATION_PATTERNS = {
    "hyphen_at_newline": {
        "pattern": r"(?<=[A-Za-zÄÖÜäöüß])-\n(?=[A-Za-zÄÖÜäöüß])",
        "description": "Bindestrich direkt gefolgt von Zeilenumbruch und Buchstabe (z.B. 'Studien-\\nordnung')",
        "replacement": "",
        "example_before": "Studien-\nordnung",
        "example_after": "Studienordnung",
    },
    "hyphen_with_spaces_at_newline": {
        "pattern": r"(?<=[A-Za-zÄÖÜäöüß])\s*-\s*\n\s*(?=[A-Za-zÄÖÜäöüß])",
        "description": "Bindestrich mit Leerzeichen vor/nach Zeilenumbruch",
        "replacement": "",
        "example_before": "Test - \n word",
        "example_after": "Test word",
    },
}

WHITESPACE_PATTERNS = {
    "multiple_spaces_or_tabs": {
        "pattern": r"[ \t]+",
        "description": "Mehrere Spaces oder Tabs in Folge",
        "replacement": " ",
        "rationale": "Normalize zu einzelnem Space",
    },
    "multiple_newlines": {
        "pattern": r"\n{3,}",
        "description": "3 oder mehr Zeilenumbrüche hintereinander",
        "replacement": "\n\n",
        "rationale": "Collapse zu 2 Zeilenumbrüchen (Paragraph-Trennung)",
    },
}

TABLE_LINE_PATTERNS = {
    "module_code": {
        "pattern": r"^[A-Z]{1,3}\d{2,}[a-zA-Z]?\b",
        "description": "Modul-Codes wie B11, WP14, WPM01",
        "rationale": "Häufig erstes Element in Tabellenzeilen von Studienplänen",
        "examples": ["B11", "WP14", "WPM01a"],
    },
    "numbered_with_text": {
        "pattern": r"^\d{1,2}\s+[A-ZÄÖÜa-zäöüß]",
        "description": "Nummern (1-99) gefolgt von Text, z.B. '13 Grundlegende Konzepte'",
        "rationale": "Häufig erstes Element in nummerierten Listen/Tabellen",
        "examples": ["1 Grundlagen", "13 Advanced Topics"],
    },
    "multi_column_numbers": {
        "pattern": r"^[A-ZÄÖÜa-zäöüß].*\b\d+\b.*\b\d+\b",
        "description": "Text mit 2+ numerischen Spalten hintereinander",
        "rationale": "Typisch für Tabellenlayouts (z.B. 'Modul 5 4 8 3')",
        "examples": ["Modul 5 4 8", "Kurs 10 20 Std"],
    },
}

def get_table_line_patterns_list() -> list:
    return [info["pattern"] for info in TABLE_LINE_PATTERNS.values()]


PARAGRAPH_PATTERNS = {
    "paragraph_header": {
        "pattern": r"(?m)(?=^\s*§\s*\d+[a-zA-Z](?:\s*[a-z])?\b)",
        "description": "Paragraph-Überschriften in Studienordnungen: '§ 1', '§ 2a', etc.",
        "flags": "MULTILINE",
        "rationale": "Definiert Grenzen für das Splitting von Studienordnungen",
        "examples": ["§ 1", "§ 2a", "§ 15b"],
    },
    "subpoint_marker": {
        "pattern": r"(?m)^\s*\(\d+\)",
        "description": "Unterpunkt-Marker: '(1)', '(2)', etc.",
        "flags": "MULTILINE",
        "rationale": "Teilt große Paragraphen in kleinere Punkte auf",
        "examples": ["(1)", "(2)", "(15)"],
    },
    "paragraph_header_with_subpoints": {
        "pattern": r"(?m)^\s*§\s*\d+[a-zA-Z]?(?:\s*[a-z])?\b.*?(?=^\s*\(1\)|\Z)",
        "description": "Paragraph-Kopf bis zum ersten Subpoint",
        "flags": "MULTILINE",
        "rationale": "Extrahiert Paragraphen-Header zum Prefix von Subpoints",
    },
}


SEMESTER_PATTERNS = {
    "semester_marker": {
        "pattern": r"(?mi)^\s*(?:[1-9]|1[0-2])\.\s*(?:Fachsemester|Semester)(?:\s*\([^\n]*\))?\b",
        "description": "Semester-Markierungen: '1. Fachsemester', '2. Semester', etc.",
        "flags": "MULTILINE, IGNORECASE",
        "rationale": "Identifiziert Semester-Blöcke in Studienplänen",
        "threshold": 2,
        "examples": ["1. Fachsemester", "2. Semester", "3. Fachsemester (WS)"],
    },
    "semester_split_point": {
        "pattern": r"(?mi)(?=^\s*(?:[1-9]|1[0-2])\.\s*(?:Fachsemester|Semester)(?:\s*\([^\n]*\))?\b)",
        "description": "Split-Punkt vor Semester-Markierungen (Lookahead)",
        "flags": "MULTILINE, IGNORECASE",
        "rationale": "Für re.split() zur Aufteilung nach Semestern",
    },
}

MODULE_PATTERNS = {
    "module_id": {
        "pattern": r"\bMODUL ID\b",
        "description": "Modul-ID Marker in Modulhandbüchern",
        "rationale": "Definiert Anfang eines neuen Moduls",
        "flags": "WORD_BOUNDARY",
    },
    "module_id_split": {
        "pattern": r"(?=\bMODUL ID\b)",
        "description": "Split-Punkt vor MODUL ID (Lookahead)",
        "rationale": "Für re.split() zur Aufteilung nach Modulen",
    },
}

SECTION_MARKERS = {
    "markers": [
        "Zusammenfassung",
        "Lernergebnisse",
        "Inhalte",
        "Lehr- und Lernformen",
        "Arbeitsaufwand und Leistungspunkte",
        "Unterrichtssprache",
        "Teilnahmevoraussetzungen und Prüfungsformen",
        "Prüfungsform / Art der Prüfung",
        "Literatur",
        "Hinweise",
        "Anerkannte Module Verwendbarkeit",
        "Verwendbarkeit",
    ],
    "description": "Typische Abschnitte in Modulhandbuch-Einträgen",
    "rationale": "Teilt große Module in kleinere semantische Einheiten auf",
}

def get_section_markers_pattern() -> str:
    markers = SECTION_MARKERS["markers"]
    escaped = "|".join(__import__('re').escape(marker) for marker in markers)
    return r"(?m)(?=^(?:" + escaped + r")\b)"


APPENDIX_PATTERNS = {
    "appendix_marker": {
        "pattern": (
            r"(?mi)(?=^\s*(?:"
            r"Anlage\s+\d+|"
            r"Fachgebundene\s+Hochschulzugangsberechtigung|"
            r"Studienplanübersicht(?:\s*\([^\n]*\))?|"
            r"Wahlpflichtmodule|"
            r"AWE-Module/Fremdsprachen|"
            r"Modulübersicht|"
            r"Lernergebnisse\s+und\s+Kompetenzen\s+für\s+jedes\s+Modul|"
            r"Spezifika\s+des\s+Diploma\s+Supplements|"
            r"Äquivalenztabelle)\b)"
        ),
        "description": "Anhang-Markierungen in Studienordnungen",
        "flags": "MULTILINE, IGNORECASE",
        "rationale": "Definiert Grenzen für Anhang-Blöcke",
        "threshold": 2,
        "markers": [
            "Anlage X",
            "Fachgebundene Hochschulzugangsberechtigung",
            "Studienplanübersicht",
            "Wahlpflichtmodule",
            "AWE-Module/Fremdsprachen",
            "Modulübersicht",
            "Lernergebnisse und Kompetenzen für jedes Modul",
            "Spezifika des Diploma Supplements",
            "Äquivalenztabelle",
        ],
    },
}

FRONT_MATTER_PATTERNS = {
    "studienordnung": {
        "markers": [
            {
                "pattern": r"\n§\s*1\b",
                "description": "§ 1 Paragraph",
                "rationale": "Erste Paragraph ist meist der Anfang des Inhalts",
            },
            {
                "pattern": r"\n§\s*1\s+[A-ZÄÖÜa-zäöüß]",
                "description": "§ 1 gefolgt von Text",
                "rationale": "Sichere Methode um § 1 zu finden",
            },
            {
                "pattern": r"\nPräambel\b",
                "description": "Preamble-Abschnitt",
                "rationale": "Alternativ: Präambel markiert Anfang des Inhalts",
            },
        ],
        "description": "Front-Matter Marker für Studienordnungen",
    },
    "modulhandbuch": {
        "markers": [
            {
                "pattern": r"\bMODUL ID\b",
                "description": "MODUL ID Marker",
                "rationale": "Erstes Modul ist Anfang des Inhalts",
            },
            {
                "pattern": r"\bZusammenfassung\b",
                "description": "Zusammenfassung-Abschnitt",
                "rationale": "Erste Zusammenfassung könnte Anfang sein",
            },
            {
                "pattern": r"\bModulverantwortliche/r\b",
                "description": "Modulverantwortliche/r Marker",
                "rationale": "Alternative Methode um Modul-Start zu erkennen",
            },
        ],
        "description": "Front-Matter Marker für Modulhandbücher",
    },
}


def get_pattern(key: str, category: str = None) -> str:
    pass

def document_patterns() -> str:
    doc = "# Regex Patterns Dokumentation\n\n"

    doc += "## Footer Patterns\n"
    for key, info in FOOTER_PATTERNS.items():
        doc += f"- **{key}**: {info['description']}\n"
        doc += f"  Pattern: `{info['pattern']}`\n"
        doc += f"  Beispiel: `{info.get('example', 'N/A')}`\n\n"

    doc += "## Hyphenation Patterns\n"
    for key, info in HYPHENATION_PATTERNS.items():
        doc += f"- **{key}**: {info['description']}\n"
        doc += f"  Pattern: `{info['pattern']}`\n"
        doc += f"  Vorher: `{info.get('example_before', 'N/A')}`\n"
        doc += f"  Nachher: `{info.get('example_after', 'N/A')}`\n\n"

    return doc


ACTIVE_PATTERNS = {
    "footer": get_footer_patterns_list(),
    "table_lines": get_table_line_patterns_list(),
    "section_markers": SECTION_MARKERS["markers"],
}

print_pattern_summary = lambda: print(
    f"Aktive Patterns:\n"
    f"- Footer: {len(FOOTER_PATTERNS)}\n"
    f"- Table Lines: {len(TABLE_LINE_PATTERNS)}\n"
    f"- Semester: {len(SEMESTER_PATTERNS)}\n"
    f"- Module: {len(MODULE_PATTERNS)}\n"
    f"- Sections: {len(SECTION_MARKERS['markers'])}\n"
    f"- Appendix: {len(APPENDIX_PATTERNS)}\n"
)

