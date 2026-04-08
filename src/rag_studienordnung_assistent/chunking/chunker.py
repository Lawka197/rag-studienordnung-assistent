"""
Hauptmodul für Text-Chunking und Preprocessing.

Dieses Modul bietet Funktionen zum Bereinigen von PDF-Text und intelligenten
Aufteilen in semantisch sinnvolle Chunks, basierend auf Dokumententyp und Struktur.
"""

import re
from pathlib import Path
from typing import List
import logging

from rag_studienordnung_assistent.chunking.strategies import (
    SemesterStrategy,
    AppendixStrategy,
)
from rag_studienordnung_assistent.chunking import patterns
from rag_studienordnung_assistent.chunking.chunking_config import ChunkingConfig, DEFAULT_CONFIG

logger = logging.getLogger(__name__)

# Default Konfiguration (kann überschrieben werden)
_DEFAULT_CONFIG = DEFAULT_CONFIG

MAX_CHUNK_LENGTH = _DEFAULT_CONFIG.max_chunk_length
MAX_TABLE_CHUNK_LENGTH = _DEFAULT_CONFIG.max_table_chunk_length
TABLE_BLOCK_LINE_LIMIT = _DEFAULT_CONFIG.table_block_line_limit


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
    """
    Entfernt typische Fußzeilen aus den PDFs.
    """
    footer_list = patterns.get_footer_patterns_list()
    for pattern in footer_list:
        text = re.sub(pattern, "", text)
    return text


def fix_hyphenation(text: str) -> str:
    """
    Setzt durch PDF-Zeilenumbruch getrennte Wörter wieder zusammen.
    """
    hyphenation_info = patterns.HYPHENATION_PATTERNS

    for key, info in hyphenation_info.items():
        text = re.sub(info["pattern"], info["replacement"], text)

    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalisiert Whitespace: mehrere Spaces/Tabs → 1 Space, 3+ Newlines → 2.
    """
    whitespace_info = patterns.WHITESPACE_PATTERNS

    for key, info in whitespace_info.items():
        text = re.sub(info["pattern"], info["replacement"], text)

    return text.strip()


def preprocess_text(text: str) -> str:
    """Führt die grundlegende Textbereinigung durch."""
    text = normalize_newlines(text)
    text = remove_footers(text)
    text = fix_hyphenation(text)
    text = normalize_whitespace(text)
    return text


def is_table_like_line(line: str) -> bool:
    """
    Heuristik für tabellenartige Zeilen aus Studienverlaufs- oder Äquivalenzübersichten.
    """
    stripped = line.strip()
    if not stripped:
        return False

    table_patterns = patterns.get_table_line_patterns_list()
    return any(re.search(pattern, stripped) for pattern in table_patterns)


def contains_table_like_structure(text: str) -> bool:
    """
    Erkennt grob tabellenartige Blöcke.

    Braucht mindestens 3 Zeilen die wie Tabellenzeilen aussehen.
    """
    lines = [line for line in text.split("\n") if line.strip()]
    if len(lines) < 3:
        return False

    table_like_lines = sum(1 for line in lines if is_table_like_line(line))
    return table_like_lines >= 3


def contains_semester_markers(text: str) -> bool:
    """
    Erkennt, ob ein Block typische Semesterüberschriften enthält (mindestens 2).
    """
    semester_pattern = patterns.SEMESTER_PATTERNS["semester_marker"]["pattern"]
    threshold = patterns.SEMESTER_PATTERNS["semester_marker"]["threshold"]

    matches = re.findall(semester_pattern, text)
    return len(matches) >= threshold


def remove_front_matter(text: str, document_type: str) -> str:
    """
    Entfernt offensichtliches Front Matter wie Titelblätter oder Inhaltsverzeichnisse.
    """
    if document_type not in patterns.FRONT_MATTER_PATTERNS:
        return text

    markers_info = patterns.FRONT_MATTER_PATTERNS[document_type]["markers"]

    earliest_match = None
    for marker in markers_info:
        pattern = marker["pattern"]
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
    paragraph_pattern = patterns.PARAGRAPH_PATTERNS["paragraph_header"]["pattern"]
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
    paragraph_header_pattern = patterns.PARAGRAPH_PATTERNS["paragraph_header_with_subpoints"]["pattern"]

    match = re.search(paragraph_header_pattern, paragraph_text)
    if match:
        paragraph_header = match.group(0).strip()
        body = paragraph_text[match.end():].strip()
    else:
        paragraph_header = ""
        body = paragraph_text.strip()

    subpoint_pattern = patterns.PARAGRAPH_PATTERNS["subpoint_marker"]["pattern"]

    if not re.search(subpoint_pattern, body):
        return split_large_chunk(paragraph_text)

    subpoint_parts = [part.strip() for part in re.split(r"(?m)(?=^\s*\(\d+\))", body) if part.strip()]
    if not subpoint_parts:
        return split_large_chunk(paragraph_text)

    result: List[str] = []
    for subpoint in subpoint_parts:
        if paragraph_header:
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
    module_pattern = patterns.MODULE_PATTERNS["module_id_split"]["pattern"]
    module_parts = [part.strip() for part in re.split(module_pattern, text) if part.strip()]

    final_chunks: List[str] = []
    for module_part in module_parts:
        if len(module_part) <= MAX_CHUNK_LENGTH:
            final_chunks.append(module_part)
        else:
            final_chunks.extend(split_module_by_sections(module_part))

    return final_chunks


def split_module_by_sections(module_text: str) -> List[str]:
    """
    Teilt große Modulblöcke an typischen Abschnittsüberschriften.
    """
    section_pattern = patterns.get_section_markers_pattern()
    parts = [part.strip() for part in re.split(section_pattern, module_text) if part.strip()]

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
    """
    Teilt sehr große Chunks intelligent auf.
    """
    if len(chunk) <= max_length:
        return [chunk.strip()]

    if contains_semester_markers(chunk):
        semester_strategy = SemesterStrategy()
        result = semester_strategy.split(chunk)
        if result:
            logger.debug(f"SemesterStrategy: {len(result)} chunks")
            return result

    appendix_strategy = AppendixStrategy()
    if appendix_strategy.can_apply(chunk):
        result = appendix_strategy.split(chunk)
        if result:
            logger.debug(f"AppendixStrategy: {len(result)} chunks")
            return result

    if contains_table_like_structure(chunk):
        logger.debug("TableStrategy applied")
        return split_table_like_block(chunk)

    return _split_by_paragraphs_and_length(chunk, max_length)


def _split_by_paragraphs_and_length(chunk: str, max_length: int) -> List[str]:
    """
    Fallback-Strategie: Teilt nach Absätzen und dann nach Länge.
    """
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
            final_chunks.extend(split_large_chunk(part, max_length))
        else:
            final_chunks.append(part)

    return final_chunks


def split_table_like_block(text: str) -> List[str]:
    """
    Teilt tabellenartige Blöcke in größere, aber begrenzte Teilblöcke.
    Zeilen sollen möglichst zusammenbleiben, ohne dass ein Monster-Chunk entsteht.
    """
    if contains_semester_markers(text):
        semester_strategy = SemesterStrategy()
        result = semester_strategy.split(text)
        if result:
            return result

    appendix_strategy = AppendixStrategy()
    if appendix_strategy.can_apply(text):
        result = appendix_strategy.split(text)
        if result:
            return result

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
    """
    Fallback-Splitting, wenn keine besseren Grenzen vorhanden sind.

    Versucht zuerst Semester/Anhang/Tabellen-Strategien, dann Split nach reiner Länge.
    """
    if contains_semester_markers(text):
        semester_strategy = SemesterStrategy()
        result = semester_strategy.split(text)
        if result:
            return result

    appendix_strategy = AppendixStrategy()
    if appendix_strategy.can_apply(text):
        result = appendix_strategy.split(text)
        if result:
            return result

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


def chunk_document(text: str, document_type: str, config: ChunkingConfig = None) -> List[str]:
    """
    Hauptfunktion: Bereitet Text vor und chunked dokumenttyp-spezifisch.

    """
    if config is None:
        config = DEFAULT_CONFIG

    global MAX_CHUNK_LENGTH, MAX_TABLE_CHUNK_LENGTH, TABLE_BLOCK_LINE_LIMIT
    MAX_CHUNK_LENGTH = config.max_chunk_length
    MAX_TABLE_CHUNK_LENGTH = config.max_table_chunk_length
    TABLE_BLOCK_LINE_LIMIT = config.table_block_line_limit

    if config.verbose:
        logger.info(f"Chunking mit config: max_chunk={config.max_chunk_length}, type={document_type}")

    cleaned_text = preprocess_text(text)

    if config.remove_front_matter:
        cleaned_text = remove_front_matter(cleaned_text, document_type)

    if document_type == "studienordnung":
        chunks = split_studienordnung(cleaned_text)
    elif document_type == "modulhandbuch":
        chunks = split_modulhandbuch(cleaned_text)
    else:
        raise ValueError(f"Unbekannter Dokumententyp: {document_type}")

    result = [chunk for chunk in chunks if chunk.strip()]

    if config.verbose:
        logger.info(f"Erstellt {len(result)} Chunks")

    return result

def save_chunks_to_file(chunks: List[str], output_path: Path) -> None:
    """Speichert Chunks in eine Datei mit Markierungen."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, start=1):
            f.write(f"----- CHUNK {i} -----\n")
            f.write(chunk)
            f.write("\n\n")

