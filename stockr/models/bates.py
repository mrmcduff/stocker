"""
Bates Jump Diffusion Model for Option Pricing.

This module implements a simplified Bates model, which extends the Black-Scholes model
by adding jump components. The Bates model can capture sudden price jumps,
making it suitable for modeling market crashes and unexpected movements.
"""


def bates_simplified(S, K, T, r, sigma, lambda_param=1.0, mu_j=-0.02, sigma_j=0.05, option_type='call'):
    """
    Calculate option price using a simplified Bates jump diffusion model.

    This implementation uses a simplified approach that models Bates as a mixture of
    Black-Scholes models with adjusted volatility and jump effects. This is more
    stable than the full Fourier-based implementation while still capturing the
    essential characteristics of the Bates model.

    Args:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Volatility of the underlying asset (decimal)
        lambda_param (float): Jump intensity (average number of jumps per year)
        mu_j (float): Average jump size (percentage)
        sigma_j (float): Jump size volatility
        option_type (str): 'call' or 'put'

    Returns:
        float: Option price
    """
    # Lazy imports
    import math
    from scipy.stats import norm

    # Convert volatility from percentage to decimal if needed
    if sigma > 1:
        sigma = sigma / 100

    # Number of jumps to consider in the mixture
    max_jumps = 10

    # Initialize option price
    option_price = 0.0

    # Adjust drift to ensure risk-neutral pricing
    adjusted_drift = r - lambda_param * (math.exp(mu_j + 0.5 * sigma_j**2) - 1)

    # Compute option price as a mixture of Black-Scholes prices
    for n in range(max_jumps):
        # Probability of exactly n jumps during time T
        jump_prob = (lambda_param * T)**n * math.exp(-lambda_param * T) / math.factorial(n)

        # Skip if probability is negligible
        if jump_prob < 1e-10:
            continue

        # Adjusted volatility with n jumps
        adjusted_sigma = math.sqrt(sigma**2 + n * sigma_j**2 / T)

        # Adjusted spot price with n jumps
        adjusted_S = S * math.exp(n * mu_j)

        # Black-Scholes price with adjusted parameters
        d1 = (math.log(adjusted_S / K) + (adjusted_drift + 0.5 * adjusted_sigma**2) * T) / (adjusted_sigma * math.sqrt(T))
        d2 = d1 - adjusted_sigma * math.sqrt(T)

        if option_type.lower() == 'call':
            bs_price = adjusted_S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        else:  # Put option
            bs_price = K * math.exp(-r * T) * norm.cdf(-d2) - adjusted_S * norm.cdf(-d1)

        # Add to the weighted sum
        option_price += jump_prob * bs_price

    return option_price


def bates_approximation(S, K, T, r, sigma, option_type='call'):
    """
    A simplified version of the Bates model with reasonable defaults.

    This function provides a user-friendly interface to the Bates model
    with sensible default parameters for the jump process.

    Args:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate (decimal)
        sigma (float): Volatility (percentage)
        option_type (str): 'call' or 'put'

    Returns:
        float: Option price
    """
    # Default jump parameters calibrated for typical market behavior
    # Lambda: Average 2 significant jumps per year
    # Mu_j: Average jump size of -2% (negative to capture crash risk)
    # Sigma_j: Jump volatility of 5%
    return bates_simplified(
        S=S,
        K=K,
        T=T,
        r=r,
        sigma=sigma,
        lambda_param=2.0,
        mu_j=-0.02,
        sigma_j=0.05,
        option_type=option_type
    )
