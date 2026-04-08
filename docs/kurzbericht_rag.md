# Kurzbericht: RAG-Modell für Studienordnungen

---
## 1. Thema & Datenbeschreibung

### 1.1 Projektziel
Ziel dieses Projekts ist die Entwicklung eines Retrieval-Augmented Generation (RAG) Modells, das in der Lage ist, Fragen zu Studienordnungen zu beantworten.
Das Modell soll relevante Informationen aus den Dokumenten extrahieren und diese nutzen, um präzise Antworten zu generieren.

### 1.2 Anwendungsfall

Da es Studierende gibt die in Teilzeit studieren und nochnach der alten Studienordnung studieren, 
gibt es immer wieder Fragen zu den Unterschieden zwischen den beiden Studienordnungen.
Das RAG-Modell soll hier helfen, indem es die relevanten Informationen aus beiden Studienordnungen extrahiert 
und die Unterschiede klar darstellt. Auch einige Module wurden umbenannt und das Modell soll helfen das Äquivalent
zu finden oder auch Unterschiede zum Praktikum erklären. 

### 1.3 Datengrundlage

- Anzahl der Dokumente: 3 (alte Studienordnung, neue Studienordnung, Modulhandbuch)
- Dokumententypen: PDF
- Umfang (Seitenzahl):  40 Seiten alte Studienordnung, 112 Seiten Modulhandbuch , 60 Seiten neue Studienordnung
- Besonderheiten: Tabellen, Sonderzeichen wie Formeln und Paragraphen, Titelblätter, Inhaltsverzeichnisse, Fußnoten, lange Absätze mit Unterpunkten, Bulletpoints, versteckte Leerzeichen

### 1.4 Herausforderungen der Daten

- viele unterschiedliche Tabellen 
- viele Sonderzeichen, die von der OCR nicht immer korrekt erkannt werden
- Bulletpoints teilweise erkannt und sonst wurden Icons anstatt Bulletpoints verwendet
- lange Paragraphen mit Unterpunkten
- versteckte Leerzeichen  

---
## 2. Systemarchitektur

### 2.1 Überblick

Das System basiert auf einem klassischen RAG-Ansatz:

**Pipeline:**
1. Datenextraktion aus PDFs  
2. Chunking der Texte  
3. Erstellung von Embeddings  
4. Speicherung in einer Vektordatenbank  
5. Retrieval relevanter Chunks  
6. Antwortgenerierung durch ein LLM  

### 2.2 Datenverarbeitung 

**Punkt 1: Textextraktion**
 
- Ich nutzte PyPDF für die Textextraktion (in ingestion/pdf_loader.py)
- mögliche Fehler: OCR-Fehler, Sprachzeichen könnten nicht korrekt erkannt werden

**Punkt 2: Preprocessing**

- ich habe Zeilenumbrüche normalisiert
- Fußzeilen entfernt
- Wort-Trennungen durch Zeilenumbruch (Hyphenation) gefixt
- Whitespace notmalisiert (mehrere Spaces -> 1 Space)

**Punkt 3: Chunking-Strategie**

Ich nutzte dokumenttyp-spezifisches Chunking:
- Für die Studienordnung: Split nach Paragraphen, dann nach Unterpunkten
- Für das Modulhandbuch: Split nach Modulblöcken, dann nach Sektionen
- Maximale Chunk-Länge: wird aus chunking_config.py gelesen
- Besonderheit: Tabellenerkennung und spezielle Behandlung von Tabellen

**Punkt 4: Metadaten**

Jeder Chunk erhält Metadaten mit Informationen wie source und chunk_id

### 2.3 Retrieval 

- Verwendete Vektordatenbank: FAISS
- FAISS-Version: IndexFlatIP (Inner Product / Kosinus-Ähnlichkeit nach Normalisierung)
- Embedding-Dimension: 384 (Modell: "all-MiniLM-L6-v2" am Anfang genutz, dann auf "paraphrase-mpnet-base-v2" gewechselt -> 768 Dimensionen und bessere Ergebnisse) 
- Ähnlichkeitsmaß: IndexFlatIP mit vorher normalisierten Embeddings = Kosinus-Ähnlichkeit
- Rückgabewert ist float zwischen 0 und 1
- Anzahl der zurückgegebenen Chunks (Top-k): 5 

Zusätzlich habe ich die Similarity-Scores der Retrieval-Ergebnisse zur Analyse in der Konsole ausgegeben,
um zu überprüfen, wie gut die gefundenen Chunks zur Anfrage passen.
Hohe Scores (nahe 1) deuten auf hohe semantische Ähnlichkeit hin.


### 2.4 LLM-Integration

- Verwendetes LLM: Ollama mit neural-chat Modell
- Prompt-Design: Kontextinformationen + Frage am Anfang, jetzt auf System-Prompt aus prompts.py gewechselt
- Besonderheiten: temperatur von 0.7 auf 0.2 gewechselt --> 0.2 = konservativ, weniger kreativ (besser für faktische Fragen)
- Query + Top-k Chunks werden kombiniert zu einem Prompt
Format: "Kontext: {chunks}\n\nFrage: {frage}\n\nAntwort:"

---
## 3. Evaluation

### 3.1 Evaluationsmethoden

- Manuelle Überprüfung der Antworten durch Expertin (Hauptmethode)
Bewertung auf 5-Punkt Skala für: Korrektheit, Vollständigkeit, Relevanz

Bemerkungen: Automatische Metriken wie Precision@k, Recall@k sind nicht implementiert. 
Diese würden zusätzliche Ground Truth Labels und mehr Aufwand erfordern. Cosine Similarity wird intern 
durch FAISS berechnet, aber nicht systematisch ausgewertet. 

### Metriken
ROUGE-L und Cosine Similarity implementiert allerdings aus Zeitgründen nicht ausgewertet. Dienen mir als
Grundlage für zukünftige systematische Evaluation.

### 3.2 Testfragen
- Frage 1: Was ist ein Modul?
- Frage 2: Wie viele Fachsemester gibt es?
- Frage 3: Welche Ziele hat das Studium?

| Frage | Erwartete Antwort | Modellantwort       | Bewertung |
|-------|------------------|---------------------|-----------|
| 1     |         Bezug auf Modulstruktur, ECTS, Prüfungen         | siehe evaluation.md | 3.67/5    |
| 2     |       Nennung der Regelstudienzeit bzw. Anzahl der Fachsemester           | siehe evaluation.md | 1/5       |
| 3     |          Inhalte aus §5 "Ziele des Studiums"        | siehe evaluation.md | 1/5       |

### 3.4 Analyse
Die Ergebnisse zeigen, dass einfache Definitionsfragen (Frage 1) teilweise korrekt beantwortet werden konnten,
während komplexere oder strukturabhängige Fragen (Frage 2 und 3) deutlich schlechter abschnitten.

Meine Schlussfolgerung daraus, dass das Retrieval relevante Informationen nicht zuverlässig liefert,
insbesondere wenn diese in Tabellen oder komplexen Strukturen enthalten sind.
---
## 4. Reflexion

### 4.1 Erkennisse
Im Verlauf des Projekts wurde mir deutlich klar, dass die Qualität eines RAG-Systems stark von der Qualität 
der Datenaufbereitung abhängt, insbesondere vom Chunking. 
Ich habe am Anfang viel zu viel Zeit in die Strukturierung von Fließtext ( Paragraphen, Zeilenumbrüche, Sonderzeichen)
investiert und somit zentrale Informationen in Tabellen nicht ausreichend berücksichtigt. 

Eine weitere Erkenntnis ist, dass die Qualität der generierten Antworten weniger vom LLM selbst abhängt, sondern 
eher stark vom Retrieval-Prozess. Selbst ein leistungsstarkes Sprchmodell kann keine guten Antworten liefern, 
wenn die relevanten Informationen nicht im Kontext enthalten sind. 

Außerdem habe ich festgestellt, dass die Wahl des Embedding-Modells einen erheblichen Einfluss auf die Retrieval-Qualität
hat. Durch den Wechsel von "all-MiniLM-L6-v2" zu "paraphrase-mpnet-base-v2" habe ich spürbare bessere Ergebnisse erzeilt. 

Ebenso der Wechsel der Temperatur des LLM als auch das Prompt-Design haben einen Einfluss auf die Antwort-Qualität, gerade bei 
faktischen Fragestellungen. 

### 4.2 Probleme 
Eines meiner größten Probleme war das Chunking für Tabellen, da viele wichtige Informationen 
in den Tabellen stecken, aber die Textextraktion und das Chunking sich hauptsächlich auf die 
Textstruktur konzentriert haben. Dadurch wurden viele relevante Informationen nicht optimal erfasst, 
was sich negativ auf die Qualität der Antworten ausgewirkt hat. 

Auch die OCR-Fehler und die Erkennung von Sonderzeichen haben zu ungenauen Chunks geführt, was 
wiederum die Retrieval-Qualität beeinträchtigt hat.

Ich habe auch zu wenig Zeit in die Evaluation investiert, da ich mich zu sehr auf die Implementierung 
konzentriert habe. Eine systematischere und automatisierte Evaluation hätte mir schnelleres Feedback 
gegeben und ermöglicht, die Schwachstellen des Modells schneller zu identifizieren und zu beheben.

Zu spät erkannt, dass ich zu schwache Modelle für die Embeddings verwendet habe, was zu schlechten 
Retrieval-Ergebnissen geführt hat.

### 4.3 Verbesserungspotential
Als erstes das Tabellen-Chunking otimieren, wenn das qualitativ besser wird, dann werden auch bessere Antworten generiert.
Dann die Paragraphen-Überschriften zu jedem Chunk bewahren, damit die Retrieval-Qualität besser wird. 
Man könnte auch die Metadaten erweitern. 
Ein besseres Embedding-Modell verwenden, um die semantische Suche zu verbessern.
Automatische Metriken wie Precision@k, Recall@k implementieren, um die Evaluation zu systematisieren und schnelleres Feedback zu erhalten.

---
## 5. Fazit 
Noch sehr viele Baustellen offen, aber es ist ein guter Anfang. Das RAG-Modell zeigt Potenzial, 
aber die Qualität der Antworten hängt stark von der Qualität der Chunks ab. Definitiv mehr Zeit 
für die Datenvorbereitung und das Chunking investieren, könnte die Ergebnisse deutlich verbessern und 
auch bessere Modelle verwenden. Auch die Evaluation könnte systematischer und automatisierter erfolgen, 
um schneller Feedback zu erhalten. Beim Chunking habe ich mich zu sehr auf die Textstruktur konzentriert 
und weniger auf die Tabellen, was sich als Fehler herausgestellt hat, da viele wichtige Informationen in 
den Tabellen stecken. Insgesamt ist es ein guter Start, aber es gibt noch viel Raum für Verbesserungen.

### 6. Nutzung von KI
- Für die Struktur von Evaluation, um das gut zu dokumentieren
- für pattern Auslagerung, da mein Code schnell zu verschachtelt wurde und in mehreren Methoden Duplikate enstanden sind
- für die Ausgabe beim RAG bei der Demo: Balken, Seperation etc. damit das übersichtlicher angezeigt wird
- teilweise für verständliche commit-Nachrichten 