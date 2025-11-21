"""Tests for gold price tools."""
import pytest
from unittest.mock import AsyncMock, patch
from src.nbp import (
    get_gold_price,
    get_gold_price_history,
    get_gold_price_last_n,
)


@pytest.mark.asyncio
async def test_get_gold_price_success():
    """Test getting current gold price successfully."""
    mock_response = [
        {
            "data": "2024-01-02",
            "cena": 245.67
        }
    ]

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_gold_price()

    assert "Date: 2024-01-02" in result
    assert "Price: 245.67 PLN/g" in result


@pytest.mark.asyncio
async def test_get_gold_price_api_error():
    """Test getting gold price when API returns error."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_gold_price()

    assert "Unable to fetch current gold price" in result


@pytest.mark.asyncio
async def test_get_gold_price_empty_response():
    """Test getting gold price when API returns empty list."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=[])):
        result = await get_gold_price()

    assert "Unable to fetch current gold price" in result


@pytest.mark.asyncio
async def test_get_gold_price_history_success():
    """Test getting historical gold prices successfully."""
    mock_response = [
        {
            "data": "2024-01-02",
            "cena": 245.67
        },
        {
            "data": "2024-01-03",
            "cena": 246.12
        },
        {
            "data": "2024-01-04",
            "cena": 245.89
        }
    ]

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_gold_price_history("2024-01-02", "2024-01-04")

    assert "Gold Price History (3 entries)" in result
    assert "Date: 2024-01-02" in result
    assert "Price: 245.67 PLN/g" in result
    assert "Date: 2024-01-03" in result
    assert "Price: 246.12 PLN/g" in result
    assert "Date: 2024-01-04" in result
    assert "Price: 245.89 PLN/g" in result


@pytest.mark.asyncio
async def test_get_gold_price_history_api_error():
    """Test getting gold price history when API returns error."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_gold_price_history("2024-01-01", "2024-01-31")

    assert "Unable to fetch gold price history" in result


@pytest.mark.asyncio
async def test_get_gold_price_history_empty_data():
    """Test getting gold price history when no data is available."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=[])):
        result = await get_gold_price_history("2024-01-01", "2024-01-31")

    assert "No gold price data available" in result


@pytest.mark.asyncio
async def test_get_gold_price_last_n_success():
    """Test getting last N gold prices successfully."""
    mock_response = [
        {
            "data": "2024-01-04",
            "cena": 245.89
        },
        {
            "data": "2024-01-03",
            "cena": 246.12
        },
        {
            "data": "2024-01-02",
            "cena": 245.67
        }
    ]

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_gold_price_last_n(3)

    assert "Last 3 Gold Prices" in result
    assert "Date: 2024-01-04" in result
    assert "Price: 245.89 PLN/g" in result
    assert "Date: 2024-01-03" in result
    assert "Date: 2024-01-02" in result


@pytest.mark.asyncio
async def test_get_gold_price_last_n_invalid_count():
    """Test getting last N gold prices with invalid count."""
    result = await get_gold_price_last_n(0)
    assert "Count must be between 1 and 255" in result

    result = await get_gold_price_last_n(256)
    assert "Count must be between 1 and 255" in result

    result = await get_gold_price_last_n(-5)
    assert "Count must be between 1 and 255" in result


@pytest.mark.asyncio
async def test_get_gold_price_last_n_api_error():
    """Test getting last N gold prices when API returns error."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_gold_price_last_n(10)

    assert "Unable to fetch last 10 gold prices" in result


@pytest.mark.asyncio
async def test_get_gold_price_last_n_empty_data():
    """Test getting last N gold prices when no data is available."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=[])):
        result = await get_gold_price_last_n(10)

    assert "No gold price data available" in result


@pytest.mark.asyncio
async def test_get_gold_price_last_n_single_price():
    """Test getting single gold price using last N."""
    mock_response = [
        {
            "data": "2024-01-02",
            "cena": 245.67
        }
    ]

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_gold_price_last_n(1)

    assert "Last 1 Gold Prices" in result
    assert "Date: 2024-01-02" in result
    assert "Price: 245.67 PLN/g" in result


@pytest.mark.asyncio
async def test_get_gold_price_with_date():
    """Test getting gold price for a specific date."""
    mock_response = [
        {
            "data": "2024-01-15",
            "cena": 248.50
        }
    ]

    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=mock_response)):
        result = await get_gold_price(date="2024-01-15")

    assert "Date: 2024-01-15" in result
    assert "Price: 248.5 PLN/g" in result


@pytest.mark.asyncio
async def test_get_gold_price_invalid_date_format():
    """Test getting gold price with invalid date format."""
    result = await get_gold_price(date="01-15-2024")
    assert "Invalid date format" in result
    assert "YYYY-MM-DD" in result

    result = await get_gold_price(date="2024/01/15")
    assert "Invalid date format" in result

    result = await get_gold_price(date="15.01.2024")
    assert "Invalid date format" in result


@pytest.mark.asyncio
async def test_get_gold_price_date_not_found():
    """Test getting gold price when date has no data (weekend/holiday)."""
    with patch("src.nbp.make_nbp_request", new=AsyncMock(return_value=None)):
        result = await get_gold_price(date="2024-01-01")

    assert "Unable to fetch gold price" in result
    assert "2024-01-01" in result
    assert "weekend, holiday" in result
    assert "2013-01-02" in result  # Mentions data availability start date
