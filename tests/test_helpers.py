"""Tests for helper functions."""
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from src.nbp import (
    make_nbp_request,
    format_rate,
    format_exchange_table,
    format_gold_price,
)


@pytest.mark.asyncio
async def test_make_nbp_request_success():
    """Test making successful NBP API request."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"test": "data"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        result = await make_nbp_request("https://api.nbp.pl/api/test")

    assert result == {"test": "data"}
    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args
    assert call_args[0][0] == "https://api.nbp.pl/api/test"
    assert call_args[1]["headers"]["User-Agent"] == "nbp-mcp-server/1.0"
    assert call_args[1]["headers"]["Accept"] == "application/json"


@pytest.mark.asyncio
async def test_make_nbp_request_http_error():
    """Test making NBP API request with HTTP error."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=MagicMock()
    )

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        result = await make_nbp_request("https://api.nbp.pl/api/test")

    assert result is None


@pytest.mark.asyncio
async def test_make_nbp_request_timeout():
    """Test making NBP API request with timeout."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Timeout")

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        result = await make_nbp_request("https://api.nbp.pl/api/test")

    assert result is None


@pytest.mark.asyncio
async def test_make_nbp_request_network_error():
    """Test making NBP API request with network error."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.NetworkError("Network error")

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_async_client.return_value.__aenter__.return_value = mock_client

        result = await make_nbp_request("https://api.nbp.pl/api/test")

    assert result is None


def test_format_rate_with_mid():
    """Test formatting rate with mid value."""
    rate = {
        "currency": "dolar amerykański",
        "code": "USD",
        "mid": 3.9876
    }

    result = format_rate(rate)

    assert "Currency: dolar amerykański" in result
    assert "Code: USD" in result
    assert "Mid Rate: 3.9876" in result
    assert "Bid Rate" not in result
    assert "Ask Rate" not in result


def test_format_rate_with_bid_ask():
    """Test formatting rate with bid and ask values."""
    rate = {
        "currency": "euro",
        "code": "EUR",
        "bid": 4.3000,
        "ask": 4.3900
    }

    result = format_rate(rate)

    assert "Currency: euro" in result
    assert "Code: EUR" in result
    assert "Bid Rate: 4.3" in result
    assert "Ask Rate: 4.39" in result
    assert "Mid Rate" not in result


def test_format_rate_all_fields():
    """Test formatting rate with all possible fields."""
    rate = {
        "currency": "funt szterling",
        "code": "GBP",
        "mid": 5.1234,
        "bid": 5.1000,
        "ask": 5.2000
    }

    result = format_rate(rate)

    assert "Currency: funt szterling" in result
    assert "Code: GBP" in result
    assert "Mid Rate: 5.1234" in result
    assert "Bid Rate: 5.1" in result
    assert "Ask Rate: 5.2" in result


def test_format_rate_missing_fields():
    """Test formatting rate with missing fields."""
    rate = {}

    result = format_rate(rate)

    assert "Currency: Unknown" in result
    assert "Code: Unknown" in result


def test_format_rate_with_country():
    """Test formatting rate with country field."""
    rate = {
        "currency": "dolar amerykański",
        "code": "USD",
        "country": "Stany Zjednoczone",
        "mid": 3.9876
    }

    result = format_rate(rate)

    assert "Currency: dolar amerykański" in result
    assert "Code: USD" in result
    assert "Country: Stany Zjednoczone" in result
    assert "Mid Rate: 3.9876" in result


def test_format_rate_with_symbol():
    """Test formatting rate with symbol field (for archived rates)."""
    rate = {
        "currency": "dolar amerykański",
        "code": "USD",
        "symbol": "840",
        "mid": 3.9876
    }

    result = format_rate(rate)

    assert "Currency: dolar amerykański" in result
    assert "Code: USD" in result
    assert "Symbol: 840" in result
    assert "Mid Rate: 3.9876" in result


def test_format_rate_with_country_and_symbol():
    """Test formatting rate with both country and symbol fields."""
    rate = {
        "currency": "dolar amerykański",
        "code": "USD",
        "country": "Stany Zjednoczone",
        "symbol": "840",
        "mid": 3.9876
    }

    result = format_rate(rate)

    assert "Currency: dolar amerykański" in result
    assert "Code: USD" in result
    assert "Country: Stany Zjednoczone" in result
    assert "Symbol: 840" in result
    assert "Mid Rate: 3.9876" in result


def test_format_exchange_table_table_a():
    """Test formatting exchange table type A."""
    table = {
        "table": "A",
        "no": "001/A/NBP/2024",
        "effectiveDate": "2024-01-02",
        "rates": [
            {
                "currency": "dolar amerykański",
                "code": "USD",
                "mid": 3.9876
            },
            {
                "currency": "euro",
                "code": "EUR",
                "mid": 4.3215
            }
        ]
    }

    result = format_exchange_table(table)

    assert "Table: A" in result
    assert "Number: 001/A/NBP/2024" in result
    assert "Effective Date: 2024-01-02" in result
    assert "Currency: dolar amerykański" in result
    assert "Code: USD" in result
    assert "Mid Rate: 3.9876" in result
    assert "Currency: euro" in result
    assert "Code: EUR" in result
    assert "Mid Rate: 4.3215" in result


def test_format_exchange_table_table_c():
    """Test formatting exchange table type C with trading date."""
    table = {
        "table": "C",
        "no": "001/C/NBP/2024",
        "tradingDate": "2024-01-02",
        "effectiveDate": "2024-01-03",
        "rates": [
            {
                "currency": "dolar amerykański",
                "code": "USD",
                "bid": 3.9500,
                "ask": 4.0250
            }
        ]
    }

    result = format_exchange_table(table)

    assert "Table: C" in result
    assert "Number: 001/C/NBP/2024" in result
    assert "Trading Date: 2024-01-02" in result
    assert "Effective Date: 2024-01-03" in result
    assert "Bid Rate: 3.95" in result
    assert "Ask Rate: 4.025" in result


def test_format_exchange_table_empty_rates():
    """Test formatting exchange table with empty rates."""
    table = {
        "table": "A",
        "no": "001/A/NBP/2024",
        "effectiveDate": "2024-01-02",
        "rates": []
    }

    result = format_exchange_table(table)

    assert "Table: A" in result
    assert "Number: 001/A/NBP/2024" in result
    assert "Effective Date: 2024-01-02" in result
    assert "Rates:" in result


def test_format_exchange_table_missing_fields():
    """Test formatting exchange table with missing fields."""
    table = {
        "rates": []
    }

    result = format_exchange_table(table)

    assert "Table: Unknown" in result
    assert "Number: Unknown" in result
    assert "Effective Date: Unknown" in result


def test_format_gold_price():
    """Test formatting gold price data."""
    gold = {
        "data": "2024-01-02",
        "cena": 245.67
    }

    result = format_gold_price(gold)

    assert "Date: 2024-01-02" in result
    assert "Price: 245.67 PLN/g" in result


def test_format_gold_price_missing_fields():
    """Test formatting gold price with missing fields."""
    gold = {}

    result = format_gold_price(gold)

    assert "Date: Unknown" in result
    assert "Price: Unknown PLN/g" in result


def test_format_gold_price_high_precision():
    """Test formatting gold price with high precision number."""
    gold = {
        "data": "2024-01-02",
        "cena": 245.6789
    }

    result = format_gold_price(gold)

    assert "Date: 2024-01-02" in result
    assert "Price: 245.6789 PLN/g" in result
