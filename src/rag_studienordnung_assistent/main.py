from pathlib import Path
from rag_studienordnung_assistent.ingestion.pdf_loader import (extract_text_from_pdf, save_extracted_text)

def main():
    project_root = Path(__file__).resolve().parents[2]
    pdf_path = project_root /"data" /"raw" /"alte_studienordnung.pdf"
    output_path = project_root /"data" /"processed" /"alte_studienordnung.txt"

    print(f"Lese PDF: {pdf_path}")
    extracted_text = extract_text_from_pdf(pdf_path)

    print("Speichere extrahierten Text...")
    save_extracted_text(extracted_text, output_path)
    print(f"Text erfolgreich gespeichert unter: {output_path}")

if __name__ == "__main__":
    main()