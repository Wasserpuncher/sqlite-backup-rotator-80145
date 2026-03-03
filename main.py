import argparse
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Konfiguriere das Logging-System für die Anwendung
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupRotator:
    """
    Verwaltet die Erstellung und Rotation von SQLite-Datenbanksicherungen.

    Diese Klasse bietet Funktionen zum Erstellen von zeitgestempelten Sicherungen
    einer SQLite-Datenbank und zum Löschen alter Sicherungen basierend auf einer
    definierten Aufbewahrungsrichtlinie.
    """

    def __init__(self, db_path: Path, backup_dir: Path, retention_days: int) -> None:
        """
        Initialisiert den BackupRotator.

        Args:
            db_path: Der Pfad zur originalen SQLite-Datenbankdatei.
            backup_dir: Das Verzeichnis, in dem die Sicherungen gespeichert werden sollen.
            retention_days: Die Anzahl der Tage, für die Sicherungen aufbewahrt werden sollen.
                            Sicherungen, die älter als diese Anzahl von Tagen sind, werden gelöscht.
        """
        # Überprüfe, ob der Datenbankpfad existiert und eine Datei ist
        if not db_path.is_file():
            logger.error(f"Datenbankdatei nicht gefunden: {db_path}")
            raise FileNotFoundError(f"Datenbankdatei nicht gefunden: {db_path}")
        self.db_path: Path = db_path

        # Stelle sicher, dass das Sicherungsverzeichnis existiert
        self.backup_dir: Path = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True) # Erstellt das Verzeichnis, falls es nicht existiert

        # Stelle sicher, dass die Aufbewahrungstage gültig sind
        if retention_days <= 0:
            logger.error(f"Ungültige Aufbewahrungsdauer: {retention_days}. Muss größer als 0 sein.")
            raise ValueError("Aufbewahrungstage müssen positiv sein.")
        self.retention_days: int = retention_days

        logger.info(f"BackupRotator initialisiert für Datenbank: {self.db_path}")
        logger.info(f"Sicherungsverzeichnis: {self.backup_dir}, Aufbewahrungsdauer: {self.retention_days} Tage")

    def create_backup(self) -> Optional[Path]:
        """
        Erstellt eine neue, zeitgestempelte Sicherung der Datenbank.

        Die Sicherungsdatei wird im Format `datenbankname_YYYYMMDD_HHMMSS.sqlite` benannt
        und im konfigurierten Sicherungsverzeichnis gespeichert.

        Returns:
            Der Pfad zur erstellten Sicherungsdatei, oder None, falls ein Fehler auftrat.
        """
        # Generiere einen Zeitstempel für den Dateinamen
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Erstelle den Namen der Sicherungsdatei
        backup_filename: str = f"{self.db_path.stem}_{timestamp}.sqlite"
        backup_path: Path = self.backup_dir / backup_filename

        try:
            # Kopiere die Datenbankdatei an den Sicherungspfad
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Sicherung erfolgreich erstellt: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Sicherung für {self.db_path}: {e}")
            return None

    def rotate_backups(self) -> None:
        """
        Löscht Sicherungen, die älter sind als die definierte Aufbewahrungsdauer.

        Identifiziert alle Sicherungsdateien im Sicherungsverzeichnis, die dem
        Namensmuster `datenbankname_YYYYMMDD_HHMMSS.sqlite` entsprechen, und
        löscht diejenigen, deren Datum vor dem aktuellen Datum minus `retention_days` liegt.
        """
        # Berechne das Datum, vor dem Sicherungen gelöscht werden sollen
        cutoff_date: datetime = datetime.now() - timedelta(days=self.retention_days)
        logger.info(f"Lösche Sicherungen vor dem Datum: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Iteriere durch alle Dateien im Sicherungsverzeichnis
        for backup_file in self.backup_dir.glob(f"{self.db_path.stem}_*.sqlite"):
            # Extrahiere den Zeitstempel aus dem Dateinamen
            try:
                # Der Zeitstempel beginnt nach dem Datenbanknamen und dem Unterstrich
                parts = backup_file.stem.split('_')
                if len(parts) < 2:
                    raise ValueError("Dateiname hat nicht genug Teile für Zeitstempel-Parsing")
                timestamp_str: str = f"{parts[-2]}_{parts[-1]}"
                backup_date: datetime = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                # Überprüfe, ob die Sicherung älter als das Cutoff-Datum ist
                if backup_date < cutoff_date:
                    backup_file.unlink() # Lösche die Datei
                    logger.info(f"Alte Sicherung gelöscht: {backup_file}")
            except (ValueError, IndexError) as e:
                logger.warning(f"Konnte Datum aus Dateiname '{backup_file.name}' nicht parsen. Überspringe. Fehler: {e}")
            except OSError as e:
                logger.error(f"Fehler beim Löschen der Sicherung '{backup_file.name}': {e}")

    def run(self) -> None:
        """
        Führt den gesamten Sicherungs- und Rotationsprozess aus.

        Erstellt zuerst eine neue Sicherung und führt dann die Rotation durch.
        """
        logger.info("Starte den Sicherungs- und Rotationsprozess.")
        new_backup_path: Optional[Path] = self.create_backup()
        if new_backup_path:
            self.rotate_backups()
        else:
            logger.error("Sicherung konnte nicht erstellt werden, Rotation wird übersprungen.")
        logger.info("Sicherungs- und Rotationsprozess abgeschlossen.")

def main() -> None:
    """
    Hauptfunktion für das Kommandozeilen-Interface.

    Verwendet `argparse`, um Datenbankpfad, Sicherungsverzeichnis und
    Aufbewahrungstage von der Kommandozeile zu empfangen und den
    BackupRotator zu initialisieren und auszuführen.
    """
    # Erstelle einen Argument-Parser
    parser = argparse.ArgumentParser(
        description="Automatischer Datenbank-Backup-Rotator für lokale SQLite-Dateien."
    )
    # Füge Argumente hinzu
    parser.add_argument(
        "db_path",
        type=str,
        help="Der Pfad zur SQLite-Datenbankdatei, die gesichert werden soll."
    )
    parser.add_argument(
        "--backup_dir",
        type=str,
        default="./backups",
        help="Das Verzeichnis, in dem Sicherungen gespeichert werden sollen. Standard: './backups'."
    )
    parser.add_argument(
        "--retention_days",
        type=int,
        default=7,
        help="Die Anzahl der Tage, für die Sicherungen aufbewahrt werden sollen. Standard: 7 Tage."
    )

    # Parse die Argumente
    args = parser.parse_args()

    try:
        # Erstelle Pfad-Objekte aus den String-Argumenten
        db_path_obj: Path = Path(args.db_path)
        backup_dir_obj: Path = Path(args.backup_dir)

        # Initialisiere und führe den BackupRotator aus
        rotator = BackupRotator(db_path_obj, backup_dir_obj, args.retention_days)
        rotator.run()
    except FileNotFoundError as e:
        logger.critical(f"Kritischer Fehler: {e}. Bitte überprüfen Sie den Datenbankpfad.")
        exit(1)
    except ValueError as e:
        logger.critical(f"Kritischer Fehler bei den Argumenten: {e}.")
        exit(1)
    except Exception as e:
        logger.critical(f"Ein unerwarteter Fehler ist aufgetreten: {e}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    main()
