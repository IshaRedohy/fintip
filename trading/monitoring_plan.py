REQUIRED_NUMERIC_FIELDS = (
    "buy_target_price",
    "investment_budget",
    "sell_target_price",
    "threshold_percent",
)


def build_monitoring_plan(preferences):
    plan = []
    seen = set()
    for preference in preferences:
        ticker = str(preference.get("ticker", "")).strip().upper()
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        if ticker in seen:
            raise ValueError(f"Duplicate ticker: {ticker}")
        normalized = {"ticker": ticker}
        for field in REQUIRED_NUMERIC_FIELDS:
            try:
                value = float(preference[field])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"{ticker} has an invalid {field}") from error
            if value <= 0:
                raise ValueError(f"{ticker} {field} must be greater than zero")
            normalized[field] = value
        plan.append(normalized)
        seen.add(ticker)
    return plan
