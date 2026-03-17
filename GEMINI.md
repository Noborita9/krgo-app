# GEMINI.md - Krgo

This file provides instructional context for Gemini when interacting with the `Krgo` project.

## Project Overview

**Krgo** is a minimal Python project. Currently, it serves as a basic template or starting point for a Python-based application. The project name "Krgo" suggests it might be inspired by Rust's "Cargo" or possibly related to Kubernetes (often abbreviated as "k8s").

- **Main Technologies:** Python 3.12+
- **Project Structure:**
  - `main.py`: The entry point of the application.
  - `pyproject.toml`: Project metadata and dependency configuration.
  - `.python-version`: Specifies the preferred Python version (3.12).

## Building and Running

Since this is a standard Python project, you can run it directly:

- **Run the main script:**
  ```bash
  python main.py
  ```

- **Install dependencies (if added in the future):**
  If using `pip`:
  ```bash
  pip install .
  ```
  If using `uv` (recommended for fast dependency management):
  ```bash
  uv sync
  ```

## Development Conventions

- **Python Version:** The project is configured for Python 3.12.
- **Project Configuration:** Project settings and dependencies are managed in `pyproject.toml` following PEP 621.
- **Entry Point:** The primary execution logic should reside in `main.py` or be called from it.

## TODOs

- [ ] Add a description to `pyproject.toml`.
- [ ] Implement core functionality in `main.py`.
- [ ] Add project details to `README.md`.
- [ ] Set up testing (e.g., `pytest`).
