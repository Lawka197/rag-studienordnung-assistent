# Verbesserung 1: Optimierte Tabellen-Erkennung & Chunking

## Problem (aus evaluation.md)

**Testfall:** 2 - "Wie viele Fachsemester gibt es?"

**Problem:** 
- Studienplan liegt in Tabelle
- Tabelle wird schlecht gechunkt
- Retrieval findet nur irrelevante Paragraphen
- Resultat: Leere Antwort

**Aktuelle Metriken:**
- Korrektheit: 1/5
- Vollständigkeit: 1/5
- Relevanz: 1/5
- **Durchschnitt: 1.0/5** 

---

## Hypothese

> Wenn ich die Tabellenerkennung verbesser und `max_table_chunk_length` erhöhe, werden Tabelleninhalte besser gechunkt und gelesen
> 
> **Erwartet:** Score für Testfall 2 steigt auf 3-4/5

---

## Geplante Änderungen

### Änderung 1: Tabellen-Erkennungs-Schwelle senken
- **Datei:** `src/rag_studienordnung_assistent/chunking/chunking_config.py`
- **Feld:** `table_detection_threshold`
- **Vorher:** 3
- **Nachher:** 2
- **Grund:** Erkennt mehr Tabellenarten (auch einfache Tabellen)

### Änderung 2: Maximale Tabellen-Chunk-Größe erhöhen
- **Datei:** `src/rag_studienordnung_assistent/chunking/chunking_config.py`
- **Feld:** `max_table_chunk_length`
- **Vorher:** 3200 Zeichen
- **Nachher:** 5000 Zeichen
- **Grund:** Erlaubt größere Tabellen in einem Chunk

---

### Test-Ergebnisse

| Testfall | Metriken | VORHER | NACHHER | Status            |
|----------|----------|--------|---------|-------------------|
| Testfall 2 | Korrektheit | 1/5 | 1/5     | keine Veränderung |
| Testfall 2 | Vollständigkeit | 1/5 | 1/5     | keine Veränderung |
| Testfall 2 | Relevanz | 1/5 | 1/5     | keine Veränderung |
| Testfall 2 | **Durchschnitt** | **1.0** | **1.0** | keine Veränderung |

### Erkenntnisse
- Tabellen gefunden? Nein
- Scores verbessert? Nein
