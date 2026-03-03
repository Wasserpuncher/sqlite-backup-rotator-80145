# Architektur-Deep-Dive: SQLite Sicherungsrotator

Dieses Dokument bietet einen detaillierten Überblick über die Architektur, Designprinzipien und Komponenten des SQLite Sicherungsrotator-Projekts.

## 1. Überblick auf hoher Ebene

Der SQLite Sicherungsrotator ist eine eigenständige Python-Anwendung, die entwickelt wurde, um die kontinuierliche Verfügbarkeit und Integrität lokaler SQLite-Datenbanken durch automatisierte Sicherung und Rotation zu gewährleisten. Er funktioniert, indem er periodisch zeitgestempelte Kopien einer angegebenen SQLite-Datenbank erstellt und dann ältere Sicherungen basierend auf einer benutzerdefinierten Aufbewahrungsrichtlinie bereinigt. Das Kernprinzip ist Einfachheit, Zuverlässigkeit und einfache Integration in bestehende Systemzeitpläne (z.B. Cron-Jobs).

## 2. Kernkomponenten

Das Projekt ist primär um eine einzige, kohärente Klasse strukturiert: `BackupRotator`, ergänzt durch eine Kommandozeilenschnittstelle (CLI), die von `argparse` gesteuert wird.

### 2.1. `BackupRotator`-Klasse (`main.py`)

Dies ist das Herzstück der Anwendung und kapselt die gesamte Sicherungs- und Rotationslogik.

*   **Zweck**: Den Lebenszyklus von SQLite-Datenbanksicherungen zu verwalten, von der Erstellung bis zur Löschung.
*   **Hauptaufgaben**:
    *   **Initialisierung (`__init__`)**:
        *   Nimmt `db_path` (Pfad zur Quelldatenbank), `backup_dir` (Pfad für Sicherungen) und `retention_days` (Ganzzahl) als Argumente entgegen.
        *   Führt eine erste Validierung durch (z.B. `db_path` existiert, `retention_days` ist positiv).
        *   Stellt sicher, dass das `backup_dir` existiert, und erstellt es bei Bedarf.
    *   **Sicherungserstellung (`create_backup`)**:
        *   Erzeugt einen eindeutigen, zeitgestempelten Dateinamen für die Sicherung (z.B. `meine_db_JJJJMMTT_HHMMSS.sqlite`).
        *   Verwendet `shutil.copy2`, um die Quelldatenbank in das Sicherungsverzeichnis zu kopieren. `shutil.copy2` bewahrt Metadaten, was nützlich sein kann.
        *   Protokolliert den Erfolg oder Misserfolg des Sicherungsvorgangs.
        *   Gibt den Pfad zur neu erstellten Sicherung zurück oder `None` im Fehlerfall.
    *   **Sicherungsrotation (`rotate_backups`)**:
        *   Berechnet ein `cutoff_date` basierend auf `datetime.now()` minus `retention_days`.
        *   Iteriert durch alle Dateien im `backup_dir`, die dem erwarteten Sicherungsdateinamenmuster entsprechen (z.B. `db_name_*.sqlite`).
        *   Parst den Zeitstempel aus jedem Sicherungsdateinamen.
        *   Wenn der Zeitstempel einer Sicherung älter als das `cutoff_date` ist, wird sie mit `Path.unlink()` gelöscht.
        *   Enthält eine robuste Fehlerbehandlung für Parsing-Probleme oder Löschfehler.
    *   **Ausführungs-Orchestrierung (`run`)**:
        *   Orchestriert den gesamten Prozess: Ruft zuerst `create_backup()` auf und, falls erfolgreich, dann `rotate_backups()`.
        *   Stellt sicher, dass die Rotation nur erfolgt, wenn eine neue Sicherung erfolgreich erstellt wurde, um ein versehentliches Löschen aller Sicherungen zu verhindern, falls der Erstellungsschritt fehlschlägt.

### 2.2. Kommandozeilenschnittstelle (`main`-Funktion in `main.py`)

Die `main`-Funktion dient als Einstiegspunkt für die Anwendung, wenn sie über die Kommandozeile ausgeführt wird.

*   **Zweck**: Kommandozeilenargumente zu parsen und den `BackupRotator` zu instanziieren/auszuführen.
*   **Schlüsselkomponenten**:
    *   **`argparse`**: Wird verwendet, um `db_path`, `--backup_dir` und `--retention_days` zu definieren und zu parsen.
    *   **Argumentvalidierung**: Grundlegende Typkonvertierung und Zuweisung von Standardwerten.
    *   **Fehlerbehandlung**: Fängt `FileNotFoundError` (für `db_path`) und `ValueError` (für `retention_days`) vom `BackupRotator`-Konstruktor ab, liefert benutzerfreundliche Fehlermeldungen und beendet das Programm mit einem Nicht-Null-Statuscode.

## 3. Datenfluss und Prozess

1.  **Initialisierung**: Der Benutzer führt `main.py` mit Argumenten aus.
2.  **Argument-Parsing**: `argparse` in `main()` verarbeitet CLI-Argumente.
3.  **Rotator-Instanziierung**: `main()` erstellt eine Instanz von `BackupRotator` und übergibt die geparsten Pfade und Aufbewahrungstage. Der `BackupRotator` validiert die Eingaben und bereitet das Sicherungsverzeichnis vor.
4.  **Prozessausführung**: `main()` ruft `rotator.run()` auf.
5.  **Sicherungserstellung**: `rotator.run()` ruft `rotator.create_backup()` auf.
    *   Die Quelldatenbank wird in eine neue, zeitgestempelte Datei im `backup_dir` kopiert.
    *   Erfolg/Misserfolg wird protokolliert.
6.  **Sicherungsrotation**: Wenn `create_backup()` erfolgreich war, ruft `rotator.run()` `rotator.rotate_backups()` auf.
    *   Der Rotator durchsucht `backup_dir` nach Dateien, die dem Sicherungsmuster der Datenbank entsprechen.
    *   Er identifiziert und löscht Sicherungen, die älter als die konfigurierten `retention_days` sind.
    *   Aktionen werden protokolliert.
7.  **Abschluss**: Der Prozess wird beendet und sein Gesamtstatus protokolliert.

```mermaid
graph TD
    A[main.py starten] --> B{CLI-Argumente parsen};
    B --> C{BackupRotator instanziieren};
    C -- Gültige Eingaben --> D[rotator.run() aufrufen];
    C -- Ungültige Eingaben --> E[Fehler protokollieren & Beenden];

    D --> F[create_backup()];
    F -- Erfolg --> G[rotate_backups()];
    F -- Fehler --> H[Fehler protokollieren & Rotation überspringen];

    G --> I[backup_dir nach alten Sicherungen durchsuchen];
    I --> J{Ist Sicherung älter als Aufbewahrungsdauer?};
    J -- Ja --> K[Sicherung löschen];
    J -- Nein --> L[Sicherung behalten];
    K --> I;
    L --> I;
    I -- Alle Sicherungen verarbeitet --> M[Prozess beenden];

    H --> M;
```

## 4. Fehlerbehandlung und Protokollierung

*   **Protokollierung**: Das `logging`-Modul wird in der gesamten Anwendung verwendet, um informative Nachrichten auf verschiedenen Ebenen (INFO, WARNING, ERROR, CRITICAL) bereitzustellen. Dies ist entscheidend für die Überwachung der Skriptausführung in automatisierten Umgebungen.
*   **Robustheit**:
    *   `FileNotFoundError` wird während der `BackupRotator`-Initialisierung abgefangen, wenn die Quelldatenbank nicht existiert.
    *   `ValueError` wird für ungültige `retention_days` ausgelöst.
    *   `shutil.copy2`-Operationen sind in `try-except`-Blöcke eingeschlossen, um potenzielle `IOError` oder andere Ausnahmen während des Dateikopierens zu behandeln.
    *   `Path.unlink()`-Operationen sind ebenfalls eingeschlossen, um `OSError` zu behandeln, falls eine Datei nicht gelöscht werden kann.
    *   Das Parsen von Zeitstempeln in `rotate_backups` enthält `try-except` für `ValueError` und `IndexError` zur eleganten Behandlung fehlerhafter Sicherungsdateinamen.
    *   Die `run`-Methode stellt sicher, dass `rotate_backups` nur aufgerufen wird, wenn `create_backup` erfolgreich war, wodurch unbeabsichtigter Datenverlust verhindert wird.

## 5. Verzeichnisstruktur

```
sqlite-backup-rotator/
├── main.py                     # Kernanwendungslogik und CLI-Einstiegspunkt
├── test_main.py                # Unit-Tests für die BackupRotator-Klasse
├── requirements.txt            # Python-Abhängigkeiten
├── README.md                   # Englische Projektdokumentation
├── README_de.md                # Deutsche Projektdokumentation
├── CONTRIBUTING.md             # Richtlinien für Mitwirkende
├── LICENSE                     # Details zur MIT-Lizenz
├── .gitignore                  # Spezifiziert absichtlich nicht verfolgte Dateien, die ignoriert werden sollen
├── .github/
│   └── workflows/
│       └── python-app.yml      # GitHub Actions CI/CD Workflow
└── docs/
    ├── architecture_en.md      # Englischer Architektur-Deep-Dive (diese Datei)
    └── architecture_de.md      # Deutscher Architektur-Deep-Dive
```

## 6. Zukünftige Erweiterungen / Roadmap

*   **Unterstützung für Konfigurationsdateien**: Implementierung des Ladens von Parametern aus einer `config.json`- oder `config.ini`-Datei, um die Bereitstellung und Verwaltung zu vereinfachen.
*   **Flexiblere Aufbewahrungsrichtlinien**: Unterstützung für "die N neuesten Sicherungen behalten" oder verschiedene Richtlinien für tägliche/wöchentliche/monatliche Sicherungen.
*   **Cloud-Speicherintegration**: Optionen zum Hochladen von Sicherungen auf S3, Azure Blob Storage, Google Cloud Storage usw.
*   **Verschlüsselung**: Unterstützung für die Verschlüsselung von Sicherungsdateien im Ruhezustand.
*   **Health Checks/Monitoring**: Integration mit Überwachungssystemen (z.B. Prometheus-Metriken, Health-Check-Endpunkte).
*   **Dockerisierung**: Bereitstellung eines Docker-Images für eine einfachere Bereitstellung in containerisierten Umgebungen.
*   **Datenbank-Sperrung**: Implementierung robusterer SQLite-Datenbank-Sperrmechanismen (z.B. Verwendung von `sqlite3.connect(..., isolation_level=None)` für `BEGIN IMMEDIATE` oder ähnliches) während des Kopiervorgangs, um die Datenkonsistenz zu gewährleisten, insbesondere bei aktiv beschriebenen Datenbanken. Derzeit kopiert `shutil.copy2` die Datei direkt, was zu einer inkonsistenten Sicherung führen könnte, wenn die DB ohne ordnungsgemäße Sperrung aktiv beschrieben wird.

Diese Architektur priorisiert Klarheit, Wartbarkeit und Robustheit für ihren anfänglichen Umfang und schafft gleichzeitig eine solide Grundlage für zukünftige Erweiterungen.
