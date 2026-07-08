import csv
from pathlib import Path


NASDAQ_DIRECTORY = Path(__file__).with_name("nasdaq_100_directory.csv")
VALID_STIP_TYPES = ("sell-price", "profit", "profit-percentage")
STIP_TYPE_OPTIONS = {
    "a": "sell-price",
    "b": "profit",
    "c": "profit-percentage",
    "sell-price": "sell-price",
    "profit": "profit",
    "profit-percentage": "profit-percentage",
}


def read_nasdaq_directory():
    with NASDAQ_DIRECTORY.open(newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def ticker_exists(rows, stock):
    target = stock.strip().lower()
    left = 0
    right = len(rows) - 1

    while left <= right:
        middle = (left + right) // 2
        ticker = rows[middle]["ticker"].strip().lower()

        if ticker == target:
            return True
        if ticker < target:
            left = middle + 1
        else:
            right = middle - 1

    return False


def validate_stock(stock):
    rows = read_nasdaq_directory()

    if ticker_exists(rows, stock):
        return True

    target = stock.strip().lower()
    for row in rows:
        if row["company"].strip().lower() == target:
            return True

    return False


def parse_stock_input(stock_input):
    if "," in stock_input:
        return [stock.strip() for stock in stock_input.split(",") if stock.strip()]

    stock_input = stock_input.strip()
    if validate_stock(stock_input):
        return [stock_input]

    return [stock.strip() for stock in stock_input.split() if stock.strip()]


def get_stocks():
    stocks = []

    while True:
        stock_input = input("What stocks would you like to invest in? ")
        entered_stocks = parse_stock_input(stock_input)

        if not entered_stocks:
            print("Please enter at least one stock.")
            continue

        invalid_stocks = []

        for stock in entered_stocks:
            normalized_stock = stock.lower()

            if validate_stock(stock):
                if normalized_stock not in stocks:
                    stocks.append(normalized_stock)
            else:
                invalid_stocks.append(stock)

        if not invalid_stocks:
            return stocks

        print("Invalid stock input:", ", ".join(invalid_stocks))
        print("Please enter a valid stock. Previously entered valid stocks were kept.")


def get_number(prompt):
    while True:
        value = input(prompt)

        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def get_btip(stocks):
    btip = {}

    for stock in stocks:
        btip[stock] = get_number(f"Enter btip for {stock}: ")

    return btip


def explain_stip_types():
    print("Before entering stip values, here is what each representation means:")
    print('"sell-price" - At what price you wish to sell your shares')
    print('"profit" - How much profit you want to make from this purchase')
    print('"profit-percentage" - At what percentage of profit you wish to sell your shares')


def get_stip_type(stock):
    while True:
        stip_type = input(
            f"Enter stip representation for {stock} "
            "(a. sell-price, b. profit, c. profit-percentage): "
        ).strip().lower()

        if stip_type in STIP_TYPE_OPTIONS:
            return STIP_TYPE_OPTIONS[stip_type]

        print("Please enter a, b, c, sell-price, profit, or profit-percentage.")


def get_stip(stocks):
    stip = {}

    explain_stip_types()

    for stock in stocks:
        value = get_number(f"Enter stip number for {stock}: ")
        representation = get_stip_type(stock)
        stip[stock] = {
            "value": value,
            "representation": representation,
        }

    return stip


stocks = get_stocks()
btip = get_btip(stocks)
stip = get_stip(stocks)

print("stocks =", stocks)
print("btip =", btip)
print("stip =", stip)
