from typing import Any, Optional
import re
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("NBP")

NBP_API_BASE = "https://api.nbp.pl/api"
USER_AGENT = "nbp-mcp-server/1.0"

# ISO 8601 date format: YYYY-MM-DD
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def validate_date(date: str) -> Optional[str]:
    """Validate date format (YYYY-MM-DD).

    Args:
        date: Date string to validate or empty string

    Returns:
        Error message if invalid, None if valid or date is empty
    """
    if not date:
        return None

    if not DATE_PATTERN.match(date):
        return f"Invalid date format: '{date}'. Expected YYYY-MM-DD (e.g., 2024-01-15)"

    return None


async def make_nbp_request(url: str) -> Optional[dict[str, Any] | list[dict[str, Any]]]:
    """Make a request to the NBP API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_rate(rate: dict) -> str:
    """Format a currency rate into a readable string."""
    parts = []
    parts.append(f"Currency: {rate.get('currency', 'Unknown')}")
    parts.append(f"Code: {rate.get('code', 'Unknown')}")

    if 'country' in rate:
        parts.append(f"Country: {rate['country']}")
    if 'symbol' in rate:
        parts.append(f"Symbol: {rate['symbol']}")

    if 'mid' in rate:
        parts.append(f"Mid Rate: {rate['mid']}")
    if 'bid' in rate:
        parts.append(f"Bid Rate: {rate['bid']}")
    if 'ask' in rate:
        parts.append(f"Ask Rate: {rate['ask']}")

    return "\n".join(parts)


def format_exchange_table(table: dict) -> str:
    """Format an exchange rate table into a readable string."""
    result = []
    result.append(f"Table: {table.get('table', 'Unknown')}")
    result.append(f"Number: {table.get('no', 'Unknown')}")

    if 'tradingDate' in table:
        result.append(f"Trading Date: {table['tradingDate']}")

    result.append(f"Effective Date: {table.get('effectiveDate', 'Unknown')}")
    result.append("\nRates:")

    rates = table.get('rates', [])
    for rate in rates:
        result.append(f"\n{format_rate(rate)}")

    return "\n".join(result)


def format_gold_price(gold: dict) -> str:
    """Format gold price data into a readable string."""
    return f"Date: {gold.get('data', 'Unknown')}\nPrice: {gold.get('cena', 'Unknown')} PLN/g"


@mcp.tool()
async def get_currency_rate(code: str, date: str = "", table: str = "a") -> str:
    """Get exchange rate for a currency, either current or for a specific date.

    Args:
        code: Three-letter currency code (e.g., USD, EUR, GBP) following ISO 4217
        date: Specific date in YYYY-MM-DD format (ISO 8601). If empty, gets current rate.
        table: Table type - 'a' for average rates, 'b' for other currencies, 'c' for bid/ask rates (default: 'a')
    """
    code = code.upper()
    table = table.lower()

    # Validate table type
    if table not in ['a', 'b', 'c']:
        return "Invalid table type. Use 'a', 'b', or 'c'."

    # Validate date format if provided
    date_error = validate_date(date)
    if date_error:
        return date_error

    # Build URL based on whether date is provided
    if date:
        url = f"{NBP_API_BASE}/exchangerates/rates/{table}/{code}/{date}/"
    else:
        url = f"{NBP_API_BASE}/exchangerates/rates/{table}/{code}/"

    data = await make_nbp_request(url)

    if not data:
        if date:
            return f"Unable to fetch exchange rate for {code} on {date}. The date may be a weekend, holiday, or outside the available data range."
        return f"Unable to fetch current exchange rate for {code} from table {table.upper()}."

    rates = data.get('rates', [])
    if not rates:
        return f"No exchange rate data available for {code}."

    rate_data = rates[0]
    result = [
        f"Currency: {data.get('currency', 'Unknown')}",
        f"Code: {data.get('code', 'Unknown')}",
        f"Table: {data.get('table', 'Unknown').upper()}",
        f"Number: {rate_data.get('no', 'Unknown')}",
        f"Effective Date: {rate_data.get('effectiveDate', 'Unknown')}",
    ]

    if 'tradingDate' in rate_data:
        result.append(f"Trading Date: {rate_data['tradingDate']}")

    if 'mid' in rate_data:
        result.append(f"Mid Rate: {rate_data['mid']} PLN")
    if 'bid' in rate_data:
        result.append(f"Bid Rate: {rate_data['bid']} PLN")
    if 'ask' in rate_data:
        result.append(f"Ask Rate: {rate_data['ask']} PLN")

    return "\n".join(result)


@mcp.tool()
async def get_exchange_table(date: str = "", table: str = "a") -> str:
    """Get exchange rate table, either current or for a specific date.

    Args:
        date: Specific date in YYYY-MM-DD format (ISO 8601). If empty, gets current table.
        table: Table type - 'a' for average rates, 'b' for other currencies, 'c' for bid/ask rates (default: 'a')
    """
    table = table.lower()

    # Validate table type
    if table not in ['a', 'b', 'c']:
        return "Invalid table type. Use 'a', 'b', or 'c'."

    # Validate date format if provided
    date_error = validate_date(date)
    if date_error:
        return date_error

    # Build URL based on whether date is provided
    if date:
        url = f"{NBP_API_BASE}/exchangerates/tables/{table}/{date}/"
    else:
        url = f"{NBP_API_BASE}/exchangerates/tables/{table}/"

    data = await make_nbp_request(url)

    # NBP API returns a list of tables (usually containing one element)
    if not data or not isinstance(data, list) or len(data) == 0:
        if date:
            return f"Unable to fetch exchange rate table {table.upper()} for {date}. The date may be a weekend, holiday, or outside the available data range."
        return f"Unable to fetch current exchange rate table {table.upper()}."

    return format_exchange_table(data[0])


@mcp.tool()
async def get_currency_rate_history(
    code: str,
    start_date: str,
    end_date: str,
    table: str = "a"
) -> str:
    """Get historical exchange rates for a currency within a date range.

    Args:
        code: Three-letter currency code (e.g., USD, EUR, GBP) following ISO 4217
        start_date: Start date in YYYY-MM-DD format (ISO 8601)
        end_date: End date in YYYY-MM-DD format (ISO 8601)
        table: Table type - 'a' for average rates, 'b' for other currencies, 'c' for bid/ask rates (default: 'a')
    """
    code = code.upper()
    table = table.lower()

    if table not in ['a', 'b', 'c']:
        return "Invalid table type. Use 'a', 'b', or 'c'."

    url = f"{NBP_API_BASE}/exchangerates/rates/{table}/{code}/{start_date}/{end_date}/"
    data = await make_nbp_request(url)

    if not data:
        return f"Unable to fetch historical data for {code} from {start_date} to {end_date}."

    rates = data.get('rates', [])
    if not rates:
        return f"No historical data available for {code} in the specified date range."

    result = [
        f"Currency: {data.get('currency', 'Unknown')}",
        f"Code: {data.get('code', 'Unknown')}",
        f"Table: {data.get('table', 'Unknown').upper()}",
        f"\nHistorical Rates ({len(rates)} entries):\n"
    ]

    for rate in rates:
        entry = [f"Date: {rate.get('effectiveDate', 'Unknown')}"]

        if 'tradingDate' in rate:
            entry.append(f"Trading Date: {rate['tradingDate']}")
        if 'mid' in rate:
            entry.append(f"Mid Rate: {rate['mid']} PLN")
        if 'bid' in rate:
            entry.append(f"Bid Rate: {rate['bid']} PLN")
        if 'ask' in rate:
            entry.append(f"Ask Rate: {rate['ask']} PLN")

        result.append(" | ".join(entry))

    return "\n".join(result)


@mcp.tool()
async def get_currency_rate_last_n(code: str, count: int, table: str = "a") -> str:
    """Get last N exchange rates for a currency.

    Args:
        code: Three-letter currency code (e.g., USD, EUR, GBP) following ISO 4217
        count: Number of last rates to retrieve (max 255)
        table: Table type - 'a' for average rates, 'b' for other currencies, 'c' for bid/ask rates (default: 'a')
    """
    code = code.upper()
    table = table.lower()

    if table not in ['a', 'b', 'c']:
        return "Invalid table type. Use 'a', 'b', or 'c'."

    if count < 1 or count > 255:
        return "Count must be between 1 and 255."

    url = f"{NBP_API_BASE}/exchangerates/rates/{table}/{code}/last/{count}/"
    data = await make_nbp_request(url)

    if not data:
        return f"Unable to fetch last {count} rates for {code}."

    rates = data.get('rates', [])
    if not rates:
        return f"No rate data available for {code}."

    result = [
        f"Currency: {data.get('currency', 'Unknown')}",
        f"Code: {data.get('code', 'Unknown')}",
        f"Table: {data.get('table', 'Unknown').upper()}",
        f"\nLast {len(rates)} Rates:\n"
    ]

    for rate in rates:
        entry = [f"Date: {rate.get('effectiveDate', 'Unknown')}"]

        if 'tradingDate' in rate:
            entry.append(f"Trading Date: {rate['tradingDate']}")
        if 'mid' in rate:
            entry.append(f"Mid Rate: {rate['mid']} PLN")
        if 'bid' in rate:
            entry.append(f"Bid Rate: {rate['bid']} PLN")
        if 'ask' in rate:
            entry.append(f"Ask Rate: {rate['ask']} PLN")

        result.append(" | ".join(entry))

    return "\n".join(result)


@mcp.tool()
async def get_gold_price(date: str = "") -> str:
    """Get gold price in PLN per gram, either current or for a specific date.

    Args:
        date: Specific date in YYYY-MM-DD format (ISO 8601). If empty, gets current price.
    """
    # Validate date format if provided
    date_error = validate_date(date)
    if date_error:
        return date_error

    # Build URL based on whether date is provided
    if date:
        url = f"{NBP_API_BASE}/cenyzlota/{date}/"
    else:
        url = f"{NBP_API_BASE}/cenyzlota/"

    data = await make_nbp_request(url)

    if not data or not isinstance(data, list) or len(data) == 0:
        if date:
            return f"Unable to fetch gold price for {date}. The date may be a weekend, holiday, or outside the available data range (data available from 2013-01-02)."
        return "Unable to fetch current gold price."

    gold = data[0]
    return format_gold_price(gold)


@mcp.tool()
async def get_gold_price_history(start_date: str, end_date: str) -> str:
    """Get historical gold prices within a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format (ISO 8601)
        end_date: End date in YYYY-MM-DD format (ISO 8601)
    """
    url = f"{NBP_API_BASE}/cenyzlota/{start_date}/{end_date}/"
    data = await make_nbp_request(url)

    if data is None or not isinstance(data, list):
        return f"Unable to fetch gold price history from {start_date} to {end_date}."

    if len(data) == 0:
        return f"No gold price data available for the specified date range."

    result = [f"Gold Price History ({len(data)} entries):\n"]

    for gold in data:
        result.append(format_gold_price(gold))

    return "\n".join(result)


@mcp.tool()
async def get_gold_price_last_n(count: int) -> str:
    """Get last N gold prices.

    Args:
        count: Number of last gold prices to retrieve (max 255)
    """
    if count < 1 or count > 255:
        return "Count must be between 1 and 255."

    url = f"{NBP_API_BASE}/cenyzlota/last/{count}/"
    data = await make_nbp_request(url)

    if data is None or not isinstance(data, list):
        return f"Unable to fetch last {count} gold prices."

    if len(data) == 0:
        return "No gold price data available."

    result = [f"Last {len(data)} Gold Prices:\n"]

    for gold in data:
        result.append(format_gold_price(gold))

    return "\n".join(result)
