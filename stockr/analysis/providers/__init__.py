"""
Provider package for different data sources.
"""

from stockr.analysis.providers.base import DataProvider
from stockr.analysis.providers.yfinance_provider import YFinanceProvider
from stockr.analysis.providers.polygon_provider import PolygonProvider

# Export the provider classes
__all__ = ["DataProvider", "YFinanceProvider", "PolygonProvider"]
