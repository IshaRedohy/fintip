from trading.order_plan import format_order_plan


def submit_order_plan(order_plan, dry_run=True):
    if dry_run:
        print("Dry run only. No Robinhood orders were placed.")
        print("Proposed orders:")
        print(format_order_plan(order_plan))
        return {
            "dry_run": True,
            "submitted": False,
            "orders": order_plan,
        }

    raise NotImplementedError("Live Robinhood MCP order submission is not implemented yet.")
