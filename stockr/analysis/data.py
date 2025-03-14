"""
Data retrieval functions for stock analysis.
"""

def get_stock_data(ticker):
    """
    Retrieve current stock price and historical data for volatility calculation.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        tuple: (current_price, company_name, historical_data)
    """
    # Import dependencies only when needed
    import datetime as dt
    import pandas as pd
    import yfinance as yf

    try:
        # Create a Ticker object
        stock = yf.Ticker(ticker)

        # Get company name
        company_name = stock.info.get('shortName', stock.info.get('longName', ticker))

        # Get the current stock price (or most recent closing price)
        current_price = stock.info.get('regularMarketPrice')
        if current_price is None:
            current_price = stock.history(period='1d')['Close'].iloc[-1]

        # Get historical data - we need more than 30 days to account for non-trading days
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=45)  # Get extra days to ensure we have 30 trading days
        historical_data = stock.history(start=start_date, end=end_date)

        if historical_data.empty:
            raise ValueError(f"No historical data found for ticker '{ticker}'. Please check the ticker symbol.")

        return current_price, company_name, historical_data
    except Exception as e:
        raise Exception(f"Error retrieving stock data: {str(e)}")


def get_risk_free_rate():
    """
    Get current risk-free rate (approximated by 3-month US Treasury yield).

    Returns:
        float: Current risk-free rate as a decimal
    """
    # Import dependencies only when needed
    import yfinance as yf

    try:
        # Use ^IRX ticker (13-week Treasury Bill) as a proxy for risk-free rate
        treasury = yf.Ticker("^IRX")
        current_yield = treasury.info.get('regularMarketPrice')

        # Convert from percentage to decimal
        if current_yield is not None:
            return current_yield / 100
        else:
            # Fallback to a reasonable default if data isn't available
            return 0.05  # 5% as a reasonable default
    except Exception:
        # Fallback to a reasonable default if there's an error
        return 0.05  # 5% as a reasonable default
