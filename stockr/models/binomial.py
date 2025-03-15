"""
Binomial Options Pricing Model.

This module implements the Cox-Ross-Rubinstein binomial model for option pricing.
The binomial model provides a discrete-time approximation to the Black-Scholes model
and can handle features like early exercise (American options) and dividends.
"""

import math
import numpy as np


def binomial_option_price(
    S, K, T, r, sigma, option_type="call", steps=100, american=False, dividend_yield=0
):
    """
    Calculate option price using the Cox-Ross-Rubinstein binomial model.

    Args:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Volatility of the underlying asset (decimal)
        option_type (str): 'call' or 'put'
        steps (int): Number of time steps in the binomial tree
        american (bool): If True, allow early exercise (American option)
        dividend_yield (float): Continuous dividend yield (decimal)

    Returns:
        float: Option price
    """
    # Convert volatility from percentage to decimal if needed
    if sigma > 1:
        sigma = sigma / 100

    # Time step
    dt = T / steps

    # Up and down factors
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u

    # Risk-neutral probability
    # Adjusted for dividend yield
    a = math.exp((r - dividend_yield) * dt)
    p = (a - d) / (u - d)

    # Discount factor
    df = math.exp(-r * dt)

    # Initialize asset prices at the final step
    prices = np.zeros(steps + 1)
    for i in range(steps + 1):
        prices[i] = S * (u ** (steps - i)) * (d**i)

    # Initialize option values at the final step
    if option_type.lower() == "call":
        option_values = np.maximum(0, prices - K)
    else:  # Put option
        option_values = np.maximum(0, K - prices)

    # Backward induction through the tree
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            # Calculate the asset price at this node
            asset_price = S * (u ** (i - j)) * (d**j)

            # Calculate the option value at this node (discounted expected value)
            option_value = df * (p * option_values[j] + (1 - p) * option_values[j + 1])

            # For American options, check if early exercise is optimal
            if american:
                if option_type.lower() == "call":
                    exercise_value = max(0, asset_price - K)
                else:  # Put option
                    exercise_value = max(0, K - asset_price)
                option_value = max(option_value, exercise_value)

            option_values[j] = option_value

    # The option price is the value at the root node
    return option_values[0]
