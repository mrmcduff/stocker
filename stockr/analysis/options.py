"""
Options data retrieval and analysis.
"""

from stockr.analysis.data import get_risk_free_rate
from stockr.models.black_scholes import black_scholes_merton

def get_options_data(ticker, current_price, annual_volatility):
    """
    Get options pricing for strike prices 10% above and below the current price.
    Also calculate theoretical prices using Black-Scholes-Merton model.

    Args:
        ticker (str): Stock ticker symbol
        current_price (float): Current stock price
        annual_volatility (float): 30-day trailing volatility (annualized)

    Returns:
        tuple: (call_option, put_option) - Dictionary with options data
    """
    # Import dependencies only when needed
    import datetime as dt
    import yfinance as yf

    try:
        stock = yf.Ticker(ticker)

        # Calculate target strike prices (10% above and below)
        call_strike_target = current_price * 1.10
        put_strike_target = current_price * 0.90

        # Get expiration dates
        expirations = stock.options

        if not expirations:
            raise ValueError(f"No options data available for ticker '{ticker}'.")

        # Choose an expiration date approximately 30-45 days out
        # This is a common timeframe for options trading (balances time decay and premium)
        today = dt.datetime.now().date()
        target_days = 30
        selected_expiration = None

        for exp in expirations:
            exp_date = dt.datetime.strptime(exp, '%Y-%m-%d').date()
            days_to_expiration = (exp_date - today).days
            if days_to_expiration >= target_days:
                selected_expiration = exp
                break

        # If no expiration is at least 30 days out, take the furthest available
        if selected_expiration is None and expirations:
            selected_expiration = expirations[-1]

        # Get the options chain for the selected expiration
        options = stock.option_chain(selected_expiration)

        # Find the closest strike prices to our targets
        calls_df = options.calls
        puts_df = options.puts

        if calls_df.empty or puts_df.empty:
            raise ValueError(f"Insufficient options data for ticker '{ticker}'.")

        # Find closest call strike
        calls_df['strike_diff'] = abs(calls_df['strike'] - call_strike_target)
        closest_call = calls_df.loc[calls_df['strike_diff'].idxmin()]

        # Find closest put strike
        puts_df['strike_diff'] = abs(puts_df['strike'] - put_strike_target)
        closest_put = puts_df.loc[puts_df['strike_diff'].idxmin()]

        # Calculate days to expiration
        exp_date = dt.datetime.strptime(selected_expiration, '%Y-%m-%d').date()
        days_to_expiration = (exp_date - today).days

        # Get risk-free rate
        risk_free_rate = get_risk_free_rate()

        # Calculate time to expiration in years
        T = days_to_expiration / 365.0

        # Calculate theoretical prices using Black-Scholes-Merton model
        bsm_call_price = black_scholes_merton(
            S=current_price,
            K=closest_call['strike'],
            T=T,
            r=risk_free_rate,
            sigma=annual_volatility,
            option_type='call'
        )

        bsm_put_price = black_scholes_merton(
            S=current_price,
            K=closest_put['strike'],
            T=T,
            r=risk_free_rate,
            sigma=annual_volatility,
            option_type='put'
        )

        # Create dictionaries with the relevant info
        call_option = {
            'strike': closest_call['strike'],
            'market_price': closest_call['lastPrice'],
            'theoretical_price': bsm_call_price,
            'price_difference': closest_call['lastPrice'] - bsm_call_price,
            'implied_volatility': closest_call['impliedVolatility'] * 100 if 'impliedVolatility' in closest_call else None,
            'expiration': selected_expiration,
            'days_to_expiration': days_to_expiration
        }

        put_option = {
            'strike': closest_put['strike'],
            'market_price': closest_put['lastPrice'],
            'theoretical_price': bsm_put_price,
            'price_difference': closest_put['lastPrice'] - bsm_put_price,
            'implied_volatility': closest_put['impliedVolatility'] * 100 if 'impliedVolatility' in closest_put else None,
            'expiration': selected_expiration,
            'days_to_expiration': days_to_expiration
        }

        return call_option, put_option

    except Exception as e:
        raise Exception(f"Error retrieving options data: {str(e)}")
