"""
Technical Indicators Module
Calculates various technical indicators for trading analysis
"""

import pandas as pd
import numpy as np
from ta.trend import MACD, ADXIndicator, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice


class TechnicalIndicators:
    """Calculate technical indicators for stock data"""
    
    def __init__(self, data):
        """
        Initialize with stock data
        
        Args:
            data: DataFrame with OHLCV data
        """
        self.data = data.copy()
    
    def add_all_indicators(self):
        """Add all technical indicators to the dataframe"""
        self.add_moving_averages()
        self.add_rsi()
        self.add_macd()
        self.add_bollinger_bands()
        self.add_atr()
        self.add_adx()
        self.add_stochastic()
        self.add_obv()
        self.add_vwap()
        self.add_rate_of_change()
        return self.data
    
    def add_moving_averages(self, periods=[10, 20, 50, 100, 200]):
        """
        Add Simple and Exponential Moving Averages
        
        Args:
            periods: List of periods for moving averages
        """
        for period in periods:
            # Simple Moving Average
            self.data[f'SMA_{period}'] = SMAIndicator(
                close=self.data['Close'], 
                window=period
            ).sma_indicator()
            
            # Exponential Moving Average
            self.data[f'EMA_{period}'] = EMAIndicator(
                close=self.data['Close'], 
                window=period
            ).ema_indicator()
        
        return self.data
    
    def add_rsi(self, period=14):
        """
        Add Relative Strength Index
        
        Args:
            period: RSI period (default: 14)
        """
        rsi = RSIIndicator(close=self.data['Close'], window=period)
        self.data['RSI'] = rsi.rsi()
        
        # Add overbought/oversold signals
        self.data['RSI_Overbought'] = self.data['RSI'] > 70
        self.data['RSI_Oversold'] = self.data['RSI'] < 30
        
        return self.data
    
    def add_macd(self, fast=12, slow=26, signal=9):
        """
        Add MACD (Moving Average Convergence Divergence)
        
        Args:
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        """
        macd = MACD(
            close=self.data['Close'],
            window_fast=fast,
            window_slow=slow,
            window_sign=signal
        )
        
        self.data['MACD'] = macd.macd()
        self.data['MACD_Signal'] = macd.macd_signal()
        self.data['MACD_Histogram'] = macd.macd_diff()
        
        # Add crossover signals
        self.data['MACD_Bullish'] = (
            (self.data['MACD'] > self.data['MACD_Signal']) & 
            (self.data['MACD'].shift(1) <= self.data['MACD_Signal'].shift(1))
        )
        self.data['MACD_Bearish'] = (
            (self.data['MACD'] < self.data['MACD_Signal']) & 
            (self.data['MACD'].shift(1) >= self.data['MACD_Signal'].shift(1))
        )
        
        return self.data
    
    def add_bollinger_bands(self, period=20, std_dev=2):
        """
        Add Bollinger Bands
        
        Args:
            period: Moving average period
            std_dev: Number of standard deviations
        """
        bb = BollingerBands(
            close=self.data['Close'],
            window=period,
            window_dev=std_dev
        )
        
        self.data['BB_Upper'] = bb.bollinger_hband()
        self.data['BB_Middle'] = bb.bollinger_mavg()
        self.data['BB_Lower'] = bb.bollinger_lband()
        self.data['BB_Width'] = bb.bollinger_wband()
        self.data['BB_Percent'] = bb.bollinger_pband()
        
        # Add signals
        self.data['BB_Squeeze'] = self.data['BB_Width'] < self.data['BB_Width'].rolling(20).mean()
        self.data['BB_Above_Upper'] = self.data['Close'] > self.data['BB_Upper']
        self.data['BB_Below_Lower'] = self.data['Close'] < self.data['BB_Lower']
        
        return self.data
    
    def add_atr(self, period=14):
        """
        Add Average True Range (volatility indicator)
        
        Args:
            period: ATR period
        """
        atr = AverageTrueRange(
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            window=period
        )
        
        self.data['ATR'] = atr.average_true_range()
        self.data['ATR_Percent'] = (self.data['ATR'] / self.data['Close']) * 100
        
        return self.data
    
    def add_adx(self, period=14):
        """
        Add Average Directional Index (trend strength)
        
        Args:
            period: ADX period
        """
        adx = ADXIndicator(
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            window=period
        )
        
        self.data['ADX'] = adx.adx()
        self.data['ADX_Pos'] = adx.adx_pos()
        self.data['ADX_Neg'] = adx.adx_neg()
        
        # Trend strength signals
        self.data['Strong_Trend'] = self.data['ADX'] > 25
        self.data['Very_Strong_Trend'] = self.data['ADX'] > 50
        
        return self.data
    
    def add_stochastic(self, period=14, smooth=3):
        """
        Add Stochastic Oscillator
        
        Args:
            period: Lookback period
            smooth: Smoothing period
        """
        stoch = StochasticOscillator(
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            window=period,
            smooth_window=smooth
        )
        
        self.data['Stoch_K'] = stoch.stoch()
        self.data['Stoch_D'] = stoch.stoch_signal()
        
        # Overbought/oversold
        self.data['Stoch_Overbought'] = self.data['Stoch_K'] > 80
        self.data['Stoch_Oversold'] = self.data['Stoch_K'] < 20
        
        return self.data
    
    def add_obv(self):
        """Add On Balance Volume (volume indicator)"""
        obv = OnBalanceVolumeIndicator(
            close=self.data['Close'],
            volume=self.data['Volume']
        )
        
        self.data['OBV'] = obv.on_balance_volume()
        self.data['OBV_MA'] = self.data['OBV'].rolling(20).mean()
        
        return self.data
    
    def add_vwap(self):
        """Add Volume Weighted Average Price"""
        try:
            vwap = VolumeWeightedAveragePrice(
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                volume=self.data['Volume']
            )
            self.data['VWAP'] = vwap.volume_weighted_average_price()
        except:
            # Fallback calculation
            self.data['VWAP'] = (
                (self.data['Close'] * self.data['Volume']).cumsum() / 
                self.data['Volume'].cumsum()
            )
        
        return self.data
    
    def add_rate_of_change(self, period=10):
        """
        Add Rate of Change (momentum indicator)
        
        Args:
            period: Period for ROC calculation
        """
        self.data[f'ROC_{period}'] = (
            (self.data['Close'] - self.data['Close'].shift(period)) / 
            self.data['Close'].shift(period) * 100
        )
        
        return self.data
    
    def add_custom_signals(self):
        """Add custom trading signals based on multiple indicators"""
        
        # Golden Cross / Death Cross
        self.data['Golden_Cross'] = (
            (self.data['SMA_50'] > self.data['SMA_200']) & 
            (self.data['SMA_50'].shift(1) <= self.data['SMA_200'].shift(1))
        )
        self.data['Death_Cross'] = (
            (self.data['SMA_50'] < self.data['SMA_200']) & 
            (self.data['SMA_50'].shift(1) >= self.data['SMA_200'].shift(1))
        )
        
        # Price vs Moving Average signals
        self.data['Price_Above_SMA50'] = self.data['Close'] > self.data['SMA_50']
        self.data['Price_Above_SMA200'] = self.data['Close'] > self.data['SMA_200']
        
        # Volume signals
        self.data['Volume_MA'] = self.data['Volume'].rolling(20).mean()
        self.data['High_Volume'] = self.data['Volume'] > self.data['Volume_MA'] * 1.5
        
        # Momentum signals
        self.data['Positive_Momentum'] = (
            (self.data['RSI'] > 50) & 
            (self.data['MACD'] > self.data['MACD_Signal']) &
            (self.data['Close'] > self.data['SMA_20'])
        )
        
        self.data['Negative_Momentum'] = (
            (self.data['RSI'] < 50) & 
            (self.data['MACD'] < self.data['MACD_Signal']) &
            (self.data['Close'] < self.data['SMA_20'])
        )
        
        return self.data
    
    def get_current_signals(self):
        """Get current trading signals"""
        if len(self.data) == 0:
            return None
        
        latest = self.data.iloc[-1]
        
        signals = {
            'Date': self.data.index[-1],
            'Close': latest['Close'],
            'RSI': latest.get('RSI', None),
            'MACD': latest.get('MACD', None),
            'MACD_Signal': latest.get('MACD_Signal', None),
            'BB_Position': latest.get('BB_Percent', None),
            'ADX': latest.get('ADX', None),
            'Price_vs_SMA50': 'Above' if latest.get('Price_Above_SMA50', False) else 'Below',
            'Price_vs_SMA200': 'Above' if latest.get('Price_Above_SMA200', False) else 'Below',
            'Trend': 'Strong' if latest.get('Strong_Trend', False) else 'Weak',
        }
        
        return signals


if __name__ == "__main__":
    # Test the indicators
    from data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    data = fetcher.fetch_data(period='1y')
    
    indicators = TechnicalIndicators(data)
    data_with_indicators = indicators.add_all_indicators()
    indicators.add_custom_signals()
    
    print("\nIndicators calculated successfully!")
    print(f"Total columns: {len(data_with_indicators.columns)}")
    print(f"\nLatest signals:")
    current_signals = indicators.get_current_signals()
    for key, value in current_signals.items():
        print(f"{key}: {value}")
