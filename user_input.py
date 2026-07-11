import csv
from pathlib import Path

from trading.monitoring_plan import build_monitoring_plan
from trading.preferences import DEFAULT_PREFERENCES_PATH, save_preferences


NASDAQ_DIRECTORY = Path(__file__).with_name("nasdaq_100_directory.csv")


def read_nasdaq_directory():
    with NASDAQ_DIRECTORY.open(newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def find_ticker(rows, stock):
    target = stock.strip().lower()
    for row in rows:
        if row["ticker"].strip().lower() == target:
            return row["ticker"].strip().upper()
        if row["company"].strip().lower() == target:
            return row["ticker"].strip().upper()
    return None


def validate_stock(stock):
    return find_ticker(read_nasdaq_directory(), stock) is not None


def parse_stock_input(stock_input):
    if "," in stock_input:
        return [stock.strip() for stock in stock_input.split(",") if stock.strip()]
    stock_input = stock_input.strip()
    if validate_stock(stock_input):
        return [stock_input]
    return [stock.strip() for stock in stock_input.split() if stock.strip()]


def get_stocks():
    rows = read_nasdaq_directory()
    while True:
        entered = parse_stock_input(input("Stocks to monitor: "))
        normalized = [find_ticker(rows, stock) for stock in entered]
        invalid = [stock for stock, ticker in zip(entered, normalized) if ticker is None]
        if entered and not invalid:
            return list(dict.fromkeys(normalized))
        print("Unsupported stock(s):", ", ".join(invalid) if invalid else "none entered")


def get_positive_number(prompt, default=None):
    while True:
        raw_value = input(prompt).strip()
        if not raw_value and default is not None:
            return float(default)
        try:
            value = float(raw_value)
            if value > 0:
                return value
        except ValueError:
            pass
        print("Please enter a number greater than zero.")


def collect_user_responses():
    preferences = []
    for ticker in get_stocks():
        preferences.append(
            {
                "ticker": ticker,
                "buy_target_price": get_positive_number(f"{ticker} buy target: $"),
                "investment_budget": get_positive_number(f"{ticker} investment budget: $"),
                "sell_target_price": get_positive_number(f"{ticker} sell target: $"),
                "threshold_percent": get_positive_number(
                    f"{ticker} alert threshold percent [5]: ", default=5
                ),
            }
        )
    return preferences


def main():
    plan = build_monitoring_plan(collect_user_responses())
    save_preferences(plan, DEFAULT_PREFERENCES_PATH)
    print(f"Saved {len(plan)} ticker preference(s) to {DEFAULT_PREFERENCES_PATH}.")
    print("No trades were placed.")


if __name__ == "__main__":
    main()
