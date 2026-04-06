# Evaluation der Chunks (zweiter Chunking-Durchlauf)

## Ziel
Ziel dieser Analyse ist die Bewertung der Qualität der erzeugten Chunks nach Anpassung des Chunking-Prozesses.  
Dabei wird untersucht, ob sich Lesbarkeit, inhaltliche Kohärenz und die Eignung für ein RAG-basiertes 
Frage-Antwort-System im Vergleich zum ersten Versuch verbessert haben.

---

## Bewertung der Chunk-Qualität

| Kriterium              | Alte Ordnung | Neue Ordnung | Modulhandbuch | Kommentar |
|------------------------|---------|---------|---------------|----------|
| Lesbarkeit             |  mittel |  mittel | mittel        | Weniger Metadaten, aber noch Formatprobleme |
| Inhaltliche Kohärenz   |  mittel |  mittel | mittel        | Teilweise vollständige Abschnitte |
| Relevanz für QA-System |  mittel |  mittel | mittel        | Mehr fachlicher Inhalt vorhanden |
| Struktur erkannt       |  teilweise|  teilweise| teilweise     | Modulstruktur klar erkennbar |

---

## Analyse

Im Vergleich zum ersten Chunking-Versuch zeigen sich deutliche Verbesserungen:

- Die Chunks enthalten nun **mehr inhaltlich relevante Abschnitte** (z. B. Paragraphen, Modulbeschreibungen)
- Besonders im Modulhandbuch entstehen **strukturierte und semantisch sinnvolle Einheiten**
- Mittlere Chunks sind deutlich besser nutzbar als Anfangs-Chunks

Dennoch bestehen weiterhin Probleme:

- **Abgeschnittene Inhalte** treten weiterhin auf (z. B. „Ma“)
- Listen und Aufzählungen werden weiterhin **nicht sauber segmentiert**
- Tabellenartige Strukturen bleiben schwer lesbar
- Formatierungsprobleme aus der PDF-Extraktion sind weiterhin sichtbar

---

## Vergleich zum ersten Chunking-Versuch

| Aspekt                     | Erster Versuch        | Zweiter Versuch        |
|---------------------------|----------------------|------------------------|
| Inhalt                    | überwiegend Metadaten| mehr fachlicher Inhalt |
| Lesbarkeit                | schlecht             | verbessert             |
| Kohärenz                 | sehr gering          | teilweise vorhanden    |
| RAG-Eignung              | ungeeignet           | eingeschränkt geeignet |
| Struktur                 | kaum erkennbar       | teilweise erkennbar    |

Wichtig:
Der zweite Versuch ist **kein Durchbruch**, aber ein klarer Fortschritt.

---

## Fazit

Das aktuelle Chunking ist **teilweise geeignet**, aber noch nicht optimal:

- Einige Chunks (v. a. mittlere und Modulhandbuch) sind bereits gut nutzbar
- Viele Chunks enthalten jedoch weiterhin strukturelle Probleme
- Für ein robustes RAG-System ist die Qualität noch nicht ausreichend

---

## Nächste Schritte

- Einführung von **Preprocessing**:
  - Entfernen von unnötigen Zeilenumbrüchen
  - Bereinigung von Formatierungsartefakten

- Verbesserung des Chunkings:
  - Chunking nach **Absätzen oder Paragraphen (§)**
  - Nutzung von **Überschriften als natürliche Grenzen**

- Spezifische Behandlung von:
  - Listen
  - Tabellen
  - Inhaltsverzeichnissen

---

## Reflexion

Der zweite Chunking-Durchlauf zeigt, dass bereits kleine Anpassungen die Qualität deutlich verbessern können.  
Gleichzeitig wird klar, dass ein rein technischer Ansatz (fixed-size) nicht ausreicht.

Für ein funktionierendes RAG-System ist ein **semantisch orientiertes Chunking erforderlich**.