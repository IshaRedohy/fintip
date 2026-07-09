# Repository Guidelines

## Project Structure & Module Organization

This directory contains a small Python project for collecting stock preferences and investment targets.

- `variables.py`: interactive script that collects stock choices, buy targets, and sell target preferences.
- `nasdaq_100_directory.csv`: stock validation data used by `variables.py`.
- `prompts/`: plain-text requirement notes for implemented features.

No formal test directory exists yet. If tests are added, place them under `tests/` and mirror the source module names.

## Build, Test, and Development Commands

Run the interactive script:

```bash
python3 variables.py
```

Check Python syntax without running the prompts:

```bash
python3 -m py_compile variables.py
```

List repository files:

```bash
rg --files
```

There is no package build step at this stage.

## Coding Style & Naming Conventions

Use standard Python style with 4-space indentation. Prefer descriptive snake_case names for functions and variables, such as `validate_stock`, `get_stip_type`, and `read_nasdaq_directory`.

Keep user prompts short and clear. Normalize user input with `.strip().lower()` where comparisons should be case-insensitive. Use Python's `csv` module for CSV parsing instead of manual string splitting.

## Testing Guidelines

There is no testing framework configured yet. For now, verify changes with `py_compile` and manual sample runs.

When adding tests, use `pytest`, name files like `test_variables.py`, and cover validation behavior for ticker matches, company-name matches, invalid inputs, and shorthand `stip` values.

## Commit & Pull Request Guidelines

This project is now tracked in Git on the `main` branch. Keep commits focused on one logical change.

Use concise, imperative commit messages, for example:

```text
Add stock validation for user input
```

Before committing, run `git status --short` and avoid committing generated files such as `__pycache__/`.

Pull requests should include a short summary, manual test commands run, and any changes to expected input/output behavior.
