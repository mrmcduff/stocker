"""
Base data provider abstract class.
"""

import abc


class DataProvider(abc.ABC):
    """Abstract base class for all data providers."""

    @abc.abstractmethod
    def get_stock_data(self, ticker):
        """
        Retrieve current stock price and historical data.

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            tuple: (current_price, company_name, historical_data)
        """
        pass

    @abc.abstractmethod
    def get_risk_free_rate(self):
        """
        Get current risk-free rate.

        Returns:
            float: Current risk-free rate as a decimal
        """
        pass

    @abc.abstractmethod
    def get_options_chain(self, ticker, expiration_date=None):
        """
        Get options chain data for a given ticker and expiration date.

        Args:
            ticker (str): Stock ticker symbol
            expiration_date (str, optional): Expiration date in 'YYYY-MM-DD' format.
                                            If None, returns the nearest available.

        Returns:
            tuple: (selected_expiration, calls_df, puts_df)
                selected_expiration: selected option expiration date in 'YYYY-MM-DD' format.
                calls_df: DataFrame with call options data
                puts_df: DataFrame with put options data
        """
        pass
