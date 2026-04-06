# Evaluation des ersten Chunks

## Ziel
Ziel dieser Analyse ist die Bewertung der Qualität des ersten Chunks, 
der aus den extrahierten Textdateien der Studienordnungen erstellt wurde. 
Dabei soll insbesondere die Lesbarkeit, die inhaltliche Kohärenz sowie die 
Eignung für die spätere Verwendung in einem RAG-basierten Frage-Antwort-System bewertet werden.

## Setup

- Chunking-Methode: Fixed-Size-Chunking mit einer Chunk-Größe von 700 Zeichen und einem Overlap von 150 Zeichen
- Anzahl der Dokumente: 3 (alte Studienordnung, neue Studienordnung, Modulhandbuch)

## Beispeil-Chunks
### Chunk 1 (alte Studienordnung)
Nr. 17/14 Amtliches Mitteilungsblatt der HTW Berlin Seite 313
	24.	Juli 2014
Amtliches Mitteilungsblatt

Seite

Studien- und Prüfungsordnung
für den Bachelorstudiengang
Informatik und Wirtschaft
…
He

### Chunk 2 (neue Studienordnung)
Nr. 08/24 Amtliches Mitteilungsblatt der HTW Berlin Seite 297 
 
  
18. März 2024 
Amtliches Mitteilungsblatt 
 
Seite
Studien- und Prüfungsordnung für den 
Bachelorstudiengang Informatik und Wirtschaft  
im Fachbereich Informatik, Kommunikation 
und Wirtschaft 
vom 10. Januar 2024. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 299 
 
 
 

Seite 298 Amtliches Mitteilungsblatt der HTW Berlin Nr. 08/24 

### Chunk 3 (Modulhandbuch)
Modulhandbuch Sommersemester 2026
620 Informatik und 
Wirtschaft
 
INHALTSVERZEICHNIS
MODUL 1110 Rechnerarchitektur/Betriebssysteme  5
UNIT 1111 Rechnerarchitektur/ Betriebssysteme (SL)  5
UNIT 1112 Rechnerarchitektur/ Betriebssysteme (PCÜ)  6
MODUL 1310 Grundlegende Konzepte der Informatik  6
UNIT 1311 Grundlegende Konzepte der Informatik (SL)  7
MODUL 1410 Verteilte Systeme  8
UNIT 1411 Verteilte Systeme (SL)  8
UNIT 1412 Verteilte Systeme (PCÜ)  9
MODUL 1610 Mathematik  9
UNIT 1611 Mathematik

---

## Bewertung der Chunk-Qualität

| Kriterium              | Alte Ordnung | Neue Ordnung | Modulhandbuch | Kommentar |
|------------------------|---------|--------|----------|----------|
| Lesbarkeit             |  schlecht |  schlecht |  mittel  | Viele Leerzeilen, abgeschnittene Wörter |
| Inhaltliche Kohärenz   |  gering |  gering |  gering  | Kein zusammenhängender Inhalt |
| Relevanz für QA-System |  niedrig | niedrig | niedrig  | Enthält hauptsächlich Metadaten |
| Struktur erkannt       |  nein   |  nein  | teilweise | Inhaltsverzeichnis teilweise erkennbar |

---

## Analyse

Die untersuchten Chunks zeigen mehrere Probleme:

- Die Inhalte bestehen überwiegend aus **Metadaten** (Titel, Seitenzahlen, Amtsblatt-Informationen)
- Es gibt **keine semantisch sinnvollen Einheiten**, die für ein Frage-Antwort-System relevant wären
- Texte werden teilweise **abgeschnitten** (z. B. „He“), was auf Probleme beim Chunking oder der Textextraktion hinweist
- Viele **Leerzeilen und Formatierungsreste** verschlechtern die Lesbarkeit
- Beim Modulhandbuch wird das **Inhaltsverzeichnis mitten im Chunk abgeschnitten**, wodurch kein vollständiger Kontext entsteht

---

## Fazit

Das aktuelle Chunking ist für den Einsatz in einem RAG-System **nicht geeignet**, da:

- keine inhaltlich abgeschlossenen Textabschnitte entstehen  
- irrelevante Informationen dominieren  
- die Qualität der Chunks die spätere Retrieval-Genauigkeit stark beeinträchtigen würde  

---

## Nächste Schritte

Zur Verbesserung der Chunk-Qualität sind folgende Maßnahmen sinnvoll:

- **Preprocessing einführen:**
  - Entfernen von Headern und Footern
  - Reduzieren von Leerzeilen
- **Semantisches Chunking testen:**
  - Chunking nach Absätzen, Überschriften, Modulblöcken oder Paragraphen, statt fixer Länge
- **Chunk-Größe optimieren**
- **Inhaltsverzeichnisse gezielt herausfiltern oder separat behandeln**

---

## Reflexion

Extraktion hat funktioniert, der aktuelle Chunk ist als technischer Test okay, aber inhaltlich noch zu schwach für eine 
sinnvolle Grundlage für Retrieval.