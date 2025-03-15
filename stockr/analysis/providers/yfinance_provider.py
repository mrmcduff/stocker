from stockr.analysis.providers.base import DataProvider
import datetime as dt


class YFinanceProvider(DataProvider):
    """Data provider using Yahoo Finance."""

    def get_stock_data(self, ticker):
        """
        Retrieve current stock price and historical data using yfinance.

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            tuple: (current_price, company_name, historical_data)
        """
        # Import dependencies only when needed
        import yfinance as yf

        try:
            # Create a Ticker object
            stock = yf.Ticker(ticker)

            # Get company name
            company_name = stock.info.get(
                "shortName", stock.info.get("longName", ticker)
            )

            # Get the current stock price (or most recent closing price)
            current_price = stock.info.get("regularMarketPrice")
            if current_price is None:
                current_price = stock.history(period="1d")["Close"].iloc[-1]

            # Get historical data - we need more than 30 days to account for non-trading days
            end_date = dt.datetime.now()
            start_date = end_date - dt.timedelta(
                days=45
            )  # Get extra days to ensure we have 30 trading days
            historical_data = stock.history(start=start_date, end=end_date)

            if historical_data.empty:
                raise ValueError(
                    f"No historical data found for ticker '{ticker}'. Please check the ticker symbol."
                )

            return current_price, company_name, historical_data
        except Exception as e:
            raise Exception(f"Error retrieving stock data from Yahoo Finance: {str(e)}")

    def get_risk_free_rate(self):
        """
        Get current risk-free rate using Yahoo Finance.

        Returns:
            float: Current risk-free rate as a decimal
        """
        # Import dependencies only when needed
        import yfinance as yf

        try:
            # Use ^IRX ticker (13-week Treasury Bill) as a proxy for risk-free rate
            treasury = yf.Ticker("^IRX")
            current_yield = treasury.info.get("regularMarketPrice")

            # Convert from percentage to decimal
            if current_yield is not None:
                return current_yield / 100
            else:
                # Fallback to a reasonable default if data isn't available
                return 0.05  # 5% as a reasonable default
        except Exception:
            # Fallback to a reasonable default if there's an error
            return 0.05  # 5% as a reasonable default

    def get_options_chain(self, ticker, expiration_date=None):
        """
        Get options chain data using Yahoo Finance.

        Args:
            ticker (str): Stock ticker symbol
            expiration_date (str, optional): Expiration date in 'YYYY-MM-DD' format.
                                            If None, returns the nearest available.

        Returns:
            tuple: (expirations, calls_df, puts_df)
                expirations: list of available expiration dates
                calls_df: DataFrame with call options data
                puts_df: DataFrame with put options data
        """
        # Import dependencies only when needed
        import yfinance as yf
        import datetime as dt

        try:
            # Create a Ticker object
            stock = yf.Ticker(ticker)

            # Get available expiration dates
            expirations = stock.options

            if not expirations:
                raise ValueError(f"No options data available for ticker '{ticker}'.")

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

            # Get the options chain
            options = stock.option_chain(selected_expiration)

            # Return the data
            return selected_expiration, options.calls, options.puts

        except Exception as e:
            raise Exception(
                f"Error retrieving options data from Yahoo Finance: {str(e)}"
            )
