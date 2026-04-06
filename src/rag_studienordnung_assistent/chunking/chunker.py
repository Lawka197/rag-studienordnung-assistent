import re
from pathlib import Path
from typing import List

MAX_CHUNK_LENGTH = 1800
MAX_TABLE_CHUNK_LENGTH = 3200
TABLE_BLOCK_LINE_LIMIT = 12

FOOTER_PATTERNS = [
    r"Seite\s+\d+\s+Amtliches Mitteilungsblatt der HTW Berlin Nr\.\s*\d+/\d+",
    r"Nr\.\s*\d+/\d+\s+Amtliches Mitteilungsblatt der HTW Berlin Seite\s+\d+",
    r"Modulhandbuch der HTW Berlin\s+\d+/\d+",
]

def normalize_newlines(text: str) -> str:
    """Vereinheitlicht Zeilenumbrüche und verschiedne Sonder-Leerzeichen."""
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\xa0", " ")
    text = text.replace("\u202f", " ")
    text = text.replace("\u2007", " ")
    text = text.replace("\u2009", " ")
    return text

def remove_footers(text: str) -> str:
    """Entfernt typische Fußzeilen aus den PDFs."""
    for pattern in FOOTER_PATTERNS:
        text = re.sub(pattern, "", text)
    return text

def fix_hyphenation(text: str) -> str:
    """Setzt durch PDF-Zeilenumbruch getrennte Wörter wieder zusammen."""
    text = re.sub(r"(?<=[A-Za-zÄÖÜäöüß])\-\n(?=[A-Za-zÄÖÜäöüß])", "", text)
    text = re.sub(r"(?<=[A-Za-zÄÖÜäöüß])\s*\-\s*\n\s*(?=[A-Za-zÄÖÜäöüß])", "", text)
    return text

def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def preprocess_text(text: str) -> str:
    """Führt die grundlegende Textbereinigung durch."""
    text = normalize_newlines(text)
    text = remove_footers(text)
    text = fix_hyphenation(text)
    text = normalize_whitespace(text)
    return text

def is_table_like_line(line: str) -> bool:
    """Heuristik für tabellenartige Zeilen aus Studienverlaufs- oder Äquivalenzübersichten."""
    stripped = line.strip()
    if not stripped:
        return False

    patterns = [
        r"^[A-Z]{1,3}\d{2,}[a-zA-Z]?\b",  # z. B. B11, WP14
        r"^\d{1,2}\s+[A-ZÄÖÜa-zäöüß]",    # z. B. 13 Grundlegende Konzepte ...
        r"^[A-ZÄÖÜa-zäöüß].*\b\d+\b.*\b\d+\b",  # mehrere numerische Spalten in einer Zeile
    ]

    return any(re.search(pattern, stripped) for pattern in patterns)


def contains_table_like_structure(text: str) -> bool:
    """Erkennt grob tabellenartige Blöcke, damit diese nicht mitten im Inhalt zerschnitten werden."""
    lines = [line for line in text.split("\n") if line.strip()]
    if len(lines) < 3:
        return False

    table_like_lines = sum(1 for line in lines if is_table_like_line(line))
    return table_like_lines >= 3


def remove_front_matter(text: str, document_type: str) -> str:
    """Entfernt offensichtliches Front Matter wie Titelblätter oder Inhaltsverzeichnisse."""
    if document_type == "studienordnung":
        markers = [
            r"\n§\s*1\b",
            r"\n§\s*1\s+[A-ZÄÖÜa-zäöüß]",
            r"\nPräambel\b",
        ]
    elif document_type == "modulhandbuch":
        markers = [
            r"\bMODUL ID\b",
            r"\bZusammenfassung\b",
            r"\bModulverantwortliche/r\b",
        ]
    else:
        return text

    earliest_match = None
    for pattern in markers:
        match = re.search(pattern, text)
        if match:
            if earliest_match is None or match.start() < earliest_match:
                earliest_match = match.start()

    if earliest_match is not None:
        return text[earliest_match:].strip()

    return text


def split_studienordnung(text: str) -> List[str]:
    """
    Zerlegt Studienordnungen zunächst nach echten Paragraphenüberschriften.
    Lange Paragraphen werden danach an Unterpunkten wie (1), (2), (3) aufgeteilt.
    """
    paragraph_pattern = r"(?m)(?=^\s*§\s*\d+[a-zA-Z](?:\s*[a-z])?\b)"
    paragraph_chunks = [part.strip() for part in re.split(paragraph_pattern, text) if part.strip()]

    final_chunks: List[str] = []
    for chunk in paragraph_chunks:
        if len(chunk) <= MAX_CHUNK_LENGTH:
            final_chunks.append(chunk)
        else:
            final_chunks.extend(split_paragraph_by_subpoints(chunk))

    return final_chunks


def split_paragraph_by_subpoints(paragraph_text: str) -> List[str]:
    """
    Teilt einen Paragraphen an Unterpunkten wie (1), (2), (3) ...
    Der Paragraphenkopf bleibt beim ersten Unterpunkt erhalten.
    """
    match = re.search(r"(?m)^\s*§\s*\d+[a-zA-Z]?(?:\s*[a-z])?\b.*?(?=^\s*\(1\)|\Z)", paragraph_text)
    if match:
        paragraph_header = match.group(0).strip()
        body = paragraph_text[match.end():].strip()
    else:
        paragraph_header = ""
        body = paragraph_text.strip()

    if not re.search(r"(?m)^\s*\(\d+\)", body):
        return split_large_chunk(paragraph_text)

    subpoint_parts = [part.strip() for part in re.split(r"(?m)(?=^\s*\(\d+\))", body) if part.strip()]
    if not subpoint_parts:
        return split_large_chunk(paragraph_text)

    result: List[str] = []
    for index, subpoint in enumerate(subpoint_parts):
        if index == 0 and paragraph_header:
            combined = f"{paragraph_header}\n{subpoint}".strip()
        else:
            combined = subpoint

        if len(combined) > MAX_CHUNK_LENGTH:
            result.extend(split_large_chunk(combined))
        else:
            result.append(combined)

    return result


def split_modulhandbuch(text: str) -> List[str]:
    """
    Zerlegt das Modulhandbuch primär nach Modulblöcken und teilt große Module
    anschließend nach typischen Unterabschnitten.
    """
    module_parts = [part.strip() for part in re.split(r"(?=\bMODUL ID\b)", text) if part.strip()]

    final_chunks: List[str] = []
    for module_part in module_parts:
        if len(module_part) <= MAX_CHUNK_LENGTH:
            final_chunks.append(module_part)
        else:
            final_chunks.extend(split_module_by_sections(module_part))

    return final_chunks


def split_module_by_sections(module_text: str) -> List[str]:
    """Teilt große Modulblöcke an typischen Abschnittsüberschriften."""
    section_markers = [
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
    ]

    pattern = r"(?m)(?=^(?:" + "|".join(re.escape(marker) for marker in section_markers) + r")\b)"
    parts = [part.strip() for part in re.split(pattern, module_text) if part.strip()]

    if len(parts) <= 1:
        return split_large_chunk(module_text)

    result: List[str] = []
    current = ""

    for part in parts:
        if not current:
            current = part
            continue

        candidate = f"{current}\n\n{part}"
        if len(candidate) <= MAX_CHUNK_LENGTH:
            current = candidate
        else:
            result.append(current.strip())
            current = part

    if current.strip():
        result.append(current.strip())

    final_chunks: List[str] = []
    for part in result:
        if len(part) > MAX_CHUNK_LENGTH:
            final_chunks.extend(split_large_chunk(part))
        else:
            final_chunks.append(part)

    return final_chunks


def split_large_chunk(chunk: str, max_length: int = MAX_CHUNK_LENGTH) -> List[str]:
    """ Teilt sehr große Chunks an Absatzgrenzen, notfalls nach Länge."""
    if len(chunk) <= max_length:
        return [chunk.strip()]

    if contains_table_like_structure(chunk):
        return split_table_like_block(chunk)

    paragraphs = [part.strip() for part in chunk.split("\n\n") if part.strip()]
    if len(paragraphs) <= 1:
        return split_by_length(chunk, max_length)

    result: List[str] = []
    current = ""

    for paragraph in paragraphs:
        if not current:
            current = paragraph
            continue

        candidate = f"{current}\n\n{paragraph}"
        if len(candidate) <= max_length:
            current = candidate
        else:
            result.append(current.strip())
            current = paragraph

    if current.strip():
        result.append(current.strip())

    final_chunks: List[str] = []
    for part in result:
        if len(part) > max_length:
            if contains_table_like_structure(part):
                final_chunks.extend(split_table_like_block(part))
            else:
                final_chunks.extend(split_by_length(part, max_length))
        else:
            final_chunks.append(part)
    return final_chunks

def split_table_like_block(text: str) -> List[str]:
    """Teilt tabellenartige Blöcke in größere, aber begrenzte Teilblöcke.
    Zeilen sollen möglichst zusammenbleiben, ohne dass ein Monster-Chunk entsteht.
    """
    lines = [line.rstrip() for line in text.split("\n")]
    if not lines:
        return []

    chunks: List[str] = []
    current_lines: List[str] = []
    current_length = 0
    table_line_count = 0

    for line in lines:
        line_length = len(line) + 1
        stripped = line.strip()
        is_table_line = is_table_like_line(line)

        would_exceed_length = current_length + line_length > MAX_TABLE_CHUNK_LENGTH
        would_exceed_table_lines = is_table_line and table_line_count >= TABLE_BLOCK_LINE_LIMIT

        if current_lines and (would_exceed_length or would_exceed_table_lines):
            chunk_text = "\n".join(current_lines).strip()
            if chunk_text:
                chunks.append(chunk_text)
            current_lines = []
            current_length = 0
            table_line_count = 0

        current_lines.append(line)
        current_length += line_length

        if is_table_line:
            table_line_count += 1
        elif stripped == "":
            table_line_count = 0

    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if chunk_text:
            chunks.append(chunk_text)

    return chunks


def split_table_rows_fallback(text: str) -> List[str]:
    """Fallback für sehr lange tabellenartige Bereiche ohne klare Absatzgrenzen."""
    lines = [line.rstrip() for line in text.split("\n") if line.strip()]
    if not lines:
        return []

    chunks: List[str] = []
    current_lines: List[str] = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1
        if current_lines and current_length + line_length > MAX_TABLE_CHUNK_LENGTH:
            chunks.append("\n".join(current_lines).strip())
            current_lines = []
            current_length = 0

        current_lines.append(line)
        current_length += line_length

    if current_lines:
        chunks.append("\n".join(current_lines).strip())

    return chunks




def split_by_length(text: str, max_length: int) -> List[str]:
    """Fallback-Splitting, wenn keine besseren Grenzen vorhanden sind."""
    if contains_table_like_structure(text):
        return split_table_rows_fallback(text)
    chunks: List[str] = []
    start = 0

    while start < len(text):
        end = min(start + max_length, len(text))

        if end < len(text):
            last_break = text.rfind("\n", start, end)
            last_space = text.rfind(" ", start, end)
            split_pos = max(last_break, last_space)
            if split_pos > start + max_length // 2:
                end = split_pos

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end

    return chunks


def chunk_document(text: str, document_type: str) -> List[str]:
    """Bereitet Text vor und chunked dokumenttyp-spezifisch."""
    cleaned_text = preprocess_text(text)
    cleaned_text = remove_front_matter(cleaned_text, document_type)

    if document_type == "studienordnung":
        chunks = split_studienordnung(cleaned_text)
    elif document_type == "modulhandbuch":
        chunks = split_modulhandbuch(cleaned_text)
    else:
        raise ValueError(f"Unbekannter Dokumententyp: {document_type}")

    return [chunk for chunk in chunks if chunk.strip()]


def save_chunks_to_file(chunks: List[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, start=1):
            f.write(f"----- CHUNK {i} -----\n")
            f.write(chunk)
            f.write("\n\n")
