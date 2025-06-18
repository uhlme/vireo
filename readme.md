# Pflanzenschutzmittel-Planer

Eine Web-Anwendung zur Erstellung und Verwaltung von Pflanzenschutzmittel-Plänen für die Schweizer Landwirtschaft. Das Projekt besteht aus einem Django-Backend (API) und einem Vue.js-Frontend.
Voraussetzungen

Bevor du beginnst, stelle sicher, dass die folgenden Werkzeuge auf deinem System installiert sind:

    Python (Version 3.10+)
    Node.js (Version 18+)
    Git

Erstmalige Installation auf einem neuen Rechner

Diese Schritte sind nur notwendig, wenn du das Projekt auf einem neuen Computer einrichtest.

    Projekt herunterladen (clonen):
    Bash

    git clone <DEINE_GITHUB_REPO_URL>
    cd <projekt-ordner>

Backend einrichten:
Bash

## Virtuelle Umgebung erstellen
    python3 -m venv venv

## Virtuelle Umgebung aktivieren
### Für Windows:
    .\venv\Scripts\activate
### Für macOS / Linux:
    source venv/bin/activate

## Alle Python-Pakete installieren
    pip install -r requirements.txt

## Die Datenbank-Struktur erstellen
    python manage.py migrate

## Einen Administrator-Benutzer für den Login anlegen
    python manage.py createsuperuser

## Die BLV-Daten importieren (dies kann einige Minuten dauern)
    python manage.py import_psm

## Frontend einrichten:
Bash

    # In den Frontend-Ordner wechseln
    cd frontend

    # Alle JavaScript-Pakete installieren
    npm install

## Anwendung im Entwicklungsmodus starten

Für die tägliche Arbeit musst du zwei Terminals gleichzeitig offen haben.
### Terminal 1: Backend-Server starten

    Navigiere in den Haupt-Projektordner (z.B. C:\vireo).
    Aktiviere die virtuelle Umgebung:
        Windows: .\venv\Scripts\activate
        macOS/Linux: source venv/bin/activate
    Starte den Django-Server:
    Bash

    python manage.py runserver

    Das Backend ist jetzt unter http://127.0.0.1:8000 erreichbar.

### Terminal 2: Frontend-Server starten

    Navigiere in den frontend-Unterordner.
    Starte den Vue-Entwicklungsserver:
    Bash

    npm run serve

    Das Frontend ist jetzt unter http://localhost:8080 erreichbar.

Öffne http://localhost:8080/ in deinem Web-Browser, um die Anwendung zu sehen und zu benutzen.
### Wichtige Befehle

    Daten neu importieren: python manage.py import_psm
    Datenbank-Modelle ändern:
        python manage.py makemigrations plaene
        python manage.py migrate