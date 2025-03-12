#!/usr/bin/env python
"""
Stock Analysis CLI Tool

This tool allows users to input a stock ticker and receive:
1. Current/most recent stock price
2. 30-day trailing volatility
3. Current options prices for specific strike prices
4. Black-Scholes-Merton theoretical prices

Usage:
    stockr TICKER
"""

import argparse
import sys
import math
import datetime as dt
from scipy.stats import norm
import numpy as np
import pandas as pd
import yfinance as yf  # Yahoo Finance API wrapper
from rich.console import Console
from rich.spinner import Spinner


def get_stock_data(ticker):
    """
    Retrieve current stock price and historical data for volatility calculation.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        tuple: (current_price, historical_data)
    """
    try:
        # Create a Ticker object
        stock = yf.Ticker(ticker)

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

        return current_price, historical_data
    except Exception as e:
        raise Exception(f"Error retrieving stock data: {str(e)}")


def calculate_volatility(historical_data, trading_days=30):
    """
    Calculate the trailing volatility based on the last N trading days.

    Args:
        historical_data (pd.DataFrame): Historical price data
        trading_days (int): Number of trading days to use for calculation

    Returns:
        float: Annualized volatility as a percentage
    """
    # Ensure we have enough data
    if len(historical_data) < trading_days:
        print(f"Warning: Only {len(historical_data)} trading days available, using all available data")
        trading_days = len(historical_data)

    # Calculate daily returns
    closing_prices = historical_data['Close'].tail(trading_days)
    daily_returns = closing_prices.pct_change().dropna()

    # Calculate standard deviation of daily returns
    daily_std = daily_returns.std()

    # Annualize the volatility (multiply by sqrt of trading days in a year)
    # Standard financial practice assumes 252 trading days in a year
    annualized_volatility = daily_std * math.sqrt(252)

    # Convert to percentage
    return annualized_volatility * 100


def black_scholes_merton(S, K, T, r, sigma, option_type='call'):
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
    # Convert volatility from percentage to decimal
    sigma = sigma / 100

    # Calculate d1 and d2
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    # Calculate option price
    if option_type.lower() == 'call':
        option_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:  # Put option
        option_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return option_price


def get_risk_free_rate():
    """
    Get current risk-free rate (approximated by 3-month US Treasury yield).

    Returns:
        float: Current risk-free rate as a decimal
    """
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


def format_output(ticker, current_price, volatility, call_option, put_option, risk_free_rate):
    """
    Format the analysis results for display.

    Args:
        ticker (str): Stock ticker symbol
        current_price (float): Current stock price
        volatility (float): 30-day trailing volatility
        call_option (dict): Call option data
        put_option (dict): Put option data
        risk_free_rate (float): Current risk-free rate

    Returns:
        str: Formatted output string
    """
    # Rich markup for better formatting
    output = []
    output.append(f"\n[bold green]===== {ticker} Stock Analysis =====[/bold green]")
    output.append(f"\n[bold]Current Price:[/bold] ${current_price:.2f}")
    output.append(f"[bold]30-Day Trailing Volatility:[/bold] {volatility:.2f}%")
    output.append(f"[bold]Risk-Free Rate:[/bold] {risk_free_rate*100:.2f}%")

    output.append("\n[bold cyan]--- Options Analysis ---[/bold cyan]")
    if call_option and put_option:
        expiry = call_option['expiration']
        days = call_option['days_to_expiration']

        output.append(f"[bold]Options Expiration:[/bold] {expiry} ({days} days)")

        # Call option details
        call_pct = (call_option['strike']/current_price - 1)*100
        output.append(f"\n[bold blue]Call Option[/bold blue] (Strike: ${call_option['strike']:.2f}, +{call_pct:.1f}%):")
        output.append(f"  [bold]Market Price:[/bold] ${call_option['market_price']:.2f}")
        output.append(f"  [bold]Theoretical Price (BSM):[/bold] ${call_option['theoretical_price']:.2f}")

        price_diff = call_option['price_difference']
        price_diff_percent = (price_diff / call_option['theoretical_price']) * 100 if call_option['theoretical_price'] > 0 else 0

        if price_diff > 0:
            output.append(f"  [bold green]Market Premium:[/bold green] ${price_diff:.2f} ({price_diff_percent:.1f}% above BSM)")
        else:
            output.append(f"  [bold red]Market Discount:[/bold red] ${abs(price_diff):.2f} ({abs(price_diff_percent):.1f}% below BSM)")

        if call_option['implied_volatility'] is not None:
            output.append(f"  [bold]Implied Volatility:[/bold] {call_option['implied_volatility']:.2f}%")
            vol_diff = call_option['implied_volatility'] - volatility
            vol_color = "green" if vol_diff >= 0 else "red"
            output.append(f"  [bold]Volatility Difference:[/bold] [{vol_color}]{vol_diff:.2f}%[/{vol_color}]")

        # Put option details
        put_pct = (put_option['strike']/current_price - 1)*100
        output.append(f"\n[bold magenta]Put Option[/bold magenta] (Strike: ${put_option['strike']:.2f}, {put_pct:.1f}%):")
        output.append(f"  [bold]Market Price:[/bold] ${put_option['market_price']:.2f}")
        output.append(f"  [bold]Theoretical Price (BSM):[/bold] ${put_option['theoretical_price']:.2f}")

        price_diff = put_option['price_difference']
        price_diff_percent = (price_diff / put_option['theoretical_price']) * 100 if put_option['theoretical_price'] > 0 else 0

        if price_diff > 0:
            output.append(f"  [bold green]Market Premium:[/bold green] ${price_diff:.2f} ({price_diff_percent:.1f}% above BSM)")
        else:
            output.append(f"  [bold red]Market Discount:[/bold red] ${abs(price_diff):.2f} ({abs(price_diff_percent):.1f}% below BSM)")

        if put_option['implied_volatility'] is not None:
            output.append(f"  [bold]Implied Volatility:[/bold] {put_option['implied_volatility']:.2f}%")
            vol_diff = put_option['implied_volatility'] - volatility
            vol_color = "green" if vol_diff >= 0 else "red"
            output.append(f"  [bold]Volatility Difference:[/bold] [{vol_color}]{vol_diff:.2f}%[/{vol_color}]")
    else:
        output.append("[yellow]Options data not available for this ticker[/yellow]")

    return "\n".join(output)


def main():
    """Main entry point for the CLI tool."""
    # Initialize Rich console for pretty output
    console = Console()

    # Check if ticker was provided as command line argument
    parser = argparse.ArgumentParser(description="Stock Analysis CLI Tool")
    parser.add_argument('ticker', type=str, nargs='?', help='Stock ticker symbol (e.g., AAPL)')

    args = parser.parse_args()

    # Interactive mode
    if args.ticker:
        # Single run mode if ticker was provided as argument
        analyze_ticker(args.ticker, console)
    else:
        # Interactive shell mode
        run_interactive_shell(console)


def analyze_ticker(ticker, console):
    """
    Analyze a specific ticker and display results.

    Args:
        ticker (str): Stock ticker symbol
        console (Console): Rich console object for output
    """
    ticker = ticker.upper()

    with console.status(f"[bold blue]Fetching data for {ticker}...", spinner="dots") as status:
        try:
            # Get stock data
            status.update(f"[bold blue]Retrieving current price for {ticker}...")
            current_price, historical_data = get_stock_data(ticker)

            # Calculate volatility
            status.update(f"[bold blue]Calculating volatility for {ticker}...")
            volatility = calculate_volatility(historical_data)

            # Get risk-free rate
            status.update(f"[bold blue]Retrieving risk-free rate...")
            risk_free_rate = get_risk_free_rate()

            # Get options data
            status.update(f"[bold blue]Analyzing options data for {ticker}...")
            call_option, put_option = get_options_data(ticker, current_price, volatility)

            # Format results
            status.update(f"[bold blue]Preparing analysis for {ticker}...")
            output = format_output(ticker, current_price, volatility, call_option, put_option, risk_free_rate)

            # Display final results
            console.print(output)
            return True
        except Exception as e:
            console.print(f"[bold red]Error analyzing {ticker}: {str(e)}[/bold red]")
            return False


def run_interactive_shell(console):
    """
    Run an interactive shell that allows analyzing multiple tickers.

    Args:
        console (Console): Rich console object for output
    """
    console.print("[bold green]===== Stock Analyzer Interactive Shell =====[/bold green]")
    console.print("Enter a ticker symbol to analyze or type 'exit' to quit.")

    while True:
        # Get user input
        ticker = console.input("\n[bold cyan]Enter ticker symbol (or 'exit' to quit): [/bold cyan]")

        # Check for exit command
        if ticker.lower() in ['exit', 'quit', 'q', 'bye']:
            console.print("[bold green]Exiting Stock Analyzer. Goodbye![/bold green]")
            break

        # Skip empty input
        if not ticker.strip():
            continue

        # Analyze the ticker
        analyze_ticker(ticker, console)


if __name__ == "__main__":
    main()
