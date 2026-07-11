# Local Testing Guide

Run all commands from the repository root:

```bash
cd /Users/shahisharedohy/Desktop/robinhood/fintip
```

The monitor is notification-only. None of these tests should access an account or place a trade.

## 1. Check Python Syntax

```bash
python3 -m py_compile \
  user_input.py \
  trading/monitoring_plan.py \
  trading/preferences.py \
  trading/notifications.py \
  trading/monitor.py \
  trading/robinhood_mcp.py \
  tests/test_monitor.py
```

Success produces no output.

## 2. Run the Automated Tests

If `pytest` is installed:

```bash
python3 -m pytest -q
```

Without `pytest`, run the test functions directly:

```bash
python3 -c 'import tempfile; from pathlib import Path; import tests.test_monitor as t; t.test_build_monitoring_plan_validates_and_normalizes(); t.test_band_edges_independence_and_transition_rearming(); t.test_missing_quote_and_notification_failure_preserve_target_state(); t.test_multiple_tickers_continue_after_partial_quote_failure(); t.test_json_round_trips(Path(tempfile.mkdtemp())); t.test_quote_boundary_and_malformed_responses(); t.test_console_notification_formatting(); print("monitor tests passed")'
```

Expected output:

```text
monitor tests passed
```

The tests cover preference validation, exact band edges, independent buy and sell alerts, duplicate suppression, re-arming, partial quote failures, notification failures, JSON persistence, malformed MCP responses, and console formatting.

## 3. Collect Preferences Locally

Run the interactive collector:

```bash
python3 user_input.py
```

For a repeatable AAPL example, use:

```bash
printf 'AAPL\n100\n500\n200\n\n' | python3 user_input.py
```

This configures:

- AAPL buy target: `$100`
- Investment budget: `$500`
- Sell target: `$200`
- Alert threshold: default `5%`

Inspect the saved preferences:

```bash
cat .fintip_preferences.json
```

The file is local and git-ignored.

## 4. Test an Alert with a Fake Quote

The following check uses the saved preferences and supplies an in-memory quote. It does not call Robinhood:

```bash
python3 - <<'PY'
from trading.monitor import run_monitoring_cycle
from trading.notifications import ConsoleNotifier
from trading.preferences import load_preferences


class FakeQuoteClient:
    def get_quotes(self, tickers):
        return {
            ticker: {
                "price": 102.00,
                "timestamp": "2026-07-11T12:00:00-04:00",
            }
            for ticker in tickers
        }


state, errors = run_monitoring_cycle(
    load_preferences(),
    FakeQuoteClient(),
    ConsoleNotifier(),
)

print("State:", state)
print("Errors:", errors)
PY
```

For the AAPL example, `$102` is 2% from the `$100` buy target and should produce one buy-target alert. `Errors` should be empty.

## 5. Test Duplicate Suppression and Re-arming

```bash
python3 - <<'PY'
from trading.monitor import run_monitoring_cycle
from trading.notifications import ConsoleNotifier
from trading.preferences import load_preferences


class FakeQuoteClient:
    def __init__(self, price):
        self.price = price

    def get_quotes(self, tickers):
        return {
            ticker: {
                "price": self.price,
                "timestamp": "2026-07-11T12:00:00-04:00",
            }
            for ticker in tickers
        }


preferences = load_preferences()
state = {}

for price in (102, 103, 120, 101):
    print(f"\nChecking ${price}:")
    state, errors = run_monitoring_cycle(
        preferences,
        FakeQuoteClient(price),
        ConsoleNotifier(),
        state,
    )
    print("State:", state)
    print("Errors:", errors)
PY
```

Expected buy-target behavior for the AAPL example:

1. `$102` enters the band and sends an alert.
2. `$103` remains inside and does not send a duplicate.
3. `$120` leaves the band and re-arms the alert.
4. `$101` re-enters and sends another alert.

## 6. Test the Scheduled CLI Safety Check

```bash
python3 -m trading.monitor
```

Until the real Robinhood MCP server name and quote-tool schema are configured, this should exit with an error similar to:

```text
Error: Robinhood quote MCP is not configured. Supply the MCP server name and a quote-tool adapter matching its schema.
```

This is the expected safe behavior. The monitor must not fall back to account access or order submission.

## 7. Reset Local Test Data

The following files contain only local runtime data and are git-ignored:

```text
.fintip_preferences.json
.fintip_alert_state.json
```

Delete them manually when you want to start with fresh preferences and alert state.
