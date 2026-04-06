from pathlib import Path
from rag_studienordnung_assistent.ingestion.pdf_loader import (extract_text_from_pdf, save_extracted_text)
from rag_studienordnung_assistent.chunking.chunker import chunk_document, save_chunks_to_file
from rag_studienordnung_assistent.chunking.chunking_config import get_config

DOCUMENTS = [
    {"filename": "alte_studienordnung.pdf", "type": "studienordnung"},
    {"filename": "neue_studienordnung.pdf", "type": "studienordnung"},
    {"filename": "stgModulHandbuch.pdf", "type": "modulhandbuch"},
]

def print_chunk_examples(chunks: list[str], pdf_file: str) -> None:
    if not chunks:
        print(f"Keine Chunks für {pdf_file} erstellt.")
        return

    example_indices = sorted({0, len(chunks) // 2, len(chunks) - 1})
    print(f"Anzahl der Chunks für {pdf_file}: {len(chunks)}")
    for index in example_indices:
        print(f"\nBeispiel-Chunk {index + 1}/{len(chunks)} für {pdf_file}:")
        print(chunks[index][:1000])

def main() -> None:
    project_root = Path(__file__).resolve().parents[2]

    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    chunk_dir = processed_dir / "chunks"

    config = get_config("default")
    print(f"Verwende Konfiguration: max_chunk_length={config.max_chunk_length}, max_table_chunk={config.max_table_chunk_length}")

    for document in DOCUMENTS:
        pdf_file = document["filename"]
        document_type = document["type"]

        pdf_path = raw_dir / pdf_file
        text_output_path = processed_dir / f"{Path(pdf_file).stem}.txt"
        chunk_output_path = chunk_dir / f"{Path(pdf_file).stem}_chunks.txt"

        print(f"\nLese PDF: {pdf_path}")
        extracted_text = extract_text_from_pdf(pdf_path)

        print("Speichere extrahierten Text...")
        save_extracted_text(extracted_text, text_output_path)
        print(f"Text erfolgreich gespeichert unter: {text_output_path}")

        chunks = chunk_document(extracted_text, document_type, config)
        save_chunks_to_file(chunks, chunk_output_path)
        print(f"Chunks erfolgreich gespeichert unter: {chunk_output_path}")
        print_chunk_examples(chunks, pdf_file)

if __name__ == "__main__":
    main()

