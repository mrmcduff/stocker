# Stockr

A command line tool for stock analysis that provides:

- Current/most recent stock price
- 30-day trailing volatility
- Detailed options analysis with theoretical prices based on Black-Scholes-Merton model
- Implied volatility comparison

## Installation

```bash
# Clone this repository or download the files
git clone https://github.com/yourusername/stockr.git

# Navigate to the directory
cd stockr

# Install the package in development mode
pip install -e .
```

## Usage

After installation, you can use the tool from anywhere in your command line:

```bash
stockr AAPL
```

Replace `AAPL` with any valid stock ticker symbol.

## Features

- **Current Stock Price**: Fetches the latest price data
- **Volatility Analysis**: Calculates 30-day trailing volatility
- **Options Analysis**: 
  - Finds options with strike prices approximately 10% above/below current price
  - Calculates theoretical prices using Black-Scholes-Merton model
  - Compares market prices with theoretical prices
  - Shows market premium/discount percentage
  - Displays implied volatility and compares with historical volatility

## Requirements

- Python 3.6+
- yfinance
- pandas
- numpy
- scipy

## License

MIT
