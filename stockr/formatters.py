"""
Formatting functions for displaying analysis results.
"""


def format_output(
    ticker,
    company_name,
    current_price,
    volatility,
    call_option,
    put_option,
    risk_free_rate,
):
    """
    Format the analysis results for display.

    Args:
        ticker (str): Stock ticker symbol
        company_name (str): Company name
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
    output.append(f"[bold yellow]{company_name}[/bold yellow]")
    output.append(f"\n[bold]Current Price:[/bold] ${current_price:.2f}")
    output.append(f"[bold]30-Day Trailing Volatility:[/bold] {volatility:.2f}%")
    output.append(f"[bold]Risk-Free Rate:[/bold] {risk_free_rate * 100:.2f}%")

    output.append("\n[bold cyan]--- Options Analysis ---[/bold cyan]")
    if call_option and put_option:
        expiry = call_option["expiration"]
        days = call_option["days_to_expiration"]

        output.append(f"[bold]Options Expiration:[/bold] {expiry} ({days} days)")

        # Call option details
        call_pct = (call_option["strike"] / current_price - 1) * 100
        output.append(
            f"\n[bold blue]Call Option[/bold blue] (Strike: ${call_option['strike']:.2f}, +{call_pct:.1f}%):"
        )
        output.append(
            f"  [bold]Market Price:[/bold] ${call_option['market_price']:.2f}"
        )
        output.append(
            f"  [bold]Theoretical Price (BSM):[/bold] ${call_option['theoretical_price']:.2f}"
        )

        price_diff = call_option["price_difference"]
        price_diff_percent = (
            (price_diff / call_option["theoretical_price"]) * 100
            if call_option["theoretical_price"] > 0
            else 0
        )

        if price_diff > 0:
            output.append(
                f"  [bold green]Market Premium:[/bold green] ${price_diff:.2f} ({price_diff_percent:.1f}% above BSM)"
            )
        else:
            output.append(
                f"  [bold red]Market Discount:[/bold red] ${abs(price_diff):.2f} ({abs(price_diff_percent):.1f}% below BSM)"
            )

        if call_option["implied_volatility"] is not None:
            output.append(
                f"  [bold]Implied Volatility:[/bold] {call_option['implied_volatility']:.2f}%"
            )
            vol_diff = call_option["implied_volatility"] - volatility
            vol_color = "green" if vol_diff >= 0 else "red"
            output.append(
                f"  [bold]Volatility Difference:[/bold] [{vol_color}]{vol_diff:.2f}%[/{vol_color}]"
            )

        # Put option details
        put_pct = (put_option["strike"] / current_price - 1) * 100
        output.append(
            f"\n[bold magenta]Put Option[/bold magenta] (Strike: ${put_option['strike']:.2f}, {put_pct:.1f}%):"
        )
        output.append(f"  [bold]Market Price:[/bold] ${put_option['market_price']:.2f}")
        output.append(
            f"  [bold]Theoretical Price (BSM):[/bold] ${put_option['theoretical_price']:.2f}"
        )

        price_diff = put_option["price_difference"]
        price_diff_percent = (
            (price_diff / put_option["theoretical_price"]) * 100
            if put_option["theoretical_price"] > 0
            else 0
        )

        if price_diff > 0:
            output.append(
                f"  [bold green]Market Premium:[/bold green] ${price_diff:.2f} ({price_diff_percent:.1f}% above BSM)"
            )
        else:
            output.append(
                f"  [bold red]Market Discount:[/bold red] ${abs(price_diff):.2f} ({abs(price_diff_percent):.1f}% below BSM)"
            )

        if put_option["implied_volatility"] is not None:
            output.append(
                f"  [bold]Implied Volatility:[/bold] {put_option['implied_volatility']:.2f}%"
            )
            vol_diff = put_option["implied_volatility"] - volatility
            vol_color = "green" if vol_diff >= 0 else "red"
            output.append(
                f"  [bold]Volatility Difference:[/bold] [{vol_color}]{vol_diff:.2f}%[/{vol_color}]"
            )
    else:
        output.append("[yellow]Options data not available for this ticker[/yellow]")

    return "\n".join(output)
