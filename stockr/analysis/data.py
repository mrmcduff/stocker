"""
Data retrieval functions for stock analysis.

This module provides a simplified interface to the data manager.
"""

from stockr.analysis.data_manager import (
    get_stock_data,
    get_risk_free_rate,
    set_default_provider,
    get_options_chain,
)

# Re-export the functions from data_manager for backward compatibility
# This allows existing code to continue working without changes

__all__ = [
    "get_stock_data",
    "get_risk_free_rate",
    "set_default_provider",
    "get_options_chain",
]
