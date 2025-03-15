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
            call_option, put_option, errors = get_options_data(
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
                errors,
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
    console.print("\nAdditional commands:")
    console.print("  [bold]provider[/bold] - Show current data provider")
    console.print(
        "  [bold]provider yfinance[/bold] - Switch to Yahoo Finance data provider"
    )
    console.print(
        "  [bold]provider polygon API_KEY[/bold] - Switch to Polygon.io with API key"
    )
    console.print("  [bold]help[/bold] - Show available commands")

    # Create ticker completer for tab completion
    ticker_completer = TickerCompleter()

    while True:
        try:
            # Get user input with tab completion
            user_input = prompt(
                "\nEnter ticker symbol or command (or 'exit' to quit): ",
                completer=ticker_completer,
            )

            # Check for exit command
            if user_input.lower() in ["exit", "quit", "q", "bye"]:
                console.print(
                    "[bold green]Exiting Stock Analyzer. Goodbye![/bold green]"
                )
                break

            # Check for help command
            if user_input.lower() == "help":
                console.print("\n[bold cyan]Available Commands:[/bold cyan]")
                console.print(
                    "  [bold]<ticker>[/bold] - Analyze a stock ticker (e.g., AAPL)"
                )
                console.print("  [bold]provider[/bold] - Show current data provider")
                console.print(
                    "  [bold]provider yfinance[/bold] - Switch to Yahoo Finance data provider"
                )
                console.print(
                    "  [bold]provider polygon API_KEY[/bold] - Switch to Polygon.io with API key"
                )
                console.print(
                    "  [bold]exit[/bold], [bold]quit[/bold], [bold]q[/bold], [bold]bye[/bold] - Exit the program"
                )
                console.print("  [bold]help[/bold] - Show this help message")
                continue

            # Check for provider command
            if user_input.lower().startswith("provider"):
                parts = user_input.split()

                # Just 'provider' - show current provider
                if len(parts) == 1:
                    from stockr.analysis.data_manager import get_default_provider

                    provider = get_default_provider()
                    provider_name = provider.__class__.__name__
                    console.print(
                        f"[bold cyan]Current data provider:[/bold cyan] {provider_name}"
                    )
                    continue

                # provider with arguments
                if len(parts) >= 2:
                    provider_name = parts[1].lower()

                    if provider_name == "yfinance":
                        from stockr.analysis.data import set_default_provider

                        set_default_provider("yfinance")
                        console.print(
                            f"[bold green]Switched to Yahoo Finance data provider[/bold green]"
                        )
                    elif provider_name == "polygon":
                        api_key = parts[2] if len(parts) > 2 else None
                        try:
                            from stockr.analysis.data import set_default_provider

                            set_default_provider("polygon", api_key=api_key)
                            console.print(
                                f"[bold green]Switched to Polygon.io data provider[/bold green]"
                            )
                        except ValueError as e:
                            console.print(f"[bold red]Error: {str(e)}[/bold red]")
                    else:
                        console.print(
                            f"[bold red]Unknown provider: {provider_name}. Choose 'yfinance' or 'polygon'.[/bold red]"
                        )
                    continue

            # Skip empty input
            if not user_input.strip():
                continue

            # Analyze the ticker
            analyze_ticker(user_input, console)
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
