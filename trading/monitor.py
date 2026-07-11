import argparse
import sys
from datetime import datetime, timezone

from trading.notifications import ConsoleNotifier
from trading.preferences import (
    DEFAULT_ALERT_STATE_PATH,
    DEFAULT_PREFERENCES_PATH,
    load_alert_state,
    load_preferences,
    save_alert_state,
)
from trading.robinhood_mcp import RobinhoodQuoteClient


def run_monitoring_cycle(preferences, quote_client, notifier, state=None, checked_at=None):
    state = dict(state or {})
    tickers = [item["ticker"] for item in preferences]
    quotes = quote_client.get_quotes(tickers)
    if not isinstance(quotes, dict):
        raise ValueError("Quote client returned a non-mapping response")
    errors = []

    for preference in preferences:
        ticker = preference["ticker"]
        quote = quotes.get(ticker)
        if quote is None:
            errors.append(f"Missing quote for {ticker}")
            continue
        try:
            current_price = float(quote["price"])
            quote_time = quote.get("timestamp") or checked_at
            if current_price <= 0:
                raise ValueError
        except (KeyError, TypeError, ValueError):
            errors.append(f"Invalid quote for {ticker}: expected a positive price")
            continue

        ticker_state = dict(state.get(ticker, {}))
        pending_state = dict(ticker_state)
        notification_failed = False
        for target_type, target_field in (("buy", "buy_target_price"), ("sell", "sell_target_price")):
            target_price = preference[target_field]
            distance_percent = abs(current_price - target_price) / target_price * 100
            is_inside = distance_percent <= preference["threshold_percent"]
            was_inside = bool(ticker_state.get(target_type, False))
            if is_inside and not was_inside:
                alert = {
                    "ticker": ticker,
                    "current_price": current_price,
                    "target_type": target_type,
                    "target_price": target_price,
                    "distance_percent": distance_percent,
                    "threshold_percent": preference["threshold_percent"],
                    "checked_at": quote_time or datetime.now(timezone.utc).isoformat(),
                }
                try:
                    notifier.notify(alert)
                except Exception as error:
                    errors.append(f"Notification failed for {ticker} {target_type}: {error}")
                    notification_failed = True
                    continue
            pending_state[target_type] = is_inside
        # Keep this ticker's prior state transactional so a failed delivery is retried.
        state[ticker] = ticker_state if notification_failed else pending_state

    return state, errors


def main(argv=None, quote_client=None):
    parser = argparse.ArgumentParser(description="Run one stock price notification check")
    parser.add_argument("--preferences", default=str(DEFAULT_PREFERENCES_PATH))
    parser.add_argument("--state", default=str(DEFAULT_ALERT_STATE_PATH))
    args = parser.parse_args(argv)
    try:
        preferences = load_preferences(args.preferences)
        old_state = load_alert_state(args.state)
        new_state, errors = run_monitoring_cycle(
            preferences, quote_client or RobinhoodQuoteClient(), ConsoleNotifier(), old_state
        )
        save_alert_state(new_state, args.state)
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1 if errors else 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
