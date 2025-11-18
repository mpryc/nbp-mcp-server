"""Pytest configuration and fixtures for NBP MCP Server tests."""
import pytest


@pytest.fixture
def sample_currency_rate_response():
    """Sample currency rate response from NBP API."""
    return {
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


@pytest.fixture
def sample_exchange_table_response():
    """Sample exchange table response from NBP API."""
    return [
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


@pytest.fixture
def sample_gold_price_response():
    """Sample gold price response from NBP API."""
    return [
        {
            "data": "2024-01-02",
            "cena": 245.67
        }
    ]


@pytest.fixture
def sample_table_c_response():
    """Sample table C (bid/ask) response from NBP API."""
    return {
        "table": "C",
        "currency": "dolar amerykański",
        "code": "USD",
        "rates": [
            {
                "no": "001/C/NBP/2024",
                "effectiveDate": "2024-01-03",
                "tradingDate": "2024-01-02",
                "bid": 3.9500,
                "ask": 4.0250
            }
        ]
    }


@pytest.fixture
def sample_historical_rates():
    """Sample historical rates response from NBP API."""
    return {
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
