from datetime import datetime

from trading.monitor import run_monitoring_cycle
from trading.monitoring_plan import build_monitoring_plan
from trading.notifications import ConsoleNotifier, format_alert
from trading.preferences import (
    load_alert_state,
    load_preferences,
    save_alert_state,
    save_preferences,
)
from trading.robinhood_mcp import (
    RobinhoodMCPConfigurationError,
    RobinhoodQuoteClient,
    normalize_quote_response,
)


PREFERENCES = build_monitoring_plan(
    [
        {
            "ticker": "aapl",
            "buy_target_price": 100,
            "investment_budget": 500,
            "sell_target_price": 200,
            "threshold_percent": 5,
        }
    ]
)


class FakeQuoteClient:
    def __init__(self, prices):
        self.prices = prices

    def get_quotes(self, tickers):
        return {
            ticker: {"price": self.prices[ticker], "timestamp": "2026-07-10T12:00:00Z"}
            for ticker in tickers
            if ticker in self.prices
        }


class RecordingNotifier:
    def __init__(self, fail=False):
        self.alerts = []
        self.fail = fail

    def notify(self, alert):
        if self.fail:
            raise RuntimeError("delivery unavailable")
        self.alerts.append(alert)


def test_build_monitoring_plan_validates_and_normalizes():
    assert PREFERENCES[0]["ticker"] == "AAPL"
    assert PREFERENCES[0]["threshold_percent"] == 5.0
    for field in ("buy_target_price", "investment_budget", "sell_target_price", "threshold_percent"):
        invalid = dict(PREFERENCES[0], **{field: 0})
        try:
            build_monitoring_plan([invalid])
            assert False, f"expected {field} validation"
        except ValueError:
            pass


def test_band_edges_independence_and_transition_rearming():
    notifier = RecordingNotifier()
    state, errors = run_monitoring_cycle(PREFERENCES, FakeQuoteClient({"AAPL": 95}), notifier)
    assert not errors
    assert [alert["target_type"] for alert in notifier.alerts] == ["buy"]
    assert state["AAPL"] == {"buy": True, "sell": False}

    state, errors = run_monitoring_cycle(PREFERENCES, FakeQuoteClient({"AAPL": 100}), notifier, state)
    assert len(notifier.alerts) == 1

    state, errors = run_monitoring_cycle(PREFERENCES, FakeQuoteClient({"AAPL": 120}), notifier, state)
    assert state["AAPL"]["buy"] is False

    state, errors = run_monitoring_cycle(PREFERENCES, FakeQuoteClient({"AAPL": 105}), notifier, state)
    assert len(notifier.alerts) == 2

    state, errors = run_monitoring_cycle(PREFERENCES, FakeQuoteClient({"AAPL": 190}), notifier, state)
    assert notifier.alerts[-1]["target_type"] == "sell"
    assert state["AAPL"] == {"buy": False, "sell": True}


def test_missing_quote_and_notification_failure_preserve_target_state():
    initial = {"AAPL": {"buy": False, "sell": False}}
    state, errors = run_monitoring_cycle(PREFERENCES, FakeQuoteClient({}), RecordingNotifier(), initial)
    assert state == initial
    assert errors == ["Missing quote for AAPL"]

    state, errors = run_monitoring_cycle(
        PREFERENCES, FakeQuoteClient({"AAPL": 100}), RecordingNotifier(fail=True), initial
    )
    assert state["AAPL"]["buy"] is False
    assert "Notification failed" in errors[0]


def test_multiple_tickers_continue_after_partial_quote_failure():
    preferences = PREFERENCES + build_monitoring_plan(
        [{"ticker": "MSFT", "buy_target_price": 50, "investment_budget": 100,
          "sell_target_price": 80, "threshold_percent": 2}]
    )
    notifier = RecordingNotifier()
    state, errors = run_monitoring_cycle(
        preferences, FakeQuoteClient({"MSFT": 50}), notifier
    )
    assert errors == ["Missing quote for AAPL"]
    assert "AAPL" not in state
    assert state["MSFT"]["buy"] is True
    assert [alert["ticker"] for alert in notifier.alerts] == ["MSFT"]


def test_json_round_trips(tmp_path):
    preferences_path = tmp_path / "preferences.json"
    state_path = tmp_path / "state.json"
    save_preferences(PREFERENCES, preferences_path)
    assert load_preferences(preferences_path) == PREFERENCES
    expected_state = {"AAPL": {"buy": True, "sell": False}}
    save_alert_state(expected_state, state_path)
    assert load_alert_state(state_path) == expected_state


def test_quote_boundary_and_malformed_responses():
    assert normalize_quote_response({"AAPL": 123.4}, ["aapl"]) == {
        "AAPL": {"price": 123.4, "timestamp": None}
    }
    try:
        normalize_quote_response({"AAPL": {"price": "bad"}}, ["AAPL"])
        assert False, "expected malformed response failure"
    except ValueError:
        pass
    try:
        RobinhoodQuoteClient().get_quotes(["AAPL"])
        assert False, "expected configuration failure"
    except RobinhoodMCPConfigurationError:
        pass


def test_console_notification_formatting():
    alert = {
        "ticker": "AAPL",
        "current_price": 101,
        "target_type": "buy",
        "target_price": 100,
        "distance_percent": 1,
        "threshold_percent": 5,
        "checked_at": datetime(2026, 7, 10).isoformat(),
    }
    lines = []
    ConsoleNotifier(lines.append).notify(alert)
    assert lines == [format_alert(alert)]
    assert "AAPL buy target" in lines[0]
    assert "distance 1.00%" in lines[0]
