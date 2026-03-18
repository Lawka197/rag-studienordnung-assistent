from pathlib import Path
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"Die Datei {pdf_path} wurde nicht gefunden.")

    reader = PdfReader(str(pdf_path))
    pages_text = ""

    for page_number, page in enumerate(reader.pages, start=1):
        pages_text += page.extract_text() + "\n"

    return pages_text

def save_extracted_text(text: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(text)


