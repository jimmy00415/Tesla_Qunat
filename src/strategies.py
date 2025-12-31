"""
Trading Strategies Module
Implements various quantitative trading strategies for Tesla stock
"""

import pandas as pd
import numpy as np
from indicators import TechnicalIndicators


class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, data, initial_capital=100000):
        """
        Initialize trading strategy
        
        Args:
            data: DataFrame with stock data and indicators
            initial_capital: Starting capital for backtesting
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.positions = None
        self.signals = None
    
    def generate_signals(self):
        """Generate trading signals - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement generate_signals()")
    
    def calculate_positions(self):
        """Calculate positions based on signals"""
        if self.signals is None:
            self.generate_signals()
        
        # Create positions DataFrame
        self.positions = pd.DataFrame(index=self.signals.index)
        self.positions['Signal'] = self.signals['Signal']
        self.positions['Position'] = self.signals['Signal'].fillna(0)
        
        return self.positions


class TrendFollowingStrategy(TradingStrategy):
    """
    Trend Following Strategy
    - Uses moving average crossovers (SMA 50/200)
    - ADX for trend strength confirmation
    - Enters on strong trends, exits on reversals
    """
    
    def generate_signals(self):
        """Generate trend following signals"""
        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['Close'] = self.data['Close']
        self.signals['Signal'] = 0
        
        # Moving average crossover signals
        sma_50 = self.data['SMA_50']
        sma_200 = self.data['SMA_200']
        adx = self.data['ADX']
        
        # Buy signal: Golden Cross + Strong Trend
        buy_condition = (
            (sma_50 > sma_200) &  # Bullish crossover
            (adx > 25) &  # Strong trend
            (self.data['Close'] > sma_50)  # Price above short MA
        )
        
        # Sell signal: Death Cross or Weak Trend
        sell_condition = (
            (sma_50 < sma_200) |  # Bearish crossover
            (adx < 20) |  # Weak trend
            (self.data['Close'] < sma_50)  # Price below short MA
        )
        
        self.signals.loc[buy_condition, 'Signal'] = 1
        self.signals.loc[sell_condition, 'Signal'] = -1
        
        # Generate actual positions (1 = long, 0 = flat, -1 = short if allowed)
        self.signals['Position'] = self.signals['Signal'].replace(-1, 0).fillna(method='ffill')
        
        return self.signals


class MeanReversionStrategy(TradingStrategy):
    """
    Mean Reversion Strategy
    - Uses Bollinger Bands for overbought/oversold conditions
    - RSI confirmation
    - Buys oversold, sells overbought
    """
    
    def generate_signals(self):
        """Generate mean reversion signals"""
        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['Close'] = self.data['Close']
        self.signals['Signal'] = 0
        
        # Bollinger Bands and RSI
        bb_percent = self.data['BB_Percent']
        rsi = self.data['RSI']
        
        # Buy signal: Oversold conditions
        buy_condition = (
            (self.data['Close'] < self.data['BB_Lower']) &  # Below lower band
            (rsi < 30) &  # RSI oversold
            (bb_percent < 0.2)  # Near lower band
        )
        
        # Sell signal: Overbought conditions
        sell_condition = (
            (self.data['Close'] > self.data['BB_Upper']) &  # Above upper band
            (rsi > 70) &  # RSI overbought
            (bb_percent > 0.8)  # Near upper band
        )
        
        # Exit signal: Return to mean
        exit_long = self.data['Close'] > self.data['BB_Middle']
        exit_short = self.data['Close'] < self.data['BB_Middle']
        
        self.signals.loc[buy_condition, 'Signal'] = 1
        self.signals.loc[sell_condition, 'Signal'] = -1
        
        # Create positions with exits
        position = 0
        positions = []
        for i in range(len(self.signals)):
            signal = self.signals['Signal'].iloc[i]
            
            if signal == 1:
                position = 1
            elif signal == -1:
                position = 0
            elif position == 1 and exit_long.iloc[i]:
                position = 0
            
            positions.append(position)
        
        self.signals['Position'] = positions
        
        return self.signals


class MomentumStrategy(TradingStrategy):
    """
    Momentum Strategy
    - MACD crossovers
    - Volume confirmation
    - Rate of change analysis
    """
    
    def generate_signals(self):
        """Generate momentum signals"""
        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['Close'] = self.data['Close']
        self.signals['Signal'] = 0
        
        # MACD signals
        macd = self.data['MACD']
        macd_signal = self.data['MACD_Signal']
        roc = self.data['ROC_10']
        volume_ratio = self.data['Volume'] / self.data['Volume_MA']
        
        # Buy signal: Bullish momentum
        buy_condition = (
            (macd > macd_signal) &  # MACD bullish
            (macd.shift(1) <= macd_signal.shift(1)) &  # Fresh crossover
            (roc > 0) &  # Positive rate of change
            (volume_ratio > 1.2)  # Above average volume
        )
        
        # Sell signal: Bearish momentum
        sell_condition = (
            (macd < macd_signal) &  # MACD bearish
            (macd.shift(1) >= macd_signal.shift(1)) &  # Fresh crossover
            (roc < 0)  # Negative rate of change
        )
        
        self.signals.loc[buy_condition, 'Signal'] = 1
        self.signals.loc[sell_condition, 'Signal'] = -1
        
        # Generate positions
        self.signals['Position'] = self.signals['Signal'].replace(-1, 0).fillna(method='ffill')
        
        return self.signals


class CombinedStrategy(TradingStrategy):
    """
    Combined Multi-Signal Strategy
    - Combines signals from multiple strategies
    - Weighted voting system
    - Risk management filters
    """
    
    def __init__(self, data, initial_capital=100000, min_signals=2):
        """
        Initialize combined strategy
        
        Args:
            data: DataFrame with stock data and indicators
            initial_capital: Starting capital
            min_signals: Minimum number of agreeing signals to trade
        """
        super().__init__(data, initial_capital)
        self.min_signals = min_signals
    
    def generate_signals(self):
        """Generate combined signals from multiple strategies"""
        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['Close'] = self.data['Close']
        
        # Get signals from individual strategies
        trend_strategy = TrendFollowingStrategy(self.data)
        trend_signals = trend_strategy.generate_signals()
        
        mean_reversion_strategy = MeanReversionStrategy(self.data)
        mean_reversion_signals = mean_reversion_strategy.generate_signals()
        
        momentum_strategy = MomentumStrategy(self.data)
        momentum_signals = momentum_strategy.generate_signals()
        
        # Combine signals (voting system)
        self.signals['Trend_Signal'] = trend_signals['Signal']
        self.signals['MeanRev_Signal'] = mean_reversion_signals['Signal']
        self.signals['Momentum_Signal'] = momentum_signals['Signal']
        
        # Count buy signals (1 = buy, -1 = sell/exit, 0 = hold)
        buy_votes = (
            (self.signals['Trend_Signal'] == 1).astype(int) +
            (self.signals['MeanRev_Signal'] == 1).astype(int) +
            (self.signals['Momentum_Signal'] == 1).astype(int)
        )
        
        sell_votes = (
            (self.signals['Trend_Signal'] == -1).astype(int) +
            (self.signals['MeanRev_Signal'] == -1).astype(int) +
            (self.signals['Momentum_Signal'] == -1).astype(int)
        )
        
        # Generate final signal based on voting
        self.signals['Buy_Votes'] = buy_votes
        self.signals['Sell_Votes'] = sell_votes
        self.signals['Signal'] = 0
        
        # Buy when enough strategies agree
        self.signals.loc[buy_votes >= self.min_signals, 'Signal'] = 1
        # Sell when enough strategies agree
        self.signals.loc[sell_votes >= self.min_signals, 'Signal'] = -1
        
        # Generate positions
        self.signals['Position'] = self.signals['Signal'].replace(-1, 0).fillna(method='ffill')
        
        # Add risk management: ATR-based stop loss
        atr = self.data['ATR']
        self.signals['Stop_Loss'] = self.signals['Close'] - (2 * atr)
        self.signals['Take_Profit'] = self.signals['Close'] + (3 * atr)
        
        return self.signals


class BreakoutStrategy(TradingStrategy):
    """
    Breakout Strategy
    - Identifies consolidation periods
    - Trades breakouts with volume confirmation
    """
    
    def generate_signals(self):
        """Generate breakout signals"""
        self.signals = pd.DataFrame(index=self.data.index)
        self.signals['Close'] = self.data['Close']
        self.signals['Signal'] = 0
        
        # Calculate 20-day high/low
        high_20 = self.data['High'].rolling(20).max()
        low_20 = self.data['Low'].rolling(20).min()
        
        volume_ratio = self.data['Volume'] / self.data['Volume_MA']
        bb_squeeze = self.data['BB_Squeeze']
        
        # Buy signal: Upside breakout
        buy_condition = (
            (self.data['Close'] > high_20.shift(1)) &  # Break above 20-day high
            (volume_ratio > 1.5) &  # High volume
            (bb_squeeze.shift(5))  # Recent squeeze
        )
        
        # Sell signal: Downside break
        sell_condition = (
            (self.data['Close'] < low_20.shift(1)) |  # Break below 20-day low
            (self.data['Close'] < self.data['SMA_20'])  # Below 20-day MA
        )
        
        self.signals.loc[buy_condition, 'Signal'] = 1
        self.signals.loc[sell_condition, 'Signal'] = -1
        
        # Generate positions
        self.signals['Position'] = self.signals['Signal'].replace(-1, 0).fillna(method='ffill')
        
        return self.signals


if __name__ == "__main__":
    # Test strategies
    from data_fetcher import DataFetcher
    
    print("Testing Trading Strategies...\n")
    
    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch_data(period='2y')
    
    # Add indicators
    indicators = TechnicalIndicators(data)
    data = indicators.add_all_indicators()
    data = indicators.add_custom_signals()
    
    # Test each strategy
    strategies = [
        ('Trend Following', TrendFollowingStrategy),
        ('Mean Reversion', MeanReversionStrategy),
        ('Momentum', MomentumStrategy),
        ('Combined', CombinedStrategy),
        ('Breakout', BreakoutStrategy)
    ]
    
    for name, StrategyClass in strategies:
        strategy = StrategyClass(data)
        signals = strategy.generate_signals()
        total_signals = (signals['Signal'] != 0).sum()
        buy_signals = (signals['Signal'] == 1).sum()
        sell_signals = (signals['Signal'] == -1).sum()
        
        print(f"{name} Strategy:")
        print(f"  Total signals: {total_signals}")
        print(f"  Buy signals: {buy_signals}")
        print(f"  Sell signals: {sell_signals}")
        print()
