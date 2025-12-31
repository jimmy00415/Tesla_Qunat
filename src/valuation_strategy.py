"""
Valuation Strategy Module
Advanced quantitative strategy to determine if Tesla is overpriced or underpriced
Provides daily long/short signals based on multiple valuation metrics
"""

import pandas as pd
import numpy as np
from scipy import stats
import yfinance as yf
from datetime import datetime, timedelta


class ValuationStrategy:
    """
    Comprehensive valuation analysis strategy
    Combines multiple approaches to determine fair value and generate trading signals
    """
    
    def __init__(self, symbol='TSLA', lookback_period=252):
        """
        Initialize valuation strategy
        
        Args:
            symbol: Stock symbol (default: TSLA)
            lookback_period: Number of days for historical analysis (default: 252 = 1 year)
        """
        self.symbol = symbol
        self.lookback_period = lookback_period
        self.data = None
        self.ticker_info = None
        self.signals = None
        
    def fetch_comprehensive_data(self, period='2y'):
        """Fetch stock data and fundamental information"""
        print(f"Fetching comprehensive data for {self.symbol}...")
        
        # Fetch price data
        ticker = yf.Ticker(self.symbol)
        self.data = ticker.history(period=period)
        
        # Fetch fundamental data
        try:
            self.ticker_info = ticker.info
            print(f"✓ Fetched {len(self.data)} days of price data")
            print(f"✓ Retrieved fundamental metrics")
        except Exception as e:
            print(f"Warning: Could not fetch all fundamental data - {e}")
            self.ticker_info = {}
        
        return self.data
    
    def calculate_statistical_fair_value(self):
        """Calculate fair value using statistical methods"""
        
        # Method 1: Mean Reversion (Historical Average)
        lookback = min(self.lookback_period, len(self.data))
        historical_avg = self.data['Close'].tail(lookback).mean()
        
        # Method 2: Bollinger Bands Mean
        sma_20 = self.data['Close'].rolling(20).mean()
        std_20 = self.data['Close'].rolling(20).std()
        bb_upper = sma_20 + (2 * std_20)
        bb_lower = sma_20 - (2 * std_20)
        bb_middle = sma_20
        
        # Method 3: Exponential Moving Average
        ema_50 = self.data['Close'].ewm(span=50).mean()
        ema_200 = self.data['Close'].ewm(span=200).mean()
        
        # Method 4: Volume Weighted Average Price
        vwap = (self.data['Close'] * self.data['Volume']).cumsum() / self.data['Volume'].cumsum()
        
        # Calculate Z-Score (how many standard deviations from mean)
        current_price = self.data['Close'].iloc[-1]
        mean_price = self.data['Close'].tail(lookback).mean()
        std_price = self.data['Close'].tail(lookback).std()
        z_score = (current_price - mean_price) / std_price if std_price != 0 else 0
        
        return {
            'historical_avg': historical_avg,
            'bb_middle': bb_middle.iloc[-1],
            'bb_upper': bb_upper.iloc[-1],
            'bb_lower': bb_lower.iloc[-1],
            'ema_50': ema_50.iloc[-1],
            'ema_200': ema_200.iloc[-1],
            'vwap': vwap.iloc[-1],
            'z_score': z_score,
            'current_price': current_price
        }
    
    def calculate_fundamental_metrics(self):
        """Calculate valuation metrics from fundamentals"""
        metrics = {}
        
        if not self.ticker_info:
            return metrics
        
        # Price-to-Earnings Ratio
        pe_ratio = self.ticker_info.get('trailingPE', None)
        forward_pe = self.ticker_info.get('forwardPE', None)
        
        # Price-to-Sales Ratio
        ps_ratio = self.ticker_info.get('priceToSalesTrailing12Months', None)
        
        # Price-to-Book Ratio
        pb_ratio = self.ticker_info.get('priceToBook', None)
        
        # PEG Ratio (PE / Growth Rate)
        peg_ratio = self.ticker_info.get('pegRatio', None)
        
        # Market Cap
        market_cap = self.ticker_info.get('marketCap', None)
        
        # Enterprise Value
        enterprise_value = self.ticker_info.get('enterpriseValue', None)
        
        # EV/EBITDA
        ev_to_ebitda = self.ticker_info.get('enterpriseToEbitda', None)
        
        # Profit Margins
        profit_margin = self.ticker_info.get('profitMargins', None)
        
        # Return on Equity
        roe = self.ticker_info.get('returnOnEquity', None)
        
        metrics = {
            'pe_ratio': pe_ratio,
            'forward_pe': forward_pe,
            'ps_ratio': ps_ratio,
            'pb_ratio': pb_ratio,
            'peg_ratio': peg_ratio,
            'market_cap': market_cap,
            'enterprise_value': enterprise_value,
            'ev_to_ebitda': ev_to_ebitda,
            'profit_margin': profit_margin,
            'roe': roe
        }
        
        return metrics
    
    def calculate_relative_valuation(self):
        """Calculate valuation relative to historical ranges"""
        
        # Calculate historical percentile
        lookback = min(self.lookback_period, len(self.data))
        historical_prices = self.data['Close'].tail(lookback)
        current_price = self.data['Close'].iloc[-1]
        
        # Percentile rank (0-100)
        percentile = stats.percentileofscore(historical_prices, current_price)
        
        # Calculate distance from 52-week high/low
        high_52w = self.data['High'].tail(252).max()
        low_52w = self.data['Low'].tail(252).min()
        
        distance_from_high = ((high_52w - current_price) / high_52w) * 100
        distance_from_low = ((current_price - low_52w) / low_52w) * 100
        
        # Position in 52-week range (0-100)
        range_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100 if high_52w != low_52w else 50
        
        return {
            'percentile': percentile,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'distance_from_high_pct': distance_from_high,
            'distance_from_low_pct': distance_from_low,
            'range_position': range_position
        }
    
    def calculate_momentum_indicators(self):
        """Calculate momentum and trend indicators"""
        
        # Rate of Change
        roc_10 = ((self.data['Close'].iloc[-1] - self.data['Close'].iloc[-11]) / 
                  self.data['Close'].iloc[-11] * 100) if len(self.data) > 10 else 0
        roc_30 = ((self.data['Close'].iloc[-1] - self.data['Close'].iloc[-31]) / 
                  self.data['Close'].iloc[-31] * 100) if len(self.data) > 30 else 0
        
        # RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = self.data['Close'].ewm(span=12).mean()
        ema_26 = self.data['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        
        return {
            'roc_10d': roc_10,
            'roc_30d': roc_30,
            'rsi': rsi.iloc[-1],
            'macd': macd.iloc[-1],
            'macd_signal': macd_signal.iloc[-1]
        }
    
    def generate_valuation_score(self):
        """
        Generate comprehensive valuation score
        Returns score from -100 (extremely underpriced) to +100 (extremely overpriced)
        """
        
        scores = []
        weights = []
        
        # Statistical Fair Value Analysis
        stat_metrics = self.calculate_statistical_fair_value()
        current_price = stat_metrics['current_price']
        
        # Score 1: Z-Score Analysis (-3 to +3 normalized)
        z_score = stat_metrics['z_score']
        z_score_normalized = np.clip(z_score * 33.33, -100, 100)  # Convert to -100 to +100
        scores.append(z_score_normalized)
        weights.append(2.0)  # High weight
        
        # Score 2: Distance from Moving Averages
        avg_fair_value = np.mean([
            stat_metrics['historical_avg'],
            stat_metrics['bb_middle'],
            stat_metrics['ema_50'],
            stat_metrics['vwap']
        ])
        price_vs_fair = ((current_price - avg_fair_value) / avg_fair_value) * 100
        price_vs_fair_normalized = np.clip(price_vs_fair * 2, -100, 100)
        scores.append(price_vs_fair_normalized)
        weights.append(1.5)
        
        # Score 3: Bollinger Band Position
        bb_upper = stat_metrics['bb_upper']
        bb_lower = stat_metrics['bb_lower']
        bb_middle = stat_metrics['bb_middle']
        
        if bb_upper != bb_lower:
            bb_position = ((current_price - bb_middle) / (bb_upper - bb_lower)) * 100
            bb_score = np.clip(bb_position * 2, -100, 100)
            scores.append(bb_score)
            weights.append(1.5)
        
        # Score 4: Relative Valuation (Percentile)
        rel_metrics = self.calculate_relative_valuation()
        percentile_score = (rel_metrics['percentile'] - 50) * 2  # Convert 0-100 to -100 to +100
        scores.append(percentile_score)
        weights.append(2.0)  # High weight
        
        # Score 5: 52-Week Range Position
        range_score = (rel_metrics['range_position'] - 50) * 2
        scores.append(range_score)
        weights.append(1.0)
        
        # Score 6: Momentum Analysis
        momentum = self.calculate_momentum_indicators()
        
        # RSI score (>70 overvalued, <30 undervalued)
        rsi_score = (momentum['rsi'] - 50) * 2
        scores.append(np.clip(rsi_score, -100, 100))
        weights.append(1.0)
        
        # Score 7: Fundamental PE Ratio (if available)
        fund_metrics = self.calculate_fundamental_metrics()
        
        if fund_metrics.get('pe_ratio'):
            # Compare to market average (~20) and sector average (~30 for tech)
            pe_ratio = fund_metrics['pe_ratio']
            if pe_ratio > 0:
                # Score based on deviation from reasonable PE
                reasonable_pe = 25  # Conservative for growth stock
                pe_deviation = ((pe_ratio - reasonable_pe) / reasonable_pe) * 100
                pe_score = np.clip(pe_deviation, -100, 100)
                scores.append(pe_score)
                weights.append(1.5)
        
        # Calculate weighted average score
        if scores:
            weighted_score = np.average(scores, weights=weights[:len(scores)])
        else:
            weighted_score = 0
        
        return weighted_score, scores, weights[:len(scores)]
    
    def generate_daily_signals(self):
        """
        Generate daily long/short signals based on valuation analysis
        
        Returns:
            DataFrame with signals and detailed analysis
        """
        
        # Fetch latest data
        if self.data is None:
            self.fetch_comprehensive_data()
        
        # Calculate all metrics
        valuation_score, component_scores, weights = self.generate_valuation_score()
        stat_metrics = self.calculate_statistical_fair_value()
        fund_metrics = self.calculate_fundamental_metrics()
        rel_metrics = self.calculate_relative_valuation()
        momentum = self.calculate_momentum_indicators()
        
        # Generate signal based on valuation score
        # Score: -100 (underpriced) to +100 (overpriced)
        
        if valuation_score <= -40:
            signal = "STRONG LONG"
            recommendation = "Significantly underpriced - Strong buy signal"
            confidence = "Very High"
        elif -40 < valuation_score <= -20:
            signal = "LONG"
            recommendation = "Underpriced - Buy signal"
            confidence = "High"
        elif -20 < valuation_score <= -10:
            signal = "WEAK LONG"
            recommendation = "Slightly underpriced - Weak buy signal"
            confidence = "Medium"
        elif -10 < valuation_score < 10:
            signal = "NEUTRAL"
            recommendation = "Fairly valued - Hold position"
            confidence = "Medium"
        elif 10 <= valuation_score < 20:
            signal = "WEAK SHORT"
            recommendation = "Slightly overpriced - Weak sell signal"
            confidence = "Medium"
        elif 20 <= valuation_score < 40:
            signal = "SHORT"
            recommendation = "Overpriced - Sell signal"
            confidence = "High"
        else:
            signal = "STRONG SHORT"
            recommendation = "Significantly overpriced - Strong sell signal"
            confidence = "Very High"
        
        # Create detailed signal report
        self.signals = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'current_price': stat_metrics['current_price'],
            'signal': signal,
            'valuation_score': valuation_score,
            'confidence': confidence,
            'recommendation': recommendation,
            
            # Statistical Metrics
            'fair_value_estimate': np.mean([
                stat_metrics['historical_avg'],
                stat_metrics['bb_middle'],
                stat_metrics['ema_50'],
                stat_metrics['vwap']
            ]),
            'z_score': stat_metrics['z_score'],
            'bb_upper': stat_metrics['bb_upper'],
            'bb_lower': stat_metrics['bb_lower'],
            
            # Relative Valuation
            'percentile_rank': rel_metrics['percentile'],
            '52w_high': rel_metrics['high_52w'],
            '52w_low': rel_metrics['low_52w'],
            'range_position_pct': rel_metrics['range_position'],
            
            # Momentum
            'rsi': momentum['rsi'],
            'roc_10d': momentum['roc_10d'],
            'roc_30d': momentum['roc_30d'],
            
            # Fundamentals
            'pe_ratio': fund_metrics.get('pe_ratio'),
            'forward_pe': fund_metrics.get('forward_pe'),
            'peg_ratio': fund_metrics.get('peg_ratio'),
            'pb_ratio': fund_metrics.get('pb_ratio'),
            
            # Component Scores
            'component_scores': component_scores,
            'weights': weights
        }
        
        return self.signals
    
    def print_signal_report(self):
        """Print detailed signal report"""
        
        if self.signals is None:
            self.generate_daily_signals()
        
        s = self.signals
        
        print("\n" + "="*80)
        print("TESLA VALUATION ANALYSIS - DAILY SIGNAL REPORT")
        print("="*80)
        
        print(f"\nDate: {s['date']}")
        print(f"Current Price: ${s['current_price']:.2f}")
        print(f"\n{'='*80}")
        print(f"SIGNAL: {s['signal']}")
        print(f"Valuation Score: {s['valuation_score']:.2f} (Range: -100 to +100)")
        print(f"Confidence: {s['confidence']}")
        print(f"Recommendation: {s['recommendation']}")
        print(f"{'='*80}")
        
        print("\n--- VALUATION METRICS ---")
        print(f"Fair Value Estimate:    ${s['fair_value_estimate']:.2f}")
        print(f"Current vs Fair Value:  {((s['current_price'] - s['fair_value_estimate']) / s['fair_value_estimate'] * 100):+.2f}%")
        print(f"Z-Score:                {s['z_score']:.2f} (σ from mean)")
        print(f"Historical Percentile:  {s['percentile_rank']:.1f}th percentile")
        
        print("\n--- PRICE RANGE ANALYSIS ---")
        print(f"52-Week High:           ${s['52w_high']:.2f}")
        print(f"52-Week Low:            ${s['52w_low']:.2f}")
        print(f"Current Position:       {s['range_position_pct']:.1f}% of 52-week range")
        print(f"Bollinger Band Upper:   ${s['bb_upper']:.2f}")
        print(f"Bollinger Band Lower:   ${s['bb_lower']:.2f}")
        
        print("\n--- MOMENTUM INDICATORS ---")
        print(f"RSI (14):               {s['rsi']:.2f}", end="")
        if s['rsi'] > 70:
            print(" (Overbought)")
        elif s['rsi'] < 30:
            print(" (Oversold)")
        else:
            print(" (Neutral)")
        print(f"10-Day ROC:             {s['roc_10d']:+.2f}%")
        print(f"30-Day ROC:             {s['roc_30d']:+.2f}%")
        
        if s['pe_ratio']:
            print("\n--- FUNDAMENTAL METRICS ---")
            print(f"P/E Ratio:              {s['pe_ratio']:.2f}")
            if s['forward_pe']:
                print(f"Forward P/E:            {s['forward_pe']:.2f}")
            if s['peg_ratio']:
                print(f"PEG Ratio:              {s['peg_ratio']:.2f}")
            if s['pb_ratio']:
                print(f"P/B Ratio:              {s['pb_ratio']:.2f}")
        
        print("\n--- SIGNAL INTERPRETATION ---")
        if s['valuation_score'] < -20:
            print("✓ Price is trading below fair value")
            print("✓ Good risk/reward ratio for long positions")
            print("✓ Consider accumulating or adding to positions")
        elif s['valuation_score'] > 20:
            print("⚠ Price is trading above fair value")
            print("⚠ Limited upside, elevated downside risk")
            print("⚠ Consider reducing exposure or shorting")
        else:
            print("● Price is near fair value")
            print("● Wait for better entry points")
            print("● Monitor for breakout or breakdown")
        
        print("\n" + "="*80 + "\n")
    
    def create_signal_dataframe(self, days=30):
        """
        Create historical signals for multiple days
        
        Args:
            days: Number of historical days to analyze
        """
        
        signals_list = []
        
        # Get historical data
        lookback = min(days + self.lookback_period, len(self.data))
        
        for i in range(lookback - days, lookback):
            if i < 0:
                continue
            
            # Use data up to day i
            temp_data = self.data.iloc[:i+1].copy()
            
            if len(temp_data) < 50:  # Need minimum data
                continue
            
            # Calculate metrics for that day
            current_price = temp_data['Close'].iloc[-1]
            
            # Simple valuation score based on percentile
            recent_prices = temp_data['Close'].tail(min(252, len(temp_data)))
            percentile = stats.percentileofscore(recent_prices, current_price)
            simple_score = (percentile - 50) * 2
            
            # Generate signal
            if simple_score <= -40:
                signal = "STRONG LONG"
            elif -40 < simple_score <= -20:
                signal = "LONG"
            elif -20 < simple_score <= -10:
                signal = "WEAK LONG"
            elif -10 < simple_score < 10:
                signal = "NEUTRAL"
            elif 10 <= simple_score < 20:
                signal = "WEAK SHORT"
            elif 20 <= simple_score < 40:
                signal = "SHORT"
            else:
                signal = "STRONG SHORT"
            
            signals_list.append({
                'Date': temp_data.index[-1],
                'Price': current_price,
                'Valuation_Score': simple_score,
                'Signal': signal,
                'Percentile': percentile
            })
        
        return pd.DataFrame(signals_list)


if __name__ == "__main__":
    print("Tesla Valuation Strategy - Testing\n")
    
    # Initialize strategy
    strategy = ValuationStrategy(symbol='TSLA')
    
    # Fetch data
    strategy.fetch_comprehensive_data(period='2y')
    
    # Generate daily signal
    strategy.generate_daily_signals()
    
    # Print detailed report
    strategy.print_signal_report()
    
    # Show historical signals
    print("Generating historical signals...")
    historical_signals = strategy.create_signal_dataframe(days=30)
    print("\nLast 10 Days Signals:")
    print(historical_signals.tail(10).to_string(index=False))
