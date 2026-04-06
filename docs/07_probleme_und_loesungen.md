## Problem: 
PDF  wurde zunächst nicht gefunden.
## Lösung:
Pfadlogik in main.py angepasst, Projektroot als Basis für relative Pfade genutzt, damit PDF-Dateien unabhängig vom Arbeitsverzeichnis gefunden werden können.

## Problem:
PDF-Text enthält kleinere Layout-Artefakte.
## Lösung:
Qualität der Extraktion grob geprüft, Artefakte als akzeptabel eingestuft,da Inhalte weitgehend verständlich bleiben; spätere Textbereinigung vorgesehen

## Problem:
1. Front MAtter / Inhaltsverzeichnis führt zu vielen irrelevanten Chunks
2. Falsche Split-Grenzen führen zu abgeschnittenen Wörtern und unverständlichen Chunks
3. zu lang gewordene Paragraphen greift Fallback und schneidet stumpf nach Länge, dadurch werden Sätze, Unerpunkte und Tabellen zerissen.
4. PDF-artefakte: Fußzeilen, Silbentrennung,Zeilenumbrüche in Tabellen und getrennte Wörter durch Bindestriche verschlechtern die semantische einheit zusätzlich.

## Lösung:
- Studienordnung nach echten Paragraphen und Unterpunkten chunken, nicht nach fixer Länge
- Modulhandbuch nach Modulblöcken chunken, nicht nach fixer Länge
- vor dem Chunking einfache Textbereinigung durchführen, um Artefakte zu entfernen (z. B. Zeilenumbrüche, Silbentrennung, Fußzeilen)
- zu lnage Einheiten: nicht mitten im Satz, sondern an Unterpunlten (1),(2) oder Absatzgrenzen trennen

## Problem:
- Dokumentstruktur erknnen und bewahren 

## Lösung:
- strukturorientiertes Chunking + leichtes Text-Cleaning vor dem Chunking

## Problem:
- einfache Tabellen-Erkennung beim Chunken nicht erfolgreich am Ende entsteht ein super langer Chunk.

## Lösung:
- begrenzte TAbellenblock-Größe 

