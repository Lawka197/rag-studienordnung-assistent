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
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap  # Überlappung berücksichtigen

    return chunks