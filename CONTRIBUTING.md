# Contributing to SQLite Backup Rotator

We welcome contributions to the SQLite Backup Rotator project! Your help is invaluable in making this tool even better. Whether it's reporting a bug, suggesting a new feature, improving the documentation, or submitting code, every contribution is appreciated.

Please take a moment to review this document to make the contribution process as smooth as possible.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md) (to be added). By participating, you are expected to uphold this code. Please report unacceptable behavior to [project maintainers email/contact].

## How Can I Contribute?

### 🐛 Reporting Bugs

*   **Check existing issues**: Before opening a new issue, please check if a similar bug has already been reported.
*   **Provide detailed information**: When reporting a bug, include:
    *   A clear and concise description of the bug.
    *   Steps to reproduce the behavior.
    *   Expected behavior vs. actual behavior.
    *   Screenshots or error logs if applicable.
    *   Your operating system, Python version, and project version.

### ✨ Suggesting Enhancements

*   **Check existing issues**: Look for similar feature requests.
*   **Describe the feature**: Clearly explain the new functionality or improvement.
*   **Explain the use case**: Describe why this feature would be valuable and how it would be used.
*   **Consider alternatives**: If you have thought about different ways to implement it, mention them.

### 📝 Improving Documentation

Documentation is crucial! If you find any inaccuracies, unclear sections, or missing information in the `README.md`, `README_de.md`, or `docs/` files, please feel free to open a pull request.

### 💻 Contributing Code

1.  **Fork the repository**: Start by forking the `sqlite-backup-rotator` repository to your GitHub account.
2.  **Clone your fork**:
    ```bash
    git clone https://github.com/your-username/sqlite-backup-rotator.git
    cd sqlite-backup-rotator
    ```
3.  **Create a new branch**: Choose a descriptive name for your branch (e.g., `feature/add-config-file`, `bugfix/fix-rotation-logic`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Set up your development environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    pip install pytest flake8 # Install dev tools
    ```
5.  **Make your changes**: Implement your feature or bug fix.
    *   **Code Style**: Adhere to PEP 8. We use `flake8` for linting.
    *   **Type Hints**: Use type hints for all function signatures and complex variables.
    *   **Docstrings**: Write clear docstrings for new functions, classes, and methods.
    *   **Comments**: Use German inline comments to explain complex logic as per project guidelines.
    *   **Tests**: Add or update unit tests in `test_main.py` to cover your changes. Ensure all existing tests pass.
6.  **Run tests and linting**:
    ```bash
    pytest
    flake8 .
    ```
7.  **Commit your changes**: Write clear, concise commit messages.
    ```bash
    git add .
    git commit -m "feat: Add configuration file support"
    ```
8.  **Push to your fork**:
    ```bash
    git push origin feature/your-feature-name
    ```
9.  **Open a Pull Request (PR)**:
    *   Go to the original `sqlite-backup-rotator` repository on GitHub.
    *   You should see a prompt to create a new pull request from your recently pushed branch.
    *   Provide a clear title and description for your PR, referencing any related issues.
    *   Ensure all CI checks pass.

## Code Review Process

The project maintainers will review your pull request. They may provide feedback or request changes. Please be responsive to these comments to facilitate a smooth review process. Once approved, your changes will be merged into the `main` branch.

Thank you for contributing!
