# Setup und Projektinitialisierung

## Ziel
Ziel dieses Schrittes war die Einrichtung einer stabilen und reproduzierbaren Entwicklungsumgebung für das RAG-Projekt zur Analyse von Studienordnungen.

## Lokale Projektanlage
Das Projekt wurde lokal in PyCharm erstellt und folgende grundlegende Ordnerstruktur angelegt:
- data/: zur Ablage der PDF-Dokumente der Studienordnungen
- src/: für den Quellcode des Projekts
- tests/: für Testfälle und Testdaten
- docs/: für die Projektdokumentation

## Versionskontrolle mit Git und GitHub
Ein GitHub-Repository wurde vorab erstellt (inklusive README.md und .gitignore für Python)

Anschließend wurde das lokale Projekt mit dem GitHub-Repository verbunden:
- Initialisierung des lokalen Git-Repositorys mit `git init`
- Hinzufügen des Remote-Repositorys mit `git remote add origin <GitHub-URL
- Erster Commit der lokalen Projektstruktur

Beim ersten Push-Versuch gab es einen Konflikt, da das Remote-Repository bereits eine README.md und .gitignore enthielt. 

Dieser Konflikt wurde gelöst durch:

Das Zusammenführen der Remote-Änderungen mit dem lokalen Branch mittels:
```git pull origin main --allow-unrelated-histories --no-rebase
```
Danach konnte das Projekt erfolgreich gepusht werden.

## Virtuelle Umgebung und Abhängigkeiten
Eine virtuelle Umgebung wurde mit `python -m venv .venv` erstellt und aktiviert.

## Installation von Abhängigkeiten
Für den Einstieg wurden folgende Python-Pakete installiert:
- pypdf: zum Einlesen und Verarbeiten von PDF-Dokumenten
- python-dotenv: zum Laden von Umgebungsvariablen aus einer .env-Datei

Die installierten Pakete wurden in einer `requirements.txt` festgehalten, um die Reproduzierbarkeit der Entwicklungsumgebung zu gewährleisten.

## Ergebnis
Die Entwicklungsumgebung ist vollständig eingereichtet:
GitHub-Inegration funktioniert
Repository ist bereinigt und strukturiert 
Virtuelle Umgebung ist aktiv und erste Abhängigkeiten sind installiert

Damit ist die Grundlage für die Implementierung des RAG-Systems geschaffen. 


