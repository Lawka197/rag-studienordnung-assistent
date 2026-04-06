import re
from pathlib import Path
from typing import List


MAX_CHUNK_LENGTH = 1800

def normalize_whitespace(text: str) -> str:
    """Vereinheitlicht überflüssige Leerzeichen und Zeilenumbrüche."""
    text = text.replace("\r\n", "\n")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def remove_front_matter(text: str, document_type: str) -> str:
    """Entfernt offensichtliches Front Matter wie Titelblätter oder Inhaltsverzeichnisse."""
    if document_type == "studienordnung":
        markers = ["§ 1","§1","Präambel"]
    elif document_type == "modulhandbuch":
        markers = ["MODUL ID", "Modulverantwortliche/r", "Zusammenfassung"]
    else:
        return text

    positions = [text.find(marker) for marker in markers if text.find(marker) != -1]
    if positions:
        return text[min(positions):].strip()
    return text

def split_studienordnung(text: str) -> List[str]:
    """Teilt die Studienordnung in Abschnitte basierend auf den Paragraphen (§) auf."""
    sections = re.split(r"(?=\n?§\s*\d+[a-zA-Z]?)", text)
    return [section.strip() for section in sections if section.strip()]

def split_modulhandbuch(text: str) -> List[str]:
    """Teilt das Modulhandbuch in Abschnitte basierend auf den Modul-IDs auf."""
    sections = re.split(r"(?=\bMODUL ID\b)", text)
    return [section.strip() for section in sections if section.strip()]

def split_large_chunk(chunk: str, max_length: int = MAX_CHUNK_LENGTH) -> List[str]:
    """ Teilt zu große Chunks weiter auf. Zuerst an Absatzgrenzen, notfalls fest nach Länge."""
    if len(chunk) <= max_length:
        return [chunk.strip()]

    paragraphs = [section.strip() for section in chunk.split("\n\n") if section.strip()]
    if len(paragraphs) <= 1:
        return _split_by_length(chunk, max_length)

    result = []
    current_chunk = ""

    for paragraph in paragraphs:
        if not current_chunk:
            current_chunk = paragraph
            continue

        candidate = f"{current_chunk}\n\n{paragraph}"
        if len(candidate) <= max_length:
            current_chunk = candidate
        else:
            result.append(current_chunk.strip())
            current_chunk = paragraph

        if current_chunk.strip():
            result.append(current_chunk.strip())

        final_chunks = []
        for section in result:
            if len(section) > max_length:
                final_chunks.extend(_split_by_length(section, max_length))
            else:
                final_chunks.append(section)
        return final_chunks

def _split_by_length(text: str, max_length: int) -> List[str]:
    """Teilt den Text strikt nach max_length, ohne Rücksicht auf Absätze."""
    return [text[i:i+max_length].strip() for i in range(0, len(text), max_length) if text[i:i+max_length].strip()]

def chunk_document(text: str, document_type: str) -> List[str]:
    """ Führt leichtes Preprocessing durch und teilt das Dokument in Chunks auf."""

    cleaned_text = normalize_whitespace(text)
    cleaned_text = remove_front_matter(cleaned_text, document_type)

    if document_type == "studienordnung":
        base_chunks = split_studienordnung(cleaned_text)
    elif document_type == "modulhandbuch":
        base_chunks = split_modulhandbuch(cleaned_text)
    else:
        raise ValueError(f"Unbekannter Dokumententyp: {document_type}")

    final_chunks = []
    for chunk in base_chunks:
        final_chunks.extend(split_large_chunk(chunk))

    return [chunk for chunk in final_chunks if chunk.strip()]


def save_chunks_to_file(chunks: List[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, start=1):
            f.write(f"----- CHUNK {i} -----\n")
            f.write(chunk)
            f.write("\n\n")