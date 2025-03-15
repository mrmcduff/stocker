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
    errors,
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
        errors (str[]): Any errors encountered during calculations

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

        # Show theoretical prices from different models
        output.append(f"  [bold]Theoretical Prices:[/bold]")
        output.append(
            f"    [bold]Black-Scholes:[/bold] ${call_option['theoretical_price']:.2f}"
        )
        output.append(
            f"    [bold]Binomial Tree:[/bold] ${call_option['binomial_price']:.2f}"
        )
        output.append(
            f"    [bold]Bates Model:[/bold] ${call_option['bates_price']:.2f}"
        )

        # Show model comparison to market price
        output.append(f"  [bold]Model vs Market:[/bold]")

        # Black-Scholes difference
        price_diff = call_option["market_price"] - call_option["theoretical_price"]
        price_diff_percent = (
            (price_diff / call_option["theoretical_price"]) * 100
            if call_option["theoretical_price"] > 0
            else 0
        )

        if price_diff > 0:
            output.append(
                f"    [bold]BSM:[/bold] [green]+${price_diff:.2f} ({price_diff_percent:.1f}% premium)[/green]"
            )
        else:
            output.append(
                f"    [bold]BSM:[/bold] [red]-${abs(price_diff):.2f} ({abs(price_diff_percent):.1f}% discount)[/red]"
            )

        # Binomial difference
        bin_diff = call_option["market_price"] - call_option["binomial_price"]
        bin_diff_percent = (
            (bin_diff / call_option["binomial_price"]) * 100
            if call_option["binomial_price"] > 0
            else 0
        )

        if bin_diff > 0:
            output.append(
                f"    [bold]Binomial:[/bold] [green]+${bin_diff:.2f} ({bin_diff_percent:.1f}% premium)[/green]"
            )
        else:
            output.append(
                f"    [bold]Binomial:[/bold] [red]-${abs(bin_diff):.2f} ({abs(bin_diff_percent):.1f}% discount)[/red]"
            )

        # Bates difference
        bates_diff = call_option["market_price"] - call_option["bates_price"]
        bates_diff_percent = (
            (bates_diff / call_option["bates_price"]) * 100
            if call_option["bates_price"] > 0
            else 0
        )

        if bates_diff > 0:
            output.append(
                f"    [bold]Bates:[/bold] [green]+${bates_diff:.2f} ({bates_diff_percent:.1f}% premium)[/green]"
            )
        else:
            output.append(
                f"    [bold]Bates:[/bold] [red]-${abs(bates_diff):.2f} ({abs(bates_diff_percent):.1f}% discount)[/red]"
            )

        if call_option["implied_volatility"] is not None:
            output.append(
                f"\n  [bold]Implied Volatility:[/bold] {call_option['implied_volatility']:.2f}%"
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

        # Show theoretical prices from different models
        output.append(f"  [bold]Theoretical Prices:[/bold]")
        output.append(
            f"    [bold]Black-Scholes:[/bold] ${put_option['theoretical_price']:.2f}"
        )
        output.append(
            f"    [bold]Binomial Tree:[/bold] ${put_option['binomial_price']:.2f}"
        )
        output.append(f"    [bold]Bates Model:[/bold] ${put_option['bates_price']:.2f}")

        # Show model comparison to market price
        output.append(f"  [bold]Model vs Market:[/bold]")

        # Black-Scholes difference
        price_diff = put_option["market_price"] - put_option["theoretical_price"]
        price_diff_percent = (
            (price_diff / put_option["theoretical_price"]) * 100
            if put_option["theoretical_price"] > 0
            else 0
        )

        if price_diff > 0:
            output.append(
                f"    [bold]BSM:[/bold] [green]+${price_diff:.2f} ({price_diff_percent:.1f}% premium)[/green]"
            )
        else:
            output.append(
                f"    [bold]BSM:[/bold] [red]-${abs(price_diff):.2f} ({abs(price_diff_percent):.1f}% discount)[/red]"
            )

        # Binomial difference
        bin_diff = put_option["market_price"] - put_option["binomial_price"]
        bin_diff_percent = (
            (bin_diff / put_option["binomial_price"]) * 100
            if put_option["binomial_price"] > 0
            else 0
        )

        if bin_diff > 0:
            output.append(
                f"    [bold]Binomial:[/bold] [green]+${bin_diff:.2f} ({bin_diff_percent:.1f}% premium)[/green]"
            )
        else:
            output.append(
                f"    [bold]Binomial:[/bold] [red]-${abs(bin_diff):.2f} ({abs(bin_diff_percent):.1f}% discount)[/red]"
            )

        # Bates difference
        bates_diff = put_option["market_price"] - put_option["bates_price"]
        bates_diff_percent = (
            (bates_diff / put_option["bates_price"]) * 100
            if put_option["bates_price"] > 0
            else 0
        )

        if bates_diff > 0:
            output.append(
                f"    [bold]Bates:[/bold] [green]+${bates_diff:.2f} ({bates_diff_percent:.1f}% premium)[/green]"
            )
        else:
            output.append(
                f"    [bold]Bates:[/bold] [red]-${abs(bates_diff):.2f} ({abs(bates_diff_percent):.1f}% discount)[/red]"
            )

        if put_option["implied_volatility"] is not None:
            output.append(
                f"\n  [bold]Implied Volatility:[/bold] {put_option['implied_volatility']:.2f}%"
            )
            vol_diff = put_option["implied_volatility"] - volatility
            vol_color = "green" if vol_diff >= 0 else "red"
            output.append(
                f"  [bold]Volatility Difference:[/bold] [{vol_color}]{vol_diff:.2f}%[/{vol_color}]"
            )
        if len(errors) > 0:
            output.extend(errors)
    else:
        output.append("[yellow]Options data not available for this ticker[/yellow]")

    return "\n".join(output)
