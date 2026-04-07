from pathlib import Path
import logging
from rag_studienordnung_assistent.rag_system import RAGSystem
from rag_studienordnung_assistent.chunking.chunking_config import get_config

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_separator(title: str = ""):
    """Separatoren"""
    if title:
        print(f"\n{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'─'*80}\n")


def main():
    print_separator("RAG-SYSTEM DEMO (FAISS + LLM)")
    print("Initialisiere RAG-System...")
    print("Vector Store: FAISS")
    print("LLM: Ollama neural-chat")

    config = get_config("default")
    try:
        rag = RAGSystem(chunking_config=config, llm_type="ollama")
        print("RAG-System erfolgreich initialisiert\n")
    except Exception as e:
        print(f"Fehler: {e}")
        print("Nutze nur Retrieved Chunks ohne LLM\n")
        return

    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    vector_store_path = project_root / "data" / "vector_store"

    documents = [
        ("alte_studienordnung.pdf", "Alte Studienordnung"),
        ("neue_studienordnung.pdf", "Neue Studienordnung"),
        ("stgModulHandbuch.pdf", "Modulhandbuch"),
    ]

    print("Lade Dokumente...")
    loaded_count = 0
    for pdf_file, doc_name in documents:
        pdf_path = raw_dir / pdf_file

        if not pdf_path.exists():
            print(f"{pdf_file} nicht gefunden - überspringe")
            continue

        try:
            print(f"{doc_name}...")
            rag.load_document(pdf_path, doc_name)
            print(f"{doc_name} geladen")
            loaded_count += 1
        except Exception as e:
            print(f"Fehler: {e}")

    if loaded_count == 0:
        print("Keine Dokumente geladen!")
        return

    # Speicher Vector Store
    print(f"\nSpeichere FAISS Vector Store zu {vector_store_path}...")
    try:
        rag.save_vector_store(str(vector_store_path))
        print("Vector Store gespeichert (kann später geladen werden!)")
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

    print_separator("BEISPIEL-FRAGEN (mit LLM-Antworten)")

    questions = [
        "Was ist ein Modul?",
        "Wie viele Fachsemester gibt es?",
        "Welche Ziele hat das Studium?",
    ]

    for i, question in enumerate(questions, 1):
        print_separator(f"FRAGE {i}: {question}")

        try:
            result = rag.answer_question(question, top_k=3, use_llm=True)

            print("RELEVANTE DOKUMENTE:")
            print(result["context"])

            if "llm_answer" in result:
                print_separator("LLM-ANTWORT")
                print(result["llm_answer"])
            else:
                print("Keine LLM-Antwort verfügbar")

        except Exception as e:
            print(f"Fehler: {e}")

    print_separator("INTERAKTIVER MODUS (Beende mit 'exit')")

    while True:
        try:
            user_question = input("Stelle mir eine Frage zum FIW-Studium: ").strip()

            if user_question.lower() in ["exit", "quit", "q"]:
                print("Tschüss! Bis zum nächsten Mal!")
                break

            if not user_question:
                continue

            print("\nSuche relevante Dokumente...")
            result = rag.answer_question(user_question, top_k=3, use_llm=True)

            print_separator("RELEVANTE DOKUMENTE")
            print(result["context"])

            if "llm_answer" in result:
                print_separator("ANTWORT")
                print(result["llm_answer"])

        except KeyboardInterrupt:
            print("\nTschüss!")
            break
        except Exception as e:
            print(f"Fehler: {e}")


if __name__ == "__main__":
    main()

