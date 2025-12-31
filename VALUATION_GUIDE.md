# Tesla Valuation Strategy - Usage Guide

## 🎯 Purpose
This strategy analyzes Tesla stock to determine if it's **overpriced** or **underpriced**, providing **daily LONG/SHORT signals** for trading decisions.

## 📊 How It Works

### Valuation Score System
The strategy generates a score from **-100 to +100**:
- **-100 to -40**: STRONG LONG (Significantly Underpriced) 📈
- **-40 to -20**: LONG (Underpriced) 📈
- **-20 to -10**: WEAK LONG (Slightly Underpriced) 📈
- **-10 to +10**: NEUTRAL (Fairly Valued) ⏸️
- **+10 to +20**: WEAK SHORT (Slightly Overpriced) 📉
- **+20 to +40**: SHORT (Overpriced) 📉
- **+40 to +100**: STRONG SHORT (Significantly Overpriced) 📉

### Analysis Components

#### 1. Statistical Analysis (40% weight)
- **Z-Score**: Measures how many standard deviations the price is from historical mean
- **Moving Averages**: Compares current price to 50-day and 200-day EMAs
- **VWAP**: Volume-weighted average price analysis
- **Bollinger Bands**: Position within upper and lower bands

#### 2. Relative Valuation (40% weight)
- **Historical Percentile**: Where current price ranks in historical distribution
- **52-Week Range**: Position between yearly high and low
- **Distance Analysis**: How far from historical averages

#### 3. Momentum Indicators (10% weight)
- **RSI**: Relative Strength Index (overbought/oversold)
- **Rate of Change**: 10-day and 30-day momentum
- **MACD**: Trend direction and strength

#### 4. Fundamental Metrics (10% weight)
- **P/E Ratio**: Price-to-Earnings compared to sector average
- **PEG Ratio**: P/E to Growth ratio
- **P/B Ratio**: Price-to-Book valuation

## 🚀 Quick Start

### Get Today's Signal
```bash
python daily_signal.py
```

### What You'll Get:
1. **Signal**: LONG, SHORT, or NEUTRAL
2. **Confidence Level**: Very High, High, or Medium
3. **Current Price** vs **Fair Value Estimate**
4. **Support and Resistance Levels**
5. **Key Metrics**: RSI, Z-Score, Percentile Rank
6. **Fundamental Ratios**: P/E, P/B, PEG
7. **Recent Signal History**: Last 10 days

## 📈 Example Output

```
SIGNAL: STRONG SHORT
Valuation Score: 47.70 (Range: -100 to +100)
Confidence: Very High
Recommendation: Significantly overpriced - Strong sell signal

Current Price: $454.43
Fair Value Estimate: $388.82
Current vs Fair Value: +16.88%
```

### Interpretation:
- **Score +47.70**: Strongly overpriced
- **Price 16.88% above fair value**: Significant premium
- **Action**: Consider SHORT position or reducing long exposure

## 🎓 Trading Strategies

### Long Strategy (When Signal = LONG)
1. **Entry**: When valuation score < -20
2. **Target**: Fair value estimate
3. **Stop Loss**: Below 52-week low or lower Bollinger Band
4. **Best Timing**: When RSI < 30 (oversold) and score < -40

### Short Strategy (When Signal = SHORT)
1. **Entry**: When valuation score > +20
2. **Target**: Fair value estimate
3. **Stop Loss**: Above 52-week high or upper Bollinger Band
4. **Best Timing**: When RSI > 70 (overbought) and score > +40

### Neutral Strategy (When Signal = NEUTRAL)
1. **Action**: Hold current positions
2. **Monitor**: Wait for score to move outside -10 to +10 range
3. **Prepare**: Set alerts at fair value ±10%

## ⚠️ Risk Management

### Position Sizing by Confidence
- **Very High Confidence**: Use up to 100% of intended position size
- **High Confidence**: Use 60-80% of intended position size
- **Medium Confidence**: Use 30-50% of intended position size

### Stop Loss Guidelines
- **Long Positions**: Set stop at -15% below entry or at lower BB
- **Short Positions**: Set stop at +15% above entry or at upper BB
- **Trailing Stop**: Use ATR-based trailing stops (2x ATR)

### Diversification
- Never allocate more than 20% of portfolio to single position
- Consider hedging with options when conviction is lower
- Scale in/out of positions rather than all-at-once

## 📊 Performance Metrics

The strategy tracks:
- **Win Rate**: Percentage of profitable signals
- **Average Return**: Mean profit/loss per trade
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst peak-to-trough decline

## 🔄 Daily Routine

### Morning (Pre-Market)
1. Run `python daily_signal.py`
2. Note the signal and confidence level
3. Check if signal changed from previous day
4. Review support/resistance levels

### During Market Hours
1. Monitor price relative to fair value
2. Watch for signal confirmation (volume, momentum)
3. Execute trades based on signal and risk tolerance

### Evening (Post-Market)
1. Log the day's signal and price
2. Track signal accuracy
3. Adjust position sizes based on performance

## 📝 Advanced Usage

### Programmatic Access
```python
from src.valuation_strategy import ValuationStrategy

# Initialize
strategy = ValuationStrategy(symbol='TSLA', lookback_period=252)

# Fetch data
strategy.fetch_comprehensive_data(period='2y')

# Generate signal
signals = strategy.generate_daily_signals()

# Access specific metrics
print(f"Signal: {signals['signal']}")
print(f"Score: {signals['valuation_score']}")
print(f"Fair Value: ${signals['fair_value_estimate']:.2f}")
```

### Historical Analysis
```python
# Get 30 days of historical signals
historical = strategy.create_signal_dataframe(days=30)
print(historical)
```

## 🎯 Signal Accuracy Tips

### High Accuracy Scenarios
- Extreme scores (< -40 or > +40)
- RSI confirms direction (< 30 for long, > 70 for short)
- Price at Bollinger Band extremes
- High volume on signal day

### Lower Accuracy Scenarios
- Scores near neutral (-10 to +10)
- Conflicting momentum indicators
- Low volume environments
- Major news/events pending

## 📚 References

### Key Concepts
- **Z-Score**: Measures standard deviations from mean
- **Percentile Rank**: Historical position (0-100%)
- **Fair Value**: Statistically derived equilibrium price
- **Bollinger Bands**: Volatility-based price channels

### Further Reading
- Technical Analysis of the Financial Markets (Murphy)
- Quantitative Value (Gray & Carlisle)
- Evidence-Based Technical Analysis (Aronson)

## ⚠️ Disclaimer

This strategy is for **educational purposes only**. 

- Not financial advice
- Past performance doesn't guarantee future results
- Always do your own research
- Consider consulting a financial advisor
- Only invest what you can afford to lose

---

**Happy Trading! 📈📉**
