# Evaluation der Chunks (dritter Chunking-Durchlauf)

## Erster Eindruck
Der dritte Chunking-Durchlauf zeigt eine deutliche Verbesserung gegenüber den vorherigen Ansätzen. 
Insbesondere die Aufteilung nach Paragraphen in den Studienordnungen sowie nach Modulblöcken im 
Modulhandbuch führt zu inhaltlich sinnvolleren Chunks.

## Positive Beobachtungen
- Die Studienordnungen werden überwiegend sinnvoll nach Paragraphen aufgeteilt.
- Wörter werden im Vergleich zu den vorherigen Durchläufen kaum noch getrennt.
- Im Modulhandbuch ist die Aufteilung nach Modulen deutlich besser nachvollziehbar.
- Die meisten Chunks enthalten nun zusammenhängendere Informationseinheiten.

## Verbleibende Probleme
- Eine Fußzeilenvariante wird noch nicht zuverlässig entfernt, z. B.:
  `Nr. 17/14 Amtliches Mitteilungsblatt der HTW Berlin Seite 319`
- Vereinzelt treten weiterhin Fehler innerhalb einzelner Wörter auf, z. B.:
  `Vo rbereitung`
- Tabellen, insbesondere Studienplanübersichten vom 1. bis zum 6. Semester, werden weiterhin
  mitten im Inhalt gechunkt.
- Im Modulhandbuch wurde in einem Einzelfall ein NNBSP innerhalb eines Satzes festgestellt.

## Bewertung
Die aktuelle Chunking-Strategie ist für Fließtext und paragraphenbasierte Inhalte bereits deutlich 
brauchbarer als die vorherigen Ansätze. Problematisch bleiben jedoch tabellenbasierte Inhalte, da 
hier die semantische Zuordnung einzelner Zeilen und Spalten nicht zuverlässig erhalten bleibt.

## Fazit
Für einen ersten RAG-Prototypen ist der aktuelle Stand bei Fließtexten und Modulbeschreibungen 
weitgehend brauchbar. Für tabellenlastige Inhalte ist jedoch noch Vorsicht geboten, da hier 
Informationsverlust oder fehlerhafte Zuordnungen möglich sind.