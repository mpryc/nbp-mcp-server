# NBP MCP Server

A Model Context Protocol (MCP) server for accessing Polish National Bank (NBP) data, including currency exchange rates and gold prices.

## Features

This server provides access to the NBP public API with the following capabilities:

### Currency Exchange Rates
- Get current exchange rates for any currency
- Retrieve complete exchange rate tables (A, B, or C)
- Query historical exchange rates for specific date ranges
- Get last N exchange rates for trend analysis

### Gold Prices
- Get current gold price (PLN per gram)
- Retrieve historical gold prices
- Query last N gold price quotations

### Table Types
- **Table A**: Average exchange rates of foreign currencies (updated daily)
- **Table B**: Average exchange rates of other currencies (updated weekly)
- **Table C**: Bid and ask rates for currencies (updated daily)

## Installation

### Create new project

```shell
uv init nbp-mcp-server
cd nbp-mcp-server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Add dependencies

```shell
uv add "mcp[cli]" httpx
```

## Configuration

### Claude Desktop

Add this to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nbp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/nbp-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

### Other MCP Clients

For other MCP clients that support stdio transport, configure them to run:

```shell
uv --directory /path/to/nbp-mcp-server run main.py
```

### n8n (HTTP Transport)

For n8n integration, use the HTTP Streamable transport with Docker:

#### Docker Compose Configuration

```yaml
nbp-mcp-server:
  image: quay.io/migi/nbp-mcp-server:1.0.0
  hostname: nbp
  container_name: nbp-mcp-server
  networks: ['mynetwork']
  ports:
    - 8000:8000
  environment:
    - PYTHONUNBUFFERED=1
  restart: unless-stopped
```

#### n8n MCP Client Tool Node Setup

Configure the MCP Client Tool node in n8n:

- **URL**: `http://nbp:8000/mcp`
- **Server Transport**: HTTP Streamable

#### Sample AI Prompt for n8n

```
Ile kosztowało EURO 15 lutego 2022 roku.

# Rules
- The date which is going in the tool needs to be in a format YYYY-MM-DD
- Always use available MCP NBP tool to query for exchange rate.
- When asking for week of the year you need to use some external knowledge to get the dates
- If no data is returned you need to query the range at least 7 days prior to the given date and choose the closest one. This is because public holidays do not contain data.

# Output
- Always respond in pure JSON without any additional text or formatting.
- Always give ONLY one rate as a number without anything else
- Example output {'convertion': '4.2566'}
- If there is some problem simply give back {'conversion': 'n/a'}
```

## Available Tools

### 1. get_currency_rate

Get the current exchange rate for a specific currency.

**Parameters:**
- `code` (required): Three-letter currency code (e.g., USD, EUR, GBP) - ISO 4217
- `table` (optional): Table type - 'a', 'b', or 'c' (default: 'a')

**Example:**
```
Get current USD exchange rate from table A
Get EUR bid/ask rates (table C)
```

### 2. get_exchange_table

Get a complete exchange rate table with all currencies.

**Parameters:**
- `table` (optional): Table type - 'a', 'b', or 'c' (default: 'a')

**Example:**
```
Get the current table A with all exchange rates
Get table C with all bid/ask rates
```

### 3. get_currency_rate_history

Get historical exchange rates for a currency within a date range.

**Parameters:**
- `code` (required): Three-letter currency code (ISO 4217)
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `table` (optional): Table type - 'a', 'b', or 'c' (default: 'a')

**Note:** Date range cannot exceed 93 days.

**Example:**
```
Get USD rates from 2024-01-01 to 2024-01-31
Get EUR historical data for the last month
```

### 4. get_currency_rate_last_n

Get the last N exchange rates for a currency.

**Parameters:**
- `code` (required): Three-letter currency code (ISO 4217)
- `count` (required): Number of rates to retrieve (1-255)
- `table` (optional): Table type - 'a', 'b', or 'c' (default: 'a')

**Example:**
```
Get last 10 USD exchange rates
Get last 30 GBP rates from table C
```

### 5. get_gold_price

Get the current gold price in PLN per gram.

**Parameters:** None

**Example:**
```
What is the current gold price?
Get today's gold price
```

### 6. get_gold_price_history

Get historical gold prices within a date range.

**Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format

**Note:** Date range cannot exceed 93 days. Gold price data is available from January 2, 2013.

**Example:**
```
Get gold prices from 2024-01-01 to 2024-01-31
Show me gold price history for last month
```

### 7. get_gold_price_last_n

Get the last N gold price quotations.

**Parameters:**
- `count` (required): Number of prices to retrieve (1-255)

**Example:**
```
Get last 10 gold prices
Show me the last 30 gold quotations
```

## Usage Examples

Once configured in Claude Desktop or another MCP client, you can ask:

- "What's the current USD to PLN exchange rate?"
- "Show me the last 30 days of EUR exchange rates"
- "Get the complete table A with all current exchange rates"
- "What was the gold price on 2024-01-15?"
- "Compare USD rates between table A and table C"
- "Show me GBP exchange rate trends for the last 10 days"

## Data Sources

All data is sourced from the official NBP (Narodowy Bank Polski) API:
- API Documentation: https://api.nbp.pl/
- Exchange rate data available from: January 2, 2002
- Gold price data available from: January 2, 2013

## Development

### Running Locally

```shell
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the server
python main.py
```

### Testing

The project includes comprehensive test coverage for all functionality.

#### Installing Test Dependencies

```shell
# Install development dependencies including pytest
uv pip install -e ".[dev]"
```

#### Running Tests

```shell
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Run tests with HTML coverage report
pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in your browser

# Run specific test file
pytest tests/test_currency_rates.py

# Run specific test function
pytest tests/test_currency_rates.py::test_get_currency_rate_success

# Run tests matching a pattern
pytest -k "currency"
```

#### Test Structure

The test suite is organized as follows:

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_currency_rates.py   # Tests for currency exchange rate tools
├── test_gold_prices.py      # Tests for gold price tools
└── test_helpers.py          # Tests for helper functions
```

#### Test Coverage

The tests cover:

**Currency Rate Tools:**
- Getting current exchange rates (tables A, B, C)
- Retrieving complete exchange rate tables
- Querying historical rates by date range
- Getting last N exchange rates
- Input validation (invalid table types, counts)
- Error handling (API errors, network issues)
- Case-insensitive currency codes

**Gold Price Tools:**
- Getting current gold price
- Retrieving historical gold prices
- Getting last N gold prices
- Input validation
- Error handling

**Helper Functions:**
- API request handling with proper headers
- HTTP error handling (404, timeouts, network errors)
- Data formatting for rates, tables, and gold prices
- Edge cases (missing fields, empty responses)

#### Continuous Testing

For development, you can use pytest-watch to automatically run tests when files change:

```shell
# Install pytest-watch
uv pip install pytest-watch

# Run tests in watch mode
ptw
```

### Testing with MCP Inspector

#### Option 1: Using stdio transport (Recommended)

```shell
npx @modelcontextprotocol/inspector uv --directory /FULL/PATH/to/nbp-mcp-server run main.py
```

This uses the default stdio transport, which the inspector can communicate with directly.

#### Option 2: Using streamable-http transport

If you want to test the HTTP transport specifically, you need to run the server and inspector separately:

**Terminal 1** - Start the server:
```shell
cd /path/to/nbp-mcp-server
uv run main.py --transport streamable-http
```

**Terminal 2** - Connect the inspector to the running server:
```shell
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

**Important:** The MCP endpoint is at `/mcp`, not at the root path.

By default, the server listens on `0.0.0.0:8000`. You can customize this:

```shell
uv run main.py --transport streamable-http --host 127.0.0.1 --port 3000
```

Then connect to `http://localhost:3000/mcp`

## License

This project is under the Apache License, Version 2.0, however uses api calls to gather data from the NBP public API.
Please refer to NBP's terms of service for data usage guidelines.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
