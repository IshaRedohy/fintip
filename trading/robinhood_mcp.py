class RobinhoodMCPConfigurationError(RuntimeError):
    pass


class RobinhoodQuoteClient:
    """Quote-only boundary for the future Robinhood MCP integration."""

    def __init__(self, server_name=None, quote_tool=None):
        self.server_name = server_name
        self.quote_tool = quote_tool

    def get_quotes(self, tickers):
        if not self.server_name or self.quote_tool is None:
            raise RobinhoodMCPConfigurationError(
                "Robinhood quote MCP is not configured. Supply the MCP server name "
                "and a quote-tool adapter matching its schema."
            )
        response = self.quote_tool(list(tickers))
        return normalize_quote_response(response, tickers)


def normalize_quote_response(response, requested_tickers):
    if not isinstance(response, dict):
        raise ValueError("Malformed MCP quote response: expected a mapping")
    normalized = {}
    for requested in requested_tickers:
        ticker = requested.strip().upper()
        raw_quote = response.get(ticker)
        if raw_quote is None:
            continue
        if isinstance(raw_quote, dict):
            price = raw_quote.get("price")
            timestamp = raw_quote.get("timestamp")
        else:
            price = raw_quote
            timestamp = None
        try:
            price = float(price)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Malformed MCP quote response for {ticker}") from error
        if price <= 0:
            raise ValueError(f"Malformed MCP quote response for {ticker}: price must be positive")
        normalized[ticker] = {"price": price, "timestamp": timestamp}
    return normalized
