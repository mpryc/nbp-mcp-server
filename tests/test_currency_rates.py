"""Tests for currency rate tools."""
import pytest
from unittest.mock import AsyncMock, patch
from src.nbp import (
    get_currency_rate,
    get_exchange_table,
    get_currency_rate_history,
    get_currency_rate_last_n,
)


@pytest.mark.asyncio
async def test_get_currency_rate_success():
    """Test getting current currency rate successfully."""
    mock_response = {
        "table": "A",
        "currency": "dolar amerykański",
        "code": "USD",
        "rates": [
            {
                "no": "001/A/NBP/2024",
                "effectiveDate": "2024-01-02",
                "mid": 3.9876
            }
        ]
    }

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_currency_rate("USD", "a")

    assert "Currency: dolar amerykański" in result
    assert "Code: USD" in result
    assert "Table: A" in result
    assert "Number: 001/A/NBP/2024" in result
    assert "Mid Rate: 3.9876 PLN" in result
    assert "Effective Date: 2024-01-02" in result


@pytest.mark.asyncio
async def test_get_currency_rate_table_c():
    """Test getting currency rate from table C with bid/ask rates."""
    mock_response = {
        "table": "C",
        "currency": "dolar amerykański",
        "code": "USD",
        "rates": [
            {
                "no": "001/C/NBP/2024",
                "effectiveDate": "2024-01-02",
                "tradingDate": "2024-01-02",
                "bid": 3.9500,
                "ask": 4.0250
            }
        ]
    }

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_currency_rate("USD", "c")

    assert "Currency: dolar amerykański" in result
    assert "Number: 001/C/NBP/2024" in result
    assert "Bid Rate: 3.95 PLN" in result
    assert "Ask Rate: 4.025 PLN" in result
    assert "Trading Date: 2024-01-02" in result


@pytest.mark.asyncio
async def test_get_currency_rate_invalid_table():
    """Test getting currency rate with invalid table type."""
    result = await get_currency_rate("USD", "x")
    assert "Invalid table type" in result


@pytest.mark.asyncio
async def test_get_currency_rate_api_error():
    """Test getting currency rate when API returns error."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_currency_rate("USD", "a")

    assert "Unable to fetch exchange rate" in result


@pytest.mark.asyncio
async def test_get_currency_rate_no_rates():
    """Test getting currency rate when no rates are available."""
    mock_response = {
        "table": "A",
        "currency": "dolar amerykański",
        "code": "USD",
        "rates": []
    }

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_currency_rate("USD", "a")

    assert "No exchange rate data available" in result


@pytest.mark.asyncio
async def test_get_exchange_table_success():
    """Test getting complete exchange table successfully."""
    mock_response = [
        {
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
    ]

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_exchange_table("a")

    assert "Table: A" in result
    assert "Number: 001/A/NBP/2024" in result
    assert "Effective Date: 2024-01-02" in result
    assert "Currency: dolar amerykański" in result
    assert "Currency: euro" in result


@pytest.mark.asyncio
async def test_get_exchange_table_invalid_type():
    """Test getting exchange table with invalid table type."""
    result = await get_exchange_table("z")
    assert "Invalid table type" in result


@pytest.mark.asyncio
async def test_get_exchange_table_api_error():
    """Test getting exchange table when API returns error."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_exchange_table("a")

    assert "Unable to fetch exchange rate table" in result


@pytest.mark.asyncio
async def test_get_currency_rate_history_success():
    """Test getting historical currency rates successfully."""
    mock_response = {
        "table": "A",
        "currency": "dolar amerykański",
        "code": "USD",
        "rates": [
            {
                "effectiveDate": "2024-01-02",
                "mid": 3.9876
            },
            {
                "effectiveDate": "2024-01-03",
                "mid": 3.9912
            },
            {
                "effectiveDate": "2024-01-04",
                "mid": 3.9850
            }
        ]
    }

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_currency_rate_history("USD", "2024-01-02", "2024-01-04", "a")

    assert "Historical Rates (3 entries)" in result
    assert "Date: 2024-01-02" in result
    assert "Mid Rate: 3.9876 PLN" in result
    assert "Date: 2024-01-03" in result
    assert "Date: 2024-01-04" in result


@pytest.mark.asyncio
async def test_get_currency_rate_history_invalid_table():
    """Test getting historical rates with invalid table type."""
    result = await get_currency_rate_history("USD", "2024-01-01", "2024-01-31", "d")
    assert "Invalid table type" in result


@pytest.mark.asyncio
async def test_get_currency_rate_history_api_error():
    """Test getting historical rates when API returns error."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_currency_rate_history("USD", "2024-01-01", "2024-01-31", "a")

    assert "Unable to fetch historical data" in result


@pytest.mark.asyncio
async def test_get_currency_rate_last_n_success():
    """Test getting last N currency rates successfully."""
    mock_response = {
        "table": "A",
        "currency": "euro",
        "code": "EUR",
        "rates": [
            {
                "effectiveDate": "2024-01-02",
                "mid": 4.3215
            },
            {
                "effectiveDate": "2024-01-03",
                "mid": 4.3198
            },
            {
                "effectiveDate": "2024-01-04",
                "mid": 4.3250
            }
        ]
    }

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_currency_rate_last_n("EUR", 3, "a")

    assert "Last 3 Rates" in result
    assert "Currency: euro" in result
    assert "Date: 2024-01-02" in result
    assert "Mid Rate: 4.3215 PLN" in result


@pytest.mark.asyncio
async def test_get_currency_rate_last_n_invalid_count():
    """Test getting last N rates with invalid count."""
    result = await get_currency_rate_last_n("USD", 0, "a")
    assert "Count must be between 1 and 255" in result

    result = await get_currency_rate_last_n("USD", 256, "a")
    assert "Count must be between 1 and 255" in result


@pytest.mark.asyncio
async def test_get_currency_rate_last_n_invalid_table():
    """Test getting last N rates with invalid table type."""
    result = await get_currency_rate_last_n("USD", 10, "e")
    assert "Invalid table type" in result


@pytest.mark.asyncio
async def test_get_currency_rate_last_n_api_error():
    """Test getting last N rates when API returns error."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_currency_rate_last_n("USD", 10, "a")

    assert "Unable to fetch last 10 rates" in result


@pytest.mark.asyncio
async def test_currency_code_case_insensitive():
    """Test that currency codes are case-insensitive."""
    mock_response = {
        "table": "A",
        "currency": "dolar amerykański",
        "code": "USD",
        "rates": [{"effectiveDate": "2024-01-02", "mid": 3.9876}]
    }

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result_lower = await get_currency_rate("usd", "a")
        result_upper = await get_currency_rate("USD", "a")
        result_mixed = await get_currency_rate("UsD", "a")

    assert "Currency: dolar amerykański" in result_lower
    assert "Currency: dolar amerykański" in result_upper
    assert "Currency: dolar amerykański" in result_mixed
