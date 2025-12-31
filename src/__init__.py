"""
Package initialization for Tesla Quant Trading Analysis
"""

__version__ = "1.0.0"
__author__ = "Tesla Quant Trading Team"

from .data_fetcher import DataFetcher
from .indicators import TechnicalIndicators
from .strategies import (
    TradingStrategy,
    TrendFollowingStrategy,
    MeanReversionStrategy,
    MomentumStrategy,
    CombinedStrategy,
    BreakoutStrategy
)
from .backtester import Backtester
from .visualizer import Visualizer

__all__ = [
    'DataFetcher',
    'TechnicalIndicators',
    'TradingStrategy',
    'TrendFollowingStrategy',
    'MeanReversionStrategy',
    'MomentumStrategy',
    'CombinedStrategy',
    'BreakoutStrategy',
    'Backtester',
    'Visualizer'
]
