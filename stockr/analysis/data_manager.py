"""
Data manager for managing different data providers.
"""

from stockr.analysis.providers import YFinanceProvider, PolygonProvider

# Singleton to store the current data provider
_current_provider = None


def get_provider(provider_name=None, **kwargs):
    """
    Get a data provider by name.

    Args:
        provider_name (str): Name of the provider ('yfinance' or 'polygon')
        **kwargs: Additional arguments to pass to the provider constructor

    Returns:
        DataProvider: An instance of the selected data provider

    Raises:
        ValueError: If the provider name is not recognized
    """
    if provider_name == "yfinance":
        return YFinanceProvider()
    elif provider_name == "polygon":
        return PolygonProvider(**kwargs)
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. Choose from 'yfinance' or 'polygon'."
        )


def set_default_provider(provider_name, **kwargs):
    """
    Set the default data provider.

    Args:
        provider_name (str): Name of the provider ('yfinance' or 'polygon')
        **kwargs: Additional arguments to pass to the provider constructor
    """
    global _current_provider
    _current_provider = get_provider(provider_name, **kwargs)


def get_default_provider():
    """
    Get the default data provider.

    Returns:
        DataProvider: The current default data provider
    """
    global _current_provider
    if _current_provider is None:
        # Default to YFinance if none is set
        _current_provider = YFinanceProvider()
    return _current_provider


def get_stock_data(ticker, provider=None, **kwargs):
    """
    Retrieve stock data using the specified or default provider.

    Args:
        ticker (str): Stock ticker symbol
        provider (str, optional): Provider name to override default
        **kwargs: Additional arguments for the provider

    Returns:
        tuple: (current_price, company_name, historical_data)
    """
    if provider:
        # Use specified provider for this call only
        data_provider = get_provider(provider, **kwargs)
    else:
        # Use default provider
        data_provider = get_default_provider()

    return data_provider.get_stock_data(ticker)


def get_risk_free_rate(provider=None, **kwargs):
    """
    Get risk-free rate using the specified or default provider.

    Args:
        provider (str, optional): Provider name to override default
        **kwargs: Additional arguments for the provider

    Returns:
        float: Current risk-free rate as a decimal
    """
    if provider:
        # Use specified provider for this call only
        data_provider = get_provider(provider, **kwargs)
    else:
        # Use default provider
        data_provider = get_default_provider()

    return data_provider.get_risk_free_rate()


def get_options_chain(ticker, expiration_date=None, provider=None, **kwargs):
    """
    Get options chain data using the specified or default provider.

    Args:
        ticker (str): Stock ticker symbol
        expiration_date (str, optional): Expiration date in 'YYYY-MM-DD' format
        provider (str, optional): Provider name to override default
        **kwargs: Additional arguments for the provider

    Returns:
        tuple: (expirations, calls_df, puts_df)
    """
    if provider:
        # Use specified provider for this call only
        data_provider = get_provider(provider, **kwargs)
    else:
        # Use default provider
        data_provider = get_default_provider()

    return data_provider.get_options_chain(ticker, expiration_date)
