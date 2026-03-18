from pathlib import Path
from rag_studienordnung_assistent.ingestion.pdf_loader import (extract_text_from_pdf, save_extracted_text)

def main():
    project_root = Path(__file__).resolve().parents[2]

    pdf_files = [
        "alte_studienordnung.pdf",
        "neue_studienordnung.pdf",
        "stgModulHandbuch.pdf",
    ]

    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"

    for pdf_file in pdf_files:
        pdf_path = raw_dir / pdf_file
        output_path = processed_dir / f"{Path(pdf_file).stem}.txt"

        print(f"Lese PDF: {pdf_path}")
        extracted_text = extract_text_from_pdf(pdf_path)

        print("Speichere extrahierten Text...")
        save_extracted_text(extracted_text, output_path)
        print(f"Text erfolgreich gespeichert unter: {output_path}")

if __name__ == "__main__":
    main()