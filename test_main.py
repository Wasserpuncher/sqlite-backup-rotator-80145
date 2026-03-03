import unittest
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Importiere die Klasse, die getestet werden soll
from main import BackupRotator, logger

class TestBackupRotator(unittest.TestCase):
    """
    Testsuite für die BackupRotator-Klasse.
    """
    def setUp(self):
        """
        Wird vor jedem Testfall ausgeführt.
        Erstellt temporäre Verzeichnisse und Dateien für Tests.
        """
        # Erstelle ein temporäres Verzeichnis für Tests
        self.test_dir = Path("./test_temp_data")
        self.test_dir.mkdir(exist_ok=True)

        # Erstelle ein temporäres Sicherungsverzeichnis
        self.temp_backup_dir = self.test_dir / "temp_backups"
        self.temp_backup_dir.mkdir(exist_ok=True)

        # Erstelle eine temporäre Dummy-Datenbankdatei
        self.dummy_db_path = self.test_dir / "test_db.sqlite"
        self.dummy_db_path.touch() # Erstellt eine leere Datei
        self.dummy_db_path.write_text("dummy data") # Fügt etwas Inhalt hinzu

        # Deaktiviere Logging für Tests, um die Ausgabe sauber zu halten
        logger.setLevel(os.environ.get("LOG_LEVEL", "CRITICAL"))

    def tearDown(self):
        """
        Wird nach jedem Testfall ausgeführt.
        Löscht temporäre Verzeichnisse und Dateien.
        """
        # Entferne das temporäre Testverzeichnis und seinen Inhalt
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        logger.setLevel(os.environ.get("LOG_LEVEL", "INFO")) # Setze Logging-Level zurück

    def test_init_success(self):
        """
        Testet die erfolgreiche Initialisierung des BackupRotators.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 5)
        self.assertEqual(rotator.db_path, self.dummy_db_path)
        self.assertEqual(rotator.backup_dir, self.temp_backup_dir)
        self.assertEqual(rotator.retention_days, 5)

    def test_init_db_not_found(self):
        """
        Testet die Initialisierung, wenn die Datenbankdatei nicht existiert.
        """
        non_existent_db = self.test_dir / "non_existent.sqlite"
        with self.assertRaises(FileNotFoundError):
            BackupRotator(non_existent_db, self.temp_backup_dir, 5)

    def test_init_invalid_retention_days(self):
        """
        Testet die Initialisierung mit ungültigen Aufbewahrungstagen.
        """
        with self.assertRaises(ValueError):
            BackupRotator(self.dummy_db_path, self.temp_backup_dir, 0)
        with self.assertRaises(ValueError):
            BackupRotator(self.dummy_db_path, self.temp_backup_dir, -1)

    def test_create_backup_success(self):
        """
        Testet die erfolgreiche Erstellung einer Sicherung.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 5)
        backup_path = rotator.create_backup()

        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.is_file())
        # Überprüfe, ob der Dateiname das korrekte Format hat (test_db_YYYYMMDD_HHMMSS.sqlite)
        self.assertRegex(backup_path.name, r"test_db_\d{8}_\d{6}\\.sqlite")
        # Überprüfe, ob der Inhalt kopiert wurde
        self.assertEqual(backup_path.read_text(), "dummy data")

    @patch('shutil.copy2', side_effect=IOError("Simulierter Kopierfehler"))
    def test_create_backup_failure(self, mock_copy2):
        """
        Testet den Fall, dass die Sicherungserstellung fehlschlägt.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 5)
        backup_path = rotator.create_backup()
        self.assertIsNone(backup_path)
        mock_copy2.assert_called_once() # Stelle sicher, dass shutil.copy2 aufgerufen wurde

    def test_rotate_backups_deletes_old_files(self):
        """
        Testet, ob alte Sicherungsdateien korrekt gelöscht werden.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 2) # Aufbewahrung: 2 Tage

        # Erstelle eine aktuelle Sicherung (sollte nicht gelöscht werden)
        current_date_str = (datetime.now() - timedelta(hours=1)).strftime("%Y%m%d_%H%M%S")
        recent_backup = self.temp_backup_dir / f"test_db_{current_date_str}.sqlite"
        recent_backup.touch()

        # Erstelle eine alte Sicherung (sollte gelöscht werden)
        old_date_str = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d_%H%M%S")
        old_backup = self.temp_backup_dir / f"test_db_{old_date_str}.sqlite"
        old_backup.touch()

        # Erstelle eine weitere alte Sicherung (sollte gelöscht werden)
        older_date_str = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d_%H%M%S")
        older_backup = self.temp_backup_dir / f"test_db_{older_date_str}.sqlite"
        older_backup.touch()

        # Erstelle eine Datei, die nicht dem Muster entspricht (sollte nicht gelöscht werden)
        other_file = self.temp_backup_dir / "other_file.txt"
        other_file.touch()

        self.assertTrue(recent_backup.exists())
        self.assertTrue(old_backup.exists())
        self.assertTrue(older_backup.exists())
        self.assertTrue(other_file.exists())

        rotator.rotate_backups()

        self.assertTrue(recent_backup.exists()) # Sollte noch existieren
        self.assertFalse(old_backup.exists())    # Sollte gelöscht werden
        self.assertFalse(older_backup.exists())  # Sollte gelöscht werden
        self.assertTrue(other_file.exists())    # Sollte noch existieren

    def test_rotate_backups_no_files_to_delete(self):
        """
        Testet, ob keine Dateien gelöscht werden, wenn alle aktuell sind.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 7) # Aufbewahrung: 7 Tage

        # Erstelle einige aktuelle Sicherungen
        for i in range(3):
            date_str = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d_%H%M%S")
            backup_file = self.temp_backup_dir / f"test_db_{date_str}.sqlite"
            backup_file.touch()
            self.assertTrue(backup_file.exists())

        initial_files_count = len(list(self.temp_backup_dir.iterdir()))
        rotator.rotate_backups()
        final_files_count = len(list(self.temp_backup_dir.iterdir()))

        self.assertEqual(initial_files_count, final_files_count) # Keine Dateien sollten gelöscht werden

    def test_run_full_process(self):
        """
        Testet den gesamten Sicherungs- und Rotationsprozess.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 1) # Aufbewahrung: 1 Tag

        # Erstelle eine alte Sicherung, die gelöscht werden sollte
        old_date_str = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d_%H%M%S")
        old_backup = self.temp_backup_dir / f"test_db_{old_date_str}.sqlite"
        old_backup.touch()
        self.assertTrue(old_backup.exists())

        # Führe den Prozess aus
        rotator.run()

        # Überprüfe, ob eine neue Sicherung erstellt wurde
        new_backups = list(self.temp_backup_dir.glob(f"{self.dummy_db_path.stem}_*.sqlite"))
        self.assertEqual(len(new_backups), 1) # Nur eine neue Sicherung sollte existieren
        self.assertFalse(old_backup.exists()) # Die alte Sicherung sollte gelöscht worden sein

    def test_run_backup_creation_failure_skips_rotation(self):
        """
        Testet, ob die Rotation übersprungen wird, wenn die Sicherungserstellung fehlschlägt.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 1)

        # Erstelle eine alte Sicherung, die eigentlich gelöscht werden sollte
        old_date_str = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d_%H%M%S")
        old_backup = self.temp_backup_dir / f"test_db_{old_date_str}.sqlite"
        old_backup.touch()
        self.assertTrue(old_backup.exists())

        # Mock create_backup, damit es None zurückgibt (Fehler)
        with patch.object(rotator, 'create_backup', return_value=None) as mock_create_backup:
            rotator.run()
            mock_create_backup.assert_called_once()
            # Da create_backup fehlschlägt, sollte rotate_backups nicht aufgerufen werden
            self.assertTrue(old_backup.exists()) # Die alte Sicherung sollte NICHT gelöscht worden sein

    def test_filename_parsing_robustness(self):
        """
        Testet die Robustheit der Dateinamen-Parsierung für rotate_backups.
        """
        rotator = BackupRotator(self.dummy_db_path, self.temp_backup_dir, 1)

        # Ungültige Dateinamen, die nicht dem Muster entsprechen
        (self.temp_backup_dir / "test_db_invalid.sqlite").touch()
        (self.temp_backup_dir / "test_db_2023_invalid.sqlite").touch()
        (self.temp_backup_dir / "another_db_20230101_120000.sqlite").touch() # Anderer Datenbankname

        # Eine gültige alte Sicherung, die gelöscht werden sollte
        old_date_str = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d_%H%M%S")
        valid_old_backup = self.temp_backup_dir / f"test_db_{old_date_str}.sqlite"
        valid_old_backup.touch()

        rotator.rotate_backups()

        self.assertTrue((self.temp_backup_dir / "test_db_invalid.sqlite").exists())
        self.assertTrue((self.temp_backup_dir / "test_db_2023_invalid.sqlite").exists())
        self.assertTrue((self.temp_backup_dir / "another_db_20230101_120000.sqlite").exists())
        self.assertFalse(valid_old_backup.exists()) # Diese sollte gelöscht worden sein

if __name__ == '__main__':
    unittest.main()
