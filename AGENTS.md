# Repository Guidelines

## Project Structure & Module Organization

This directory contains a small Python project for collecting stock preferences and monitoring prices near buy and sell targets. It sends notifications only and must never place trades.

- `user_input.py`: collect and validate terminal responses, then save monitoring preferences.
- `trading/monitoring_plan.py`: normalize and validate monitoring preferences.
- `trading/preferences.py`: load and save versioned preference and alert-state JSON files.
- `trading/monitor.py`: perform one deterministic monitoring cycle and provide the scheduled CLI entry point.
- `trading/notifications.py`: define the notification interface and console implementation.
- `trading/robinhood_mcp.py`: isolate the quote-only Robinhood MCP boundary.
- `trading/order_plan.py`: legacy order-planning code; do not use it from the monitor.
- `tests/test_monitor.py`: focused monitoring, persistence, quote, and notification tests.
- `nasdaq_100_directory.csv`: stock validation data used by `user_input.py`.
- `prompts/`: plain-text requirement notes for implemented features.

Place new tests under `tests/` and mirror source module names where practical.

## Monitoring Workflow Design

Keep responsibilities separated:

- `user_input.py` handles terminal input and ticker validation.
- `trading/monitoring_plan.py` validates normalized tickers, positive target prices, budgets, and thresholds.
- `trading/preferences.py` owns local JSON persistence.
- `trading/robinhood_mcp.py` retrieves quotes only.
- `trading/monitor.py` evaluates price bands and manages alert transitions.
- `trading/notifications.py` delivers alerts without embedding provider-specific logic in the monitor.

Do not add a subagent for the monitoring flow unless the project later needs true multi-agent review or auditing. Keep the implementation as deterministic Python modules and a scheduled CLI command.

The monitor must never expose or invoke account access, order planning, or order submission. The Robinhood adapter must remain quote-only. Until the real MCP server name, authentication setup, and quote-tool schema are known, raise a clear configuration error.

Proximity is symmetric around each target and is calculated as:

```text
abs(current_price - target_price) / target_price
```

Track buy and sell bands independently. Notify only when a target moves from outside to inside its configured band. Re-arm it after the price leaves. Missing or invalid quotes and notification failures must produce actionable errors without incorrectly advancing alert state.

The initial notification provider is the console. Keep AWS SES, SNS, and Twilio as possible future adapters without selecting one prematurely.

## Local Persistence

Preferences are stored in `.fintip_preferences.json`, including a schema version and per-ticker buy target, investment budget, sell target, and threshold percentage. Alert transitions are stored in `.fintip_alert_state.json`.

Both runtime files are git-ignored. Use atomic replacement when saving JSON so an interrupted write does not leave a partially written state file.

## Build, Test, and Development Commands

Collect and save preferences interactively:

```bash
python3 user_input.py
```

Run a scripted preference sample. The blank final input selects the default 5% threshold:

```bash
printf 'AAPL\n100\n500\n200\n\n' | python3 user_input.py
```

Run one monitoring cycle:

```bash
python3 -m trading.monitor
```

Until the Robinhood quote MCP is configured, this command should exit with a clear configuration error and must not change alert state or attempt a trade.

Check Python syntax without running prompts:

```bash
python3 -m py_compile user_input.py trading/monitoring_plan.py trading/preferences.py trading/notifications.py trading/monitor.py trading/robinhood_mcp.py tests/test_monitor.py
```

Run current assertions without `pytest`:

```bash
python3 -c 'import tempfile; from pathlib import Path; import tests.test_monitor as t; t.test_build_monitoring_plan_validates_and_normalizes(); t.test_band_edges_independence_and_transition_rearming(); t.test_missing_quote_and_notification_failure_preserve_target_state(); t.test_multiple_tickers_continue_after_partial_quote_failure(); t.test_json_round_trips(Path(tempfile.mkdtemp())); t.test_quote_boundary_and_malformed_responses(); t.test_console_notification_formatting(); print("monitor tests passed")'
```

If `pytest` is available:

```bash
python3 -m pytest -q
```

List repository files:

```bash
rg --files
```

There is no package build step at this stage.

## Coding Style & Naming Conventions

Use standard Python style with 4-space indentation. Prefer descriptive snake_case names such as `validate_stock`, `build_monitoring_plan`, and `run_monitoring_cycle`.

Use import-friendly filenames with underscores. Keep terminal prompts and error messages short and actionable. Normalize ticker symbols to uppercase at module boundaries and use positive numeric values for prices, budgets, and thresholds.

Use Python's `csv` module for CSV parsing and `json` for persistence. Keep core monitoring calculations pure and inject quote clients and notifiers so tests never require network or brokerage access.

## Testing Guidelines

There is no required testing framework dependency. Verify changes with `py_compile`, direct assertions, and manual runs with a fake quote client before connecting a real MCP server.

Write pytest-compatible functions named like `test_monitor.py` or `test_user_input.py`. Cover:

- Empty, unsupported, and normalized ticker inputs.
- Non-positive and malformed target prices, budgets, and thresholds.
- Prices outside, exactly on, and inside both sides of a proximity band.
- Independent buy-target and sell-target evaluation.
- One alert on entry, suppression while inside, and re-alerting after exit and re-entry.
- Preference and alert-state JSON round trips.
- Multiple tickers, missing quotes, partial failures, and malformed MCP responses.
- Notification formatting and failure behavior.
- The absence of order submission from every monitoring path.

## Commit & Pull Request Guidelines

This project is tracked in Git on the `main` branch. Keep commits focused on one logical change.

Use concise, imperative commit messages, for example:

```text
Add price target notification monitor
```

Before committing, run `git status --short` and avoid committing generated files such as `__pycache__/`, `.fintip_preferences.json`, or `.fintip_alert_state.json`.

Pull requests should include a short summary, test commands run, changes to expected input/output behavior, and any remaining Robinhood MCP configuration requirements.
