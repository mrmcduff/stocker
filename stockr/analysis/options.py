"""
Options data retrieval and analysis.
"""

from stockr.analysis.data import get_risk_free_rate
from stockr.models.black_scholes import black_scholes_merton
from stockr.models.binomial import binomial_option_price
from stockr.models.bates import bates_approximation


def get_options_data(ticker, current_price, annual_volatility):
    """
    Get options pricing for strike prices 10% above and below the current price.
    Also calculate theoretical prices using multiple option pricing models.

    Args:
        ticker (str): Stock ticker symbol
        current_price (float): Current stock price
        annual_volatility (float): 30-day trailing volatility (annualized)

    Returns:
        tuple: (call_option, put_option) - Dictionary with options data
    """
    # Import dependencies only when needed
    import datetime as dt
    import numpy as np
    import yfinance as yf

    try:
        stock = yf.Ticker(ticker)

        errors = []
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
            exp_date = dt.datetime.strptime(exp, "%Y-%m-%d").date()
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
        calls_df["strike_diff"] = abs(calls_df["strike"] - call_strike_target)
        closest_call = calls_df.loc[calls_df["strike_diff"].idxmin()]

        # Find closest put strike
        puts_df["strike_diff"] = abs(puts_df["strike"] - put_strike_target)
        closest_put = puts_df.loc[puts_df["strike_diff"].idxmin()]

        # Calculate days to expiration
        exp_date = dt.datetime.strptime(selected_expiration, "%Y-%m-%d").date()
        days_to_expiration = (exp_date - today).days

        # Get risk-free rate
        risk_free_rate = get_risk_free_rate()

        # Calculate time to expiration in years
        T = days_to_expiration / 365.0

        # Calculate theoretical prices using different option pricing models
        # 1. Black-Scholes-Merton model
        bsm_call_price = black_scholes_merton(
            S=current_price,
            K=closest_call["strike"],
            T=T,
            r=risk_free_rate,
            sigma=annual_volatility,
            option_type="call",
        )

        bsm_put_price = black_scholes_merton(
            S=current_price,
            K=closest_put["strike"],
            T=T,
            r=risk_free_rate,
            sigma=annual_volatility,
            option_type="put",
        )

        # 2. Binomial model (with 100 steps)
        bin_call_price = binomial_option_price(
            S=current_price,
            K=closest_call["strike"],
            T=T,
            r=risk_free_rate,
            sigma=annual_volatility / 100,  # Convert from percentage to decimal
            option_type="call",
            steps=100,
            american=False,  # Match BSM assumptions for comparison
        )

        bin_put_price = binomial_option_price(
            S=current_price,
            K=closest_put["strike"],
            T=T,
            r=risk_free_rate,
            sigma=annual_volatility / 100,  # Convert from percentage to decimal
            option_type="put",
            steps=100,
            american=False,  # Match BSM assumptions for comparison
        )

        # 3. Bates model (simplified approximation)
        try:
            bates_call_price = bates_approximation(
                S=current_price,
                K=closest_call['strike'],
                T=T,
                r=risk_free_rate,
                sigma=annual_volatility,  # Will be converted inside the function
                option_type='call'
            )

            bates_put_price = bates_approximation(
                S=current_price,
                K=closest_put['strike'],
                T=T,
                r=risk_free_rate,
                sigma=annual_volatility,  # Will be converted inside the function
                option_type='put'
            )

            # Sanity check for Bates model results
            # If Bates price differs too much from BSM, fall back to BSM
            if (abs(bates_call_price - bsm_call_price) > bsm_call_price) or not np.isfinite(bates_call_price):
                bates_call_price = bsm_call_price
                errors.append(f"    Bates call price too far from BSM: {bates_call_price}")

            if (abs(bates_put_price - bsm_put_price) > bsm_put_price) or not np.isfinite(bates_put_price):
                bates_put_price = bsm_put_price
                errors.append(f"    Bates put price too far from BSM: {bates_put_price}")

        except Exception:
            # Bates model can sometimes fail, fallback to BSM
            bates_call_price = bsm_call_price
            bates_put_price = bsm_put_price
            errors.append("Bates process did not converge")

        # Create dictionaries with the relevant info
        call_option = {
            "strike": closest_call["strike"],
            "market_price": closest_call["lastPrice"],
            "theoretical_price": bsm_call_price,
            "price_difference": closest_call["lastPrice"] - bsm_call_price,
            "implied_volatility": closest_call["impliedVolatility"] * 100
            if "impliedVolatility" in closest_call
            else None,
            "expiration": selected_expiration,
            "days_to_expiration": days_to_expiration,
            # Additional pricing models
            "binomial_price": bin_call_price,
            "bates_price": bates_call_price,
        }

        put_option = {
            "strike": closest_put["strike"],
            "market_price": closest_put["lastPrice"],
            "theoretical_price": bsm_put_price,
            "price_difference": closest_put["lastPrice"] - bsm_put_price,
            "implied_volatility": closest_put["impliedVolatility"] * 100
            if "impliedVolatility" in closest_put
            else None,
            "expiration": selected_expiration,
            "days_to_expiration": days_to_expiration,
            # Additional pricing models
            "binomial_price": bin_put_price,
            "bates_price": bates_put_price,
        }

        return call_option, put_option, errors

    except Exception as e:
        raise Exception(f"Error retrieving options data: {str(e)}")
