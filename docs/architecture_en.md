# Architecture Deep Dive: SQLite Backup Rotator

This document provides a detailed overview of the architecture, design principles, and components of the SQLite Backup Rotator project.

## 1. High-Level Overview

The SQLite Backup Rotator is a standalone Python application designed to ensure the continuous availability and integrity of local SQLite databases through automated backup and rotation. It operates by periodically creating timestamped copies of a specified SQLite database and then pruning older backups based on a user-defined retention policy. The core principle is simplicity, reliability, and ease of integration into existing system schedules (e.g., cron jobs).

## 2. Core Components

The project is primarily structured around a single, cohesive class: `BackupRotator`, complemented by a command-line interface (CLI) driven by `argparse`.

### 2.1. `BackupRotator` Class (`main.py`)

This is the heart of the application, encapsulating all backup and rotation logic.

*   **Purpose**: To manage the lifecycle of SQLite database backups, from creation to deletion.
*   **Key Responsibilities**:
    *   **Initialization (`__init__`)**:
        *   Takes `db_path` (Path to the source database), `backup_dir` (Path for backups), and `retention_days` (integer) as arguments.
        *   Performs initial validation (e.g., `db_path` exists, `retention_days` is positive).
        *   Ensures the `backup_dir` exists, creating it if necessary.
    *   **Backup Creation (`create_backup`)**:
        *   Generates a unique, timestamped filename for the backup (e.g., `my_db_YYYYMMDD_HHMMSS.sqlite`).
        *   Uses `shutil.copy2` to copy the source database to the backup directory. `shutil.copy2` preserves metadata, which can be useful.
        *   Logs the success or failure of the backup operation.
        *   Returns the path to the newly created backup or `None` on failure.
    *   **Backup Rotation (`rotate_backups`)**:
        *   Calculates a `cutoff_date` based on `datetime.now()` minus `retention_days`.
        *   Iterates through all files in the `backup_dir` that match the expected backup filename pattern (e.g., `db_name_*.sqlite`).
        *   Parses the timestamp from each backup filename.
        *   If a backup's timestamp is older than the `cutoff_date`, it is deleted using `Path.unlink()`.
        *   Includes robust error handling for parsing issues or deletion failures.
    *   **Execution Orchestration (`run`)**:
        *   Orchestrates the entire process: first calls `create_backup()`, and if successful, then calls `rotate_backups()`.
        *   Ensures that rotation only occurs if a new backup was successfully created, preventing accidental deletion of all backups if the creation step fails.

### 2.2. Command-Line Interface (`main` function in `main.py`)

The `main` function serves as the entry point for the application when run from the command line.

*   **Purpose**: To parse command-line arguments and instantiate/execute the `BackupRotator`.
*   **Key Components**:
    *   **`argparse`**: Used to define and parse `db_path`, `--backup_dir`, and `--retention_days`.
    *   **Argument Validation**: Basic type conversion and default value assignment.
    *   **Error Handling**: Catches `FileNotFoundError` (for `db_path`) and `ValueError` (for `retention_days`) from the `BackupRotator` constructor, providing user-friendly error messages and exiting with a non-zero status code.

## 3. Data Flow and Process

1.  **Initialization**: User executes `main.py` with arguments.
2.  **Argument Parsing**: `argparse` in `main()` processes CLI arguments.
3.  **Rotator Instantiation**: `main()` creates an instance of `BackupRotator`, passing the parsed paths and retention days. The `BackupRotator` validates inputs and prepares the backup directory.
4.  **Process Execution**: `main()` calls `rotator.run()`.
5.  **Backup Creation**: `rotator.run()` calls `rotator.create_backup()`.
    *   Source DB is copied to a new timestamped file in `backup_dir`.
    *   Success/failure is logged.
6.  **Backup Rotation**: If `create_backup()` was successful, `rotator.run()` calls `rotator.rotate_backups()`.
    *   The rotator scans `backup_dir` for files matching the database's backup pattern.
    *   It identifies and deletes backups older than the configured `retention_days`.
    *   Actions are logged.
7.  **Completion**: The process finishes, logging its overall status.

```mermaid
graph TD
    A[Start main.py] --> B{Parse CLI Arguments};
    B --> C{Instantiate BackupRotator};
    C -- Valid Inputs --> D[Call rotator.run()];
    C -- Invalid Inputs --> E[Log Error & Exit];

    D --> F[create_backup()];
    F -- Success --> G[rotate_backups()];
    F -- Failure --> H[Log Error & Skip Rotation];

    G --> I[Scan backup_dir for old backups];
    I --> J{Is backup older than retention?};
    J -- Yes --> K[Delete backup];
    J -- No --> L[Keep backup];
    K --> I;
    L --> I;
    I -- All backups processed --> M[End Process];

    H --> M;
```

## 4. Error Handling and Logging

*   **Logging**: The `logging` module is used throughout the application to provide informative messages at different levels (INFO, WARNING, ERROR, CRITICAL). This is crucial for monitoring the script's execution in automated environments.
*   **Robustness**:
    *   `FileNotFoundError` is caught during `BackupRotator` initialization if the source database doesn't exist.
    *   `ValueError` is raised for invalid `retention_days`.
    *   `shutil.copy2` operations are wrapped in `try-except` blocks to handle potential `IOError` or other exceptions during file copying.
    *   `Path.unlink()` operations are also wrapped to handle `OSError` if a file cannot be deleted.
    *   Timestamp parsing in `rotate_backups` includes `try-except` for `ValueError` and `IndexError` to gracefully handle malformed backup filenames.
    *   The `run` method ensures that `rotate_backups` is only called if `create_backup` was successful, preventing unintended data loss.

## 5. Directory Structure

```
sqlite-backup-rotator/
├── main.py                     # Core application logic and CLI entry point
├── test_main.py                # Unit tests for the BackupRotator class
├── requirements.txt            # Python dependencies
├── README.md                   # English project documentation
├── README_de.md                # German project documentation
├── CONTRIBUTING.md             # Guidelines for contributors
├── LICENSE                     # MIT License details
├── .gitignore                  # Specifies intentionally untracked files to ignore
├── .github/
│   └── workflows/
│       └── python-app.yml      # GitHub Actions CI/CD workflow
└── docs/
    ├── architecture_en.md      # English architecture deep dive (this file)
    └── architecture_de.md      # German architecture deep dive
```

## 6. Future Enhancements / Roadmap

*   **Configuration File Support**: Implement loading parameters from a `config.json` or `config.ini` file to simplify deployment and management.
*   **More Flexible Retention Policies**: Add support for "keep N latest backups" or different policies for daily/weekly/monthly backups.
*   **Cloud Storage Integration**: Options to upload backups to S3, Azure Blob Storage, Google Cloud Storage, etc.
*   **Encryption**: Support for encrypting backup files at rest.
*   **Health Checks/Monitoring**: Integration with monitoring systems (e.g., Prometheus metrics, health check endpoints).
*   **Dockerization**: Provide a Docker image for easier deployment in containerized environments.
*   **Database Locking**: Implement more robust SQLite database locking mechanisms (e.g., using `sqlite3.connect(..., isolation_level=None)` for `BEGIN IMMEDIATE` or similar) during the copy operation to ensure data consistency, especially for actively written-to databases. Currently, `shutil.copy2` copies the file directly, which might lead to an inconsistent backup if the DB is being actively written to without proper locking.

This architecture prioritizes clarity, maintainability, and robustness for its initial scope, while laying a solid foundation for future expansion.
