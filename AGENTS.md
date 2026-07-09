# Repository Guidelines

## Project Structure & Module Organization

This directory contains a small Python project for collecting stock preferences, investment targets, and trade planning.

- `user_input.py`: interactive script that collects stock choices, buy targets, and sell target preferences.
- `trading/`: trade planning and brokerage integration code.
- `tests/`: focused tests for pure planning and dry-run behavior.
- `nasdaq_100_directory.csv`: stock validation data used by `user_input.py`.
- `prompts/`: plain-text requirement notes for implemented features.

Place new tests under `tests/` and mirror the source module names where practical.

## Trading Workflow Design

Keep the project split into three simple responsibilities:

- `user_input.py`: collect and validate user responses from the terminal.
- `trading/order_plan.py`: convert validated user responses into intended trade plans.
- `trading/robinhood_mcp.py`: isolate Robinhood MCP account access and order execution.

Do not add a subagent for the trading flow unless the project later needs true multi-agent review or auditing. Keep the first implementation as normal Python modules.

Do not add `trading/preferences.py` unless structured preference objects, such as dataclasses, are actually needed. If it is added later, use it only for typed preference data, not terminal prompts or brokerage calls.

Default Robinhood-related work to a dry-run path during development. `submit_order_plan(..., dry_run=True)` must not place live orders. Before live execution is added, print the exact proposed orders and require an explicit confirmation step.

## Build, Test, and Development Commands

Run the interactive script:

```bash
python3 user_input.py
```

Check Python syntax without running the prompts:

```bash
python3 -m py_compile user_input.py trading/order_plan.py trading/robinhood_mcp.py tests/test_order_plan.py
```

Run the current test assertions without `pytest`:

```bash
python3 -c 'import tests.test_order_plan as t; t.test_build_order_plan_from_user_responses(); t.test_format_order_plan(); t.test_submit_order_plan_dry_run_does_not_submit(); print("order plan tests passed")'
```

Run a manual dry-run sample:

```bash
printf 'AAPL\n100\n10\nc\n' | python3 user_input.py
```

List repository files:

```bash
rg --files
```

There is no package build step at this stage.

## Coding Style & Naming Conventions

Use standard Python style with 4-space indentation. Prefer descriptive snake_case names for functions and variables, such as `validate_stock`, `get_stip_type`, and `read_nasdaq_directory`.

Use import-friendly Python filenames with underscores, such as `user_input.py`, instead of hyphens.

Keep user prompts short and clear. Normalize user input with `.strip().lower()` where comparisons should be case-insensitive. Use Python's `csv` module for CSV parsing instead of manual string splitting.

## Testing Guidelines

There is no testing framework dependency installed yet. For now, verify changes with `py_compile`, the direct assertion command above, and manual sample runs.

When adding tests, write pytest-compatible functions named like `test_order_plan.py` or `test_user_input.py`. Cover validation behavior for ticker matches, company-name matches, invalid inputs, shorthand `stip` values, order-plan formatting, and dry-run submission behavior.

## Commit & Pull Request Guidelines

This project is now tracked in Git on the `main` branch. Keep commits focused on one logical change.

Use concise, imperative commit messages, for example:

```text
Add stock validation for user input
```

Before committing, run `git status --short` and avoid committing generated files such as `__pycache__/`.

Pull requests should include a short summary, manual test commands run, and any changes to expected input/output behavior.
