from pathlib import Path
from rag_studienordnung_assistent.ingestion.pdf_loader import (extract_text_from_pdf, save_extracted_text)
from rag_studienordnung_assistent.chunking.chunker import chunk_text, save_chunks_to_file

pdf_files = [
        "alte_studienordnung.pdf",
        "neue_studienordnung.pdf",
        "stgModulHandbuch.pdf",
    ]

def print_chunk_examples(chunks: list[str], pdf_file:str) -> None:
    if not chunks:
        print(f"Keine Chunks für {pdf_file} erstellt.")
        return

    example_indices = sorted({0, len(chunks) // 2, len(chunks) - 1})
    print(f"Anzahl der Chunks für {pdf_file}: {len(chunks)}")
    for index in example_indices:
        print(f"\nBeispiel-Chunk {index + 1}/{len(chunks)} für {pdf_file}:")
        print(chunks[index][:700])

def main():
    project_root = Path(__file__).resolve().parents[2]

    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    chunks_dir = processed_dir / "data" / "chunks"

    for pdf_file in pdf_files:
        pdf_path = raw_dir / pdf_file
        output_path = processed_dir / f"{Path(pdf_file).stem}.txt"
        chunk_output_path = chunks_dir / f"{Path(pdf_file).stem}.txt"

        print(f"\nLese PDF: {pdf_path}")
        extracted_text = extract_text_from_pdf(pdf_path)

        print("Speichere extrahierten Text...")
        save_extracted_text(extracted_text, output_path)
        print(f"Text erfolgreich gespeichert unter: {output_path}")

        chunks = chunk_text(extracted_text)
        save_chunks_to_file(chunks, chunk_output_path)
        print(f"Chunks erfolgreich gespeichert unter: {pdf_file}: {chunk_output_path}")
        print_chunk_examples(chunks, pdf_file)

if __name__ == "__main__":
    main()