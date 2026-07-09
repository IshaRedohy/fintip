def build_order_plan(user_responses):
    orders = []

    for ticker in user_responses["stocks"]:
        orders.append(
            {
                "ticker": ticker.upper(),
                "buy_amount": user_responses["btip"][ticker],
                "sell_target": user_responses["stip"][ticker],
            }
        )

    return orders


def format_order_plan(order_plan):
    if not order_plan:
        return "No orders proposed."

    lines = []

    for order in order_plan:
        sell_target = order["sell_target"]
        lines.append(
            "- {ticker}: buy ${buy_amount:.2f}; sell target {value:g} ({representation})".format(
                ticker=order["ticker"],
                buy_amount=order["buy_amount"],
                value=sell_target["value"],
                representation=sell_target["representation"],
            )
        )

    return "\n".join(lines)
