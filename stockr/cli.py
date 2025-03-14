#!/usr/bin/env python
"""
Stock Analysis CLI Tool

This tool allows users to input a stock ticker and receive:
1. Current/most recent stock price
2. 30-day trailing volatility
3. Current options prices for specific strike prices
4. Black-Scholes-Merton theoretical prices

Usage:
    stockr [TICKER]  # Interactive mode if no ticker provided
"""

# Start with only essential imports for startup
import argparse
import sys
from prompt_toolkit import prompt

# Rich is smaller than pandas/numpy, so it's acceptable for startup
from rich.console import Console
from rich.spinner import Spinner

# Local imports - these are small and fast
from stockr.completion import TickerCompleter
from stockr.formatters import format_output
from stockr.analysis import (
    get_stock_data,
    get_risk_free_rate,
    calculate_volatility,
    get_options_data,
)


def analyze_ticker(ticker, console):
    """
    Analyze a specific ticker and display results.

    Args:
        ticker (str): Stock ticker symbol
        console (Console): Rich console object for output
    """
    ticker = ticker.upper()

    with console.status(
        f"[bold blue]Fetching data for {ticker}...", spinner="dots"
    ) as status:
        try:
            # Get stock data
            status.update(f"[bold blue]Retrieving current price for {ticker}...")
            current_price, company_name, historical_data = get_stock_data(ticker)

            # Calculate volatility
            status.update(f"[bold blue]Calculating volatility for {ticker}...")
            volatility = calculate_volatility(historical_data)

            # Get risk-free rate
            status.update(f"[bold blue]Retrieving risk-free rate...")
            risk_free_rate = get_risk_free_rate()

            # Get options data
            status.update(f"[bold blue]Analyzing options data for {ticker}...")
            call_option, put_option = get_options_data(
                ticker, current_price, volatility
            )

            # Format results
            status.update(f"[bold blue]Preparing analysis for {ticker}...")
            output = format_output(
                ticker,
                company_name,
                current_price,
                volatility,
                call_option,
                put_option,
                risk_free_rate,
            )

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
    console.print(
        "[bold green]===== Stock Analyzer Interactive Shell =====[/bold green]"
    )
    console.print("Enter a ticker symbol to analyze or type 'exit' to quit.")
    console.print("Press [bold]Tab[/bold] to autocomplete ticker symbols.")

    # Create ticker completer for tab completion
    ticker_completer = TickerCompleter()

    while True:
        try:
            # Get user input with tab completion
            ticker = prompt(
                "\nEnter ticker symbol (or 'exit' to quit): ",
                completer=ticker_completer,
            )

            # Check for exit command
            if ticker.lower() in ["exit", "quit", "q", "bye"]:
                console.print(
                    "[bold green]Exiting Stock Analyzer. Goodbye![/bold green]"
                )
                break

            # Skip empty input
            if not ticker.strip():
                continue

            # Analyze the ticker
            analyze_ticker(ticker, console)
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C and Ctrl+D gracefully
            console.print(
                "\n[bold yellow]Keyboard interrupt detected. Use 'exit' to quit.[/bold yellow]"
            )
            continue


def main():
    """Main entry point for the CLI tool."""
    # Initialize Rich console for pretty output
    console = Console()

    # Check if ticker was provided as command line argument
    parser = argparse.ArgumentParser(description="Stock Analysis CLI Tool")
    parser.add_argument(
        "ticker", type=str, nargs="?", help="Stock ticker symbol (e.g., AAPL)"
    )

    args = parser.parse_args()

    # Interactive mode
    if args.ticker:
        # Single run mode if ticker was provided as argument
        analyze_ticker(args.ticker, console)
    else:
        # Interactive shell mode
        run_interactive_shell(console)


if __name__ == "__main__":
    main()
