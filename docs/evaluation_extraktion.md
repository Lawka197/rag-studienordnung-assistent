# Evaluation der PDF-Extraktion

## Ziel
Ziel dieser Analyse ist die Bewertung der Qualität der PDF-Extraktion aus den verwendeten PDF-Dokumenten im Hinblick auf die spätere Verwendung in einem RAG-basierten Frage-Antwort-System.

Die Bewertung erfolgt anhand von definierter Kriterien: Lesebarkeit, Struktur, Tabellenqualität sowie anhand typischer Nutzerfragen

## Bewertungsmatrix

### Bewertungsskala

| Wert   | Bedeutung |
|--------|-----------|
| 1      | unbrauchbar, unlesbar, keine Struktur, Tabellen unbrauchbar |
| 2      | schlecht, teilweise lesbar, Struktur kaum erkennbar, Tabellen teilweise unbrauchbar |
| 3      | akzeptabel, lesbar, Struktur erkennbar, Tabellen teilweise brauchbar |
| 4      | gut, gut lesbar, Struktur klar erkennbar, Tabellen brauchbar |
| 5      | sehr gut, sehr gut lesbar, Struktur klar und vollständig erkennbar, Tabellen vollständig brauchbar |

## 1. Alte Studienordnung

### Bewertung

|Kategorie           | Bewertung                     | Begründung |
|--------------------|-------------------------------|--------------------|
|Fließtext           |            4                  | größtenteils gut lesbar |
|Tabellen            |            3                  | teilweise unübersichtlich |
|Listen              |            4                  | weitgehend korrekt |
|Sonderzeichen       |            2                  | Probleme bei Formeln & Symbolen |
|Konsistenz          |            4                  | teilweise Strukturverlust |
|RAG-Tauglichkeit    |            4                  | grundsätzlich geeignet, Verbesserungsbedarf bei Tabellen |


**Gesamtbewertung:** 3.5

### Interpretaion / Kommentare: 
- die Formel für die Berechnung des GEsamtprädikats wird nicht erkannt, würde ich erstmal akzeptieren, da ich mich auf andere Informationen konzentriere
- der Anfang mit den Paragraphen sieht super aus
- Bulletpoints werden auch erkannt
- die erste Tabelle solide 4 einige ungünstigen Zeilenumbrüche, teilweise zwei zahlen hintereinander für die Modulbezeichnung und die Gewichtung Frage wird das hier erkannt? 
- die nächsten Tabellen 3 da einige Zeilen über mehrer Spalten geht, hier könnte die Zuordnung fehlschlagen

## 2. Neue Studienordnung

### Bewertung

| Kategorie | Bewertung | Begründung |
|-----------|-----------|------------|
| Fließtext | 4 | gut lesbar |
| Tabellen | 3 | teilweise schwer verständlich, Zeilenumbrüche |
| Listen | 3 | inkonsistente Darstellung, Icons statt Bulletpoints |
| Sonderzeichen | 2 | Probleme bei Formeln und Symbolen |
| Konsistenz | 3 | teilweise Strukturverlust, insbesondere bei Listen |
| RAG-Tauglichkeit | 3 | grundsätzlich geeignet, Verbesserungsbedarf bei Tabellen und Listen |

**Gesamtbewertung:** 3.0

### Interpretaion / Kommentare: 
- die Formel für die Berechnung des GEsamtprädikats wird nicht erkannt, würde ich erstmal akzeptieren, da ich mich auf andere Informationen konzentriere
- Tabellen teilweise schwer verständlich, Zeilenumbrüche führen zu unklaren Zuordnungen, insbesondere bei Modulen mit mehreren Zeilen
- Listen teilweise inkonsistent, Icons statt Bulletpoints führen zu Erkennungsproblemen, teilweise werden Listenpunkte nicht erkannt, was die Struktur erschwert
- insgesamt ist die Extraktion brauchbar, aber es gibt Verbesserungsbedarf bei der Erkennung von Tabellen und Listen, um die spätere Nutzung zu optimieren

## 3. Modulhandbuch

### Bewertung

| Kategorie | Bewertung | Begründung |
|-----------|-----------|------------|
| Fließtext | 3 | lesbar, aber durch NBSP-Sonderzeichen beeinträchtigt |
| Tabellen | 3 | teilweise unübersichtlich, NBSP-Sonderzeichen beeinträchtigen die Lesbarkeit |
| Listen | 4 | weitgehend korrekt erkannt, Bulletpoints gut erkannt |
| Sonderzeichen | 3 | moderate Probleme |
| Konsistenz | 2 | Inhalte teilweise vermischt |
| RAG-Tauglichkeit | 2 | könnte unzuverlässig sein, insbesondere aufgrund von NBSP-Problemen und Strukturverlust |

**Gesamtbewertung:** 2.8

### Interpretaion / Kommentare: 
- das Inhaltsverzeichnis gut lesbar, allerdings wird NBSP als Sonderzeichen erkannt, was die Lesbarkeit beeinträchtigt
- NBSP-Problem auch bei Tabellen
- dafür Bulletpoints gut erkannt
- an sich wird der TExt Zeile für Zeile erkannt, allerdings teilweise mit Zeilenumbrüchen, was die Struktur erschwert

## Vergleich und Fazit 
- Insgesamt zeigt die Extraktion der PDF-Dokumente eine akzeptable Qualität, 
  wobei die alte Studienordnung am besten abschneidet, gefolgt von der neuen Studienordnung und dem Modulhandbuch
- für einen ersten Prototypen insgesamt brauchbare Ergebnisse
- Die Hauptprobleme liegen in der Erkennung von Tabellen und Sonderzeichen, insbesondere bei Formeln und Symbolen,
  sowie in der teilweise inkonsistenten Darstellung von Listen
- Für die spätere Nutzung in einem RAG-basierten Frage-Antwort-System ist die Extraktion grundsätzlich geeignet,
  jedoch sollten Verbesserungen bei der Erkennung von Tabellen und Listen sowie der Handhabung von Sonderzeichen in Betracht gezogen werden, 
  um die Zuverlässigkeit und Genauigkeit der Informationen zu erhöhen

## Gesamtvergleich der Dokumente

| Dokument | Fließtext | Tabellen | Listen | Sonderzeichen | Konsistenz | RAG-Tauglichkeit | Gesamtbewertung |
|----------|-----------|----------|--------|----------------|------------|------------------|-----------------|
| Alte Studienordnung | 4 | 3 | 4 | 2 | 4 | 4 | 3.5 |
| Neue Studienordnung | 4 | 3 | 3 | 2 | 3 | 3 | 3.0 |
| Modulhandbuch | 3 | 3 | 4 | 3 | 2 | 2 | 2.8 |