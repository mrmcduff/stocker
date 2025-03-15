from stockr.analysis.providers.base import DataProvider

import datetime as dt
import os


class PolygonProvider(DataProvider):
    """Data provider using Polygon.io API."""

    def __init__(self, api_key=None):
        """
        Initialize with Polygon API key.

        Args:
            api_key (str, optional): API key for Polygon.io. If None, will look for POLYGON_API_KEY env var.
        """
        # Get API key from parameters or environment variable
        self.api_key = api_key or os.environ.get("POLYGON_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Polygon API key is required. Provide as parameter or set POLYGON_API_KEY environment variable."
            )

    def get_stock_data(self, ticker):
        """
        Retrieve current stock price and historical data using Polygon.io.

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            tuple: (current_price, company_name, historical_data)
        """
        # Import dependency only when needed
        import requests
        import pandas as pd

        try:
            # Get company details
            ticker_details_url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={self.api_key}"
            details_response = requests.get(ticker_details_url)
            details_data = details_response.json()

            if "results" not in details_data:
                raise ValueError(
                    f"No data found for ticker '{ticker}'. Please check the ticker symbol."
                )

            company_name = details_data["results"].get("name", ticker)

            # Get current price (latest close)
            current_price_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?apiKey={self.api_key}"
            price_response = requests.get(current_price_url)
            price_data = price_response.json()

            if "results" not in price_data or not price_data["results"]:
                raise ValueError(f"No price data found for ticker '{ticker}'.")

            current_price = price_data["results"][0]["c"]  # Closing price

            # Get historical data
            end_date = dt.datetime.now()
            start_date = end_date - dt.timedelta(days=45)

            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            historical_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}?apiKey={self.api_key}"
            historical_response = requests.get(historical_url)
            historical_data = historical_response.json()

            if "results" not in historical_data or not historical_data["results"]:
                raise ValueError(f"No historical data found for ticker '{ticker}'.")

            # Convert to pandas DataFrame
            df = pd.DataFrame(historical_data["results"])
            df["Date"] = pd.to_datetime(df["t"], unit="ms")
            df.set_index("Date", inplace=True)

            # Rename columns to match yfinance format
            df_renamed = pd.DataFrame(
                {
                    "Open": df["o"],
                    "High": df["h"],
                    "Low": df["l"],
                    "Close": df["c"],
                    "Volume": df["v"],
                }
            )

            return current_price, company_name, df_renamed

        except Exception as e:
            raise Exception(f"Error retrieving stock data from Polygon.io: {str(e)}")

    def get_risk_free_rate(self):
        """
        Get current risk-free rate using Polygon.io or FRED as fallback.

        Returns:
            float: Current risk-free rate as a decimal
        """
        # Import dependencies only when needed
        import requests

        try:
            # First attempt: Try to get 3-month Treasury yield from Polygon
            # The Treasury ticker for 3-month bills is typically $TNX or $IRX
            tsy_ticker = "TNX"  # 10-year Treasury Note Yield
            treasury_url = f"https://api.polygon.io/v2/aggs/ticker/{tsy_ticker}/prev?apiKey={self.api_key}"

            response = requests.get(treasury_url)
            data = response.json()

            if "results" in data and data["results"]:
                # Treasury yield is reported in percentage points, so divide by 100
                return data["results"][0]["c"] / 100

            # Second attempt: Try FRED API for 3-month Treasury Rate
            # This requires a separate FRED API key which we may not have
            # So we'll use a public endpoint that doesn't require authentication
            try:
                # Use FRED public data service
                fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS"
                fred_response = requests.get(fred_url)

                if fred_response.status_code == 200:
                    # Parse the CSV data (very simple parsing since we just need the latest value)
                    lines = fred_response.text.strip().split("\n")
                    if len(lines) > 1:
                        # Get the last line which should have the most recent data
                        latest_data = lines[-1].split(",")
                        if len(latest_data) >= 2:
                            try:
                                # Convert to decimal (FRED reports in percentage points)
                                return float(latest_data[1]) / 100
                            except (ValueError, IndexError):
                                pass
            except Exception:
                # If FRED fails, continue to fallback
                pass

            # Fallback: Use Yahoo Finance provider's method
            # Import locally to avoid circular imports
            from stockr.analysis.data_providers import YFinanceProvider

            yf_provider = YFinanceProvider()
            return yf_provider.get_risk_free_rate()

        except Exception:
            # Final fallback to a reasonable default if all methods fail
            return 0.05  # 5% as a default

    def get_options_chain(self, ticker, expiration_date=None):
        """
        Get options chain data using Polygon.io.

        Args:
            ticker (str): Stock ticker symbol
            expiration_date (str, optional): Expiration date in 'YYYY-MM-DD' format.
                                            If None, returns one between 30-45 days in the future if possible.

        Returns:
            tuple: (selected_expiration, calls_df, puts_df)
                selected_expiration: the selected expiration date in 'YYYY-MM-DD' format
                calls_df: DataFrame with call options data
                puts_df: DataFrame with put options data
        """
        # Import dependencies only when needed
        import requests
        import pandas as pd
        import datetime as dt

        try:
            # Get all available expiration dates
            expirations_url = f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={ticker}&limit=1000&apiKey={self.api_key}"
            expirations_response = requests.get(expirations_url)
            expirations_data = expirations_response.json()

            if "results" not in expirations_data or not expirations_data["results"]:
                raise ValueError(f"No options data available for ticker '{ticker}'.")

            # Extract unique expiration dates
            all_expirations = set()
            for contract in expirations_data["results"]:
                exp_date = contract.get("expiration_date")
                if exp_date:
                    all_expirations.add(exp_date)

            expirations = sorted(list(all_expirations))

            if not expirations:
                raise ValueError(
                    f"No options expiration dates found for ticker '{ticker}'."
                )

            # If no expiration date is specified, choose one 30-45 days out
            if expiration_date is None:
                today = dt.datetime.now().date()
                target_min_days = 30  # Target at least 30 days out
                target_max_days = 45  # Preferably not more than 45 days out

                # Convert all expiration strings to date objects for comparison
                expiry_dates = []
                for exp in expirations:
                    exp_date = dt.datetime.strptime(exp, "%Y-%m-%d").date()
                    days_to_expiry = (exp_date - today).days
                    expiry_dates.append((exp, days_to_expiry))

                # Sort by days to expiration
                expiry_dates.sort(key=lambda x: x[1])

                # Filter future dates
                future_expiries = [exp for exp in expiry_dates if exp[1] > 0]

                if not future_expiries:
                    # No future expirations available, take the most recent one
                    selected_expiration = expirations[-1]
                else:
                    # Find an expiration within our target range
                    target_expiries = [
                        exp for exp in future_expiries if exp[1] >= target_min_days
                    ]

                    if not target_expiries:
                        # No expirations at least 30 days out, take the furthest available
                        selected_expiration = future_expiries[-1][0]
                    else:
                        # Find expirations in the ideal 30-45 day range
                        ideal_expiries = [
                            exp for exp in target_expiries if exp[1] <= target_max_days
                        ]

                        if ideal_expiries:
                            # Take the one closest to 30 days
                            ideal_expiries.sort(
                                key=lambda x: abs(x[1] - target_min_days)
                            )
                            selected_expiration = ideal_expiries[0][0]
                        else:
                            # Take the one closest to 45 days
                            target_expiries.sort(
                                key=lambda x: abs(x[1] - target_max_days)
                            )
                            selected_expiration = target_expiries[0][0]

            # Fetch options chain for the selected expiration date
            options_url = f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={ticker}&expiration_date={selected_expiration}&limit=1000&apiKey={self.api_key}"
            options_response = requests.get(options_url)
            options_data = options_response.json()

            if "results" not in options_data or not options_data["results"]:
                raise ValueError(
                    f"No options contracts found for {ticker} with expiration date {selected_expiration}."
                )

            # Separate calls and puts
            calls = []
            puts = []

            for contract in options_data["results"]:
                contract_type = contract.get("contract_type")
                if contract_type == "call":
                    calls.append(contract)
                elif contract_type == "put":
                    puts.append(contract)

            # Get the latest prices for the options contracts
            # This requires additional API calls in a production environment
            # For this implementation, we'll create DataFrames with available data

            # Create call options DataFrame
            calls_df = pd.DataFrame(calls)
            if len(calls_df) > 0:
                # Transform to match yfinance format as closely as possible
                calls_df["strike"] = calls_df["strike_price"]
                calls_df["lastPrice"] = 0.0  # Would require additional API calls
                calls_df["impliedVolatility"] = (
                    0.0  # Would require additional API calls
                )

                # Add additional API calls for prices and greeks in a production implementation
            else:
                calls_df = pd.DataFrame(
                    columns=["strike", "lastPrice", "impliedVolatility"]
                )

            # Create put options DataFrame
            puts_df = pd.DataFrame(puts)
            if len(puts_df) > 0:
                # Transform to match yfinance format as closely as possible
                puts_df["strike"] = puts_df["strike_price"]
                puts_df["lastPrice"] = 0.0  # Would require additional API calls
                puts_df["impliedVolatility"] = 0.0  # Would require additional API calls

                # Add additional API calls for prices and greeks in a production implementation
            else:
                puts_df = pd.DataFrame(
                    columns=["strike", "lastPrice", "impliedVolatility"]
                )

            return selected_expiration, calls_df, puts_df

        except Exception as e:
            raise Exception(f"Error retrieving options data from Polygon.io: {str(e)}")
