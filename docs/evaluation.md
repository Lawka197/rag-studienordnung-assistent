# Evaluation der Ausgabe vom RAG

### Testfall 1: Modul 
**Frage:**
Was ist ein Modul?

**Erwartung:**
- Definition aus der Studienordnung
- ggf. Bezug auf Modulstruktur, ECTS, Prüfungen
- 
**RAG-Antwort:**
"Ein Modul bezeichnet einen Teilbereich innerhalb des Studiums, der bestimmte Themen 
oder Inhalte abdeckt und in eine spezielle Fachrichtung eingebettet ist. Es besteht 
aus Lehrveranstaltungen mit praktischen Lerninhalten sowie theoretischem Wissen, um 
zielgruppengerechte Kompetenzen und Fähigkeiten zu erlangen. Der Erwerb eines Moduls 
wird meist durch eine Modulprüfung nachgewiesen."

**Bewertung:**
Korrektheit: 4 (Die Antwort ist größtenteils korrekt, enthält aber einige Ungenauigkeiten und könnte präziser sein.)
Vollständigkeit: 3 (Die Antwort deckt die grundlegende Definition ab)
Relevanz: 4 (Die Antwort ist relevant, da sie die Frage beantwortet, aber sie könnte spezifischer auf die Studienordnung eingehen.)

**Problem:**
- Die Antwort ist inhaltlich plausibel, basiert jedoch nicht eindeutig auf den bereitgestellten Dokumenten
- Die gefundenen Chunks enthalten keine explizite Definition eines Moduls 
- Das LLM greift vermutlich auf Allgemeinwissen zurück, statt auf den Kontext

**Mögliche Ursache:**
- Definition eines Moduls wurde nicht korrekt gechunkt
- Retriever findet nur Randinformationen
- Embeddings erkennen "Definition" nicht ausreichend

**Verbesserungsideen:**
- Prompt anpassen 
---
### Testfall 2: Anzahl der Fachsemester

**Frage:**  
Wie viele Fachsemester gibt es?

**Erwartung:**  
- Nennung der Regelstudienzeit bzw. Anzahl der Fachsemester  
- idealerweise aus Studienplan oder allgemeinem Teil der Studienordnung  
- ggf. Unterscheidung zwischen alter und neuer Studienordnung, falls relevant  

**RAG-Antwort:**  
"Die angegebenen Dokumente enthalten keine Information über die Anzahl der Fachsemester."

**Bewertung:** 
- Korrektheit: 1 (Die Antwort ist unbrauchbar, da die Informationen zur Anzahl der Fachsemester tatsächlich im Text vorhanden sein sollten und erkannt werden sollten.)
- Vollständigkeit: 1 (Die Antwort enthält keine der erwarteten Informationen.)
- Relevanz: 1 (Die Antwort ist nicht relevant, da sie die gestellte Frage nicht beantwortet.)

**Probleme:**  
- Es wurden keine passenden Chunks zur Frage gefunden  
- Retrieval liefert irrelevante Paragraphen zum Fachpraktikum und Geltungsbereich  
- Die Antwort ist nur bezogen auf den gelieferten Kontext korrekt, beantwortet aber die Nutzerfrage nicht  

**Mögliche Ursache:**  
- Informationen zur Anzahl der Fachsemester liegen möglicherweise in einer Tabelle oder im Studienplan, die schlecht gechunkt wurde  
- Der Retriever erkennt den Zusammenhang zwischen „Fachsemester“ und Studienstruktur nicht zuverlässig  
- Tabelleninhalte oder Überschriften werden nicht gut in Embeddings abgebildet  

**Verbesserungsideen:**  
- Studienplan-Tabellen separat und strukturiert chunken  
- Überschriften wie „Regelstudienzeit“, „Fachsemester“ oder „Studienplan“ im Chunk mitführen  
- Metadaten für Semesterangaben ergänzen  
- Query-Formulierungen testen, z.B. „Regelstudienzeit“, „Anzahl Semester“, „Studienplan Fachsemester“

---
### Testfall 3: Ziele des Studiums 

**Frage:**  
Welche Ziele hat das Studium?

**Erwartung:**  
- Inhalte aus §5 "Ziele des Studiums"
- Auflistung der drei bzw. 4 Unterpunkte je nach Studienordnung
- ggf. Unterscheidung alte vs. neue Studienordnung

**RAG-Antwort:**  
"Der gegebene Text enthält keine direkten Informationen über die Ziele des Studiums."

**Bewertung:**
Korrektheit: 1 (Die Antwort ist unbrauchbar, da die Informationen zu den Zielen des Studiums tatsächlich im Text vorhanden sind und erkannt werden sollten.)
Vollständigkeit: 1 (Die Antwort enthält keine der erwarteten Informationen.)
Relevanz: 1 (Die Antwort ist nicht relevant, da sie die gestellte Frage nicht beantwortet.)

**Probleme:**
- es wurde kein relevanter Chunk zu §5 gefunden
- das Retrieval liefert irrelevante Paragraphen ( §2 Studienpaln)
- die Scores sind sehr ähnlich, was zur schlechten Differenzierung führt

**Mögliche Ursache:**
- die Chunks enthalten keine Paragraphenüberschrift ("Ziele des Stuiums")
- die semantische Suche erkennt Begriffe wie "Ziele" nicht ausreichend
- das Chunking trennt §5 ungünstig auf
- das Embedding-Modell ist nicht optimal für solche Texte

**Verbesserungsideen:**
- Paragraphenüberschrift immer in den Chunk aufnehmen
- Metadaten hinzufügen
- besseres Embedding-Modell oder feintuning

---
**Erkennis:**
- Retrieval ist aktuell der größte Schwachpunkt
- Tabellen und strukturierte Inhalte werden schlecht gefunden
- Fehlende Paragraphenüberschriften im Chunk verschlechtern die Suche
- Das LLM verhält sich teils diszipliniert, teils beantwortet es Fragen mit Allgemeinwissen statt mit Kontext