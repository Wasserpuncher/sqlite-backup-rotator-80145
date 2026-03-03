# SQLite Sicherungsrotator

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/<your-username>/sqlite-backup-rotator/actions/workflows/python-app.yml/badge.svg)](https://github.com/<your-username>/sqlite-backup-rotator/actions/workflows/python-app.yml)

## 🚀 Übersicht

Der **SQLite Sicherungsrotator** ist ein unternehmenstaugliches, quelloffenes Python-Tool, das entwickelt wurde, um die Sicherung und Rotation lokaler SQLite-Datenbankdateien zu automatisieren. Es bietet eine robuste und benutzerfreundliche Lösung zur Pflege einer Historie Ihrer kritischen SQLite-Daten, gewährleistet die Datenintegrität und ermöglicht die Wiederherstellung nach potenziellen Datenverlustszenarien. Mit konfigurierbaren Aufbewahrungsrichtlinien verwaltet es den Speicherplatz effizient, indem es alte Sicherungen automatisch löscht.

## ✨ Funktionen

*   **Automatisierte Sicherungen**: Erstellen Sie einfach zeitgestempelte Sicherungen jeder SQLite-Datenbank.
*   **Konfigurierbare Rotation**: Definieren Sie, wie viele Tage Sicherungen aufbewahrt werden sollen.
*   **Speicherplatzverwaltung**: Löscht automatisch alte Sicherungen, um Speicherplatz freizugeben.
*   **Robust & Zuverlässig**: Entwickelt mit Fehlerbehandlung und Logging für Produktionsumgebungen.
*   **Einfache Kommandozeilenschnittstelle**: Leicht in Cron-Jobs oder geplante Aufgaben zu integrieren.
*   **Pythonisch & Typ-Hinweise**: Sauberer, wartbarer Code mit modernen Python-Praktiken.

## ⚙️ Installation

1.  **Klonen Sie das Repository:**
    ```bash
    git clone https://github.com/<your-username>/sqlite-backup-rotator.git
    cd sqlite-backup-rotator
    ```

2.  **Erstellen Sie eine virtuelle Umgebung (empfohlen):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate
    ```

3.  **Installieren Sie Abhängigkeiten:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Verwendung

Um den Sicherungsrotator auszuführen, führen Sie einfach das Skript `main.py` mit den erforderlichen Argumenten aus.

```bash
python main.py <pfad_zu_ihrer_sqlite_datenbank> [--backup_dir <pfad_zum_sicherungsverzeichnis>] [--retention_days <anzahl_tage>]
```

**Argumente:**

*   `<pfad_zu_ihrer_sqlite_datenbank>` (erforderlich): Der absolute oder relative Pfad zur SQLite-Datei (`.sqlite` oder `.db`), die gesichert werden soll.
*   `--backup_dir` (optional): Das Verzeichnis, in dem Sicherungsdateien gespeichert werden. Standard ist `./backups`. Wenn das Verzeichnis nicht existiert, wird es erstellt.
*   `--retention_days` (optional): Die Anzahl der Tage, für die Sicherungen aufbewahrt werden sollen. Sicherungen, die älter als diese Anzahl von Tagen sind, werden gelöscht. Standard ist `7`. Muss eine positive Ganzzahl sein.

**Beispiele:**

1.  **Einfache Sicherung mit Standardeinstellungen:**
    Dies sichert `my_app.sqlite` in `./backups` und behält Sicherungen für 7 Tage.
    ```bash
    python main.py my_app.sqlite
    ```

2.  **Sicherungsverzeichnis und Aufbewahrung angeben:**
    Dies sichert `data/production.db` in `/var/backups/sqlite` und behält Sicherungen für 30 Tage.
    ```bash
    python main.py data/production.db --backup_dir /var/backups/sqlite --retention_days 30
    ```

## 🗓️ Planung (z.B. mit Cron)

Für automatisierte tägliche Sicherungen können Sie das Skript mit `cron` unter Linux/macOS oder dem Aufgabenplaner unter Windows planen.

**Beispiel Cron-Job (täglich um 2 Uhr morgens):**

1.  Öffnen Sie Ihren Crontab-Editor:
    ```bash
    crontab -e
    ```
2.  Fügen Sie die folgende Zeile hinzu (Pfade nach Bedarf anpassen):
    ```cron
    0 2 * * * /usr/bin/python3 /pfad/zum/sqlite-backup-rotator/main.py /pfad/zu/ihrer/datenbank.sqlite --backup_dir /pfad/zu/ihrem/sicherungsordner --retention_days 14 >> /var/log/sqlite_backup.log 2>&1
    ```
    *   Stellen Sie sicher, dass `/usr/bin/python3` der korrekte Pfad zu Ihrem Python-Interpreter ist.
    *   Ersetzen Sie `/pfad/zum/sqlite-backup-rotator/` durch den tatsächlichen Pfad zu diesem Projekt.
    *   Ersetzen Sie `/pfad/zu/ihrer/datenbank.sqlite` und `/pfad/zu/ihrem/sicherungsordner` durch Ihre spezifischen Pfade.
    *   Der Teil `>> /var/log/sqlite_backup.log 2>&1` leitet alle Ausgaben (stdout und stderr) in eine Protokolldatei um.

## 🤝 Mitwirken

Wir freuen uns über Beiträge! Weitere Informationen zum Einstieg finden Sie in unserer [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert – weitere Details finden Sie in der Datei [LICENSE](LICENSE).

## 📞 Support / Kontakt

Bei Fragen können Sie gerne ein Issue im GitHub-Repository eröffnen.
