from trading.order_plan import build_order_plan, format_order_plan
from trading.robinhood_mcp import submit_order_plan


def test_build_order_plan_from_user_responses():
    user_responses = {
        "stocks": ["aapl", "msft"],
        "btip": {
            "aapl": 100.0,
            "msft": 50.0,
        },
        "stip": {
            "aapl": {
                "value": 10.0,
                "representation": "profit-percentage",
            },
            "msft": {
                "value": 500.0,
                "representation": "sell-price",
            },
        },
    }

    assert build_order_plan(user_responses) == [
        {
            "ticker": "AAPL",
            "buy_amount": 100.0,
            "sell_target": {
                "value": 10.0,
                "representation": "profit-percentage",
            },
        },
        {
            "ticker": "MSFT",
            "buy_amount": 50.0,
            "sell_target": {
                "value": 500.0,
                "representation": "sell-price",
            },
        },
    ]


def test_format_order_plan():
    order_plan = [
        {
            "ticker": "AAPL",
            "buy_amount": 100.0,
            "sell_target": {
                "value": 10.0,
                "representation": "profit-percentage",
            },
        }
    ]

    assert format_order_plan(order_plan) == (
        "- AAPL: buy $100.00; sell target 10 (profit-percentage)"
    )


def test_submit_order_plan_dry_run_does_not_submit():
    order_plan = [
        {
            "ticker": "AAPL",
            "buy_amount": 100.0,
            "sell_target": {
                "value": 10.0,
                "representation": "profit-percentage",
            },
        }
    ]

    result = submit_order_plan(order_plan, dry_run=True)

    assert result == {
        "dry_run": True,
        "submitted": False,
        "orders": order_plan,
    }
