"""
Volatility calculation functions.
"""


def calculate_volatility(historical_data, trading_days=30):
    """
    Calculate the trailing volatility based on the last N trading days.

    Args:
        historical_data (pd.DataFrame): Historical price data
        trading_days (int): Number of trading days to use for calculation

    Returns:
        float: Annualized volatility as a percentage
    """
    # Import dependencies only when needed
    import math
    import numpy as np

    # Ensure we have enough data
    if len(historical_data) < trading_days:
        print(
            f"Warning: Only {len(historical_data)} trading days available, using all available data"
        )
        trading_days = len(historical_data)

    # Calculate daily returns
    closing_prices = historical_data["Close"].tail(trading_days)
    daily_returns = closing_prices.pct_change().dropna()

    # Calculate standard deviation of daily returns
    daily_std = daily_returns.std()

    # Annualize the volatility (multiply by sqrt of trading days in a year)
    # Standard financial practice assumes 252 trading days in a year
    annualized_volatility = daily_std * math.sqrt(252)

    # Convert to percentage
    return annualized_volatility * 100
