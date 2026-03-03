# SQLite Backup Rotator

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/<your-username>/sqlite-backup-rotator/actions/workflows/python-app.yml/badge.svg)](https://github.com/<your-username>/sqlite-backup-rotator/actions/workflows/python-app.yml)

## 🚀 Overview

The **SQLite Backup Rotator** is an enterprise-ready, open-source Python tool designed to automate the backup and rotation of local SQLite database files. It provides a robust and easy-to-use solution for maintaining a history of your critical SQLite data, ensuring data integrity and allowing for recovery from potential data loss scenarios. With configurable retention policies, it efficiently manages disk space by automatically deleting old backups.

## ✨ Features

*   **Automated Backups**: Easily create timestamped backups of any SQLite database.
*   **Configurable Rotation**: Define how many days backups should be retained.
*   **Disk Space Management**: Automatically deletes old backups to free up storage.
*   **Robust & Reliable**: Built with error handling and logging for production environments.
*   **Simple Command-Line Interface**: Easy to integrate into cron jobs or scheduled tasks.
*   **Pythonic & Type-Hinted**: Clean, maintainable code with modern Python practices.

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<your-username>/sqlite-backup-rotator.git
    cd sqlite-backup-rotator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

To run the backup rotator, simply execute the `main.py` script with the required arguments.

```bash
python main.py <path_to_your_sqlite_database> [--backup_dir <path_to_backup_directory>] [--retention_days <number_of_days>]
```

**Arguments:**

*   `<path_to_your_sqlite_database>` (required): The absolute or relative path to the SQLite `.sqlite` or `.db` file you want to back up.
*   `--backup_dir` (optional): The directory where backup files will be stored. Defaults to `./backups`. If the directory does not exist, it will be created.
*   `--retention_days` (optional): The number of days to retain backups. Backups older than this will be deleted. Defaults to `7`. Must be a positive integer.

**Examples:**

1.  **Basic backup with default settings:**
    This will back up `my_app.sqlite` to `./backups` and retain backups for 7 days.
    ```bash
    python main.py my_app.sqlite
    ```

2.  **Specify backup directory and retention:**
    This will back up `data/production.db` to `/var/backups/sqlite` and retain backups for 30 days.
    ```bash
    python main.py data/production.db --backup_dir /var/backups/sqlite --retention_days 30
    ```

## 🗓️ Scheduling (e.g., with Cron)

For automated daily backups, you can schedule the script using `cron` on Linux/macOS or Task Scheduler on Windows.

**Example Cron Job (daily at 2 AM):**

1.  Open your crontab editor:
    ```bash
    crontab -e
    ```
2.  Add the following line (adjust paths as necessary):
    ```cron
    0 2 * * * /usr/bin/python3 /path/to/sqlite-backup-rotator/main.py /path/to/your/database.sqlite --backup_dir /path/to/your/backup/folder --retention_days 14 >> /var/log/sqlite_backup.log 2>&1
    ```
    *   Make sure `/usr/bin/python3` is the correct path to your Python interpreter.
    *   Replace `/path/to/sqlite-backup-rotator/` with the actual path to this project.
    *   Replace `/path/to/your/database.sqlite` and `/path/to/your/backup/folder` with your specific paths.
    *   The `>> /var/log/sqlite_backup.log 2>&1` part redirects all output (stdout and stderr) to a log file.

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support / Contact

If you have any questions, feel free to open an issue on the GitHub repository.
