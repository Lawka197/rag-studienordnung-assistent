from pathlib import Path
from typing import List


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 150) -> List[str]:
    """
    Teilt den Text in überlappende Abschnitte (Chunks) auf.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap  # Überlappung berücksichtigen

    return chunks

def save_chunks_to_file(chunks: List[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, start=1):
            f.write(f"---Chunk {i} ---\n")
            f.write(chunk)
            f.write("\n\n")