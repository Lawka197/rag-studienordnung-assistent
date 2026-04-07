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

### 2.3 Retrieval 

- Verwendete Vektordatenbank: FAISS
- Ähnlichkeitsmaß: Kosinus-Ähnlichkeit
- Anzahl der zurückgegebenen Chunks (Top-k):
- Besonderheiten: 

### 2.4 LLM-Integration

- Verwendetes LLM: neural-chat
- Prompt-Design: Kontextinformationen + Frage
- Besonderheiten: 

---
## 3. Evaluation

### 3.1 Evaluationsmethoden

- Manuelle Überprüfung der Antworten durch Experten

### Metriken


### 3.2 Testfragen
- Frage 1: 
- Frage 2:
- Frage 3:

| Frage | Erwartete Antwort | Modellantwort | Bewertung |
|-------|------------------|--------------|-----------|
| 1     |                  |              |           |
| 2     |                  |              |           |
| 3     |                  |              |           |

### 3.4 Analyse

---
## 4. Reflexion

### 4.1 Erkennisse

### 4.2 Probleme 
- Chunking war eine große Herausforderung, besonders die Tabellen 
### 4.3 Verbesserungspotential

---
## 5. Fazit 
