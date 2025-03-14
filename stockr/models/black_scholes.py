"""
Black-Scholes-Merton option pricing model.
"""


def black_scholes_merton(S, K, T, r, sigma, option_type="call"):
    """
    Calculate option price using Black-Scholes-Merton model.

    Args:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate
        sigma (float): Volatility of the underlying asset (annualized)
        option_type (str): 'call' or 'put'

    Returns:
        float: Option price
    """
    # Import dependencies only when needed
    import math
    from scipy.stats import norm

    # Convert volatility from percentage to decimal
    sigma = sigma / 100

    # Calculate d1 and d2
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    # Calculate option price
    if option_type.lower() == "call":
        option_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:  # Put option
        option_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return option_price
