# Tesla Quantitative Trading Analysis Strategy

A comprehensive quantitative trading analysis system for Tesla (TSLA) stock, featuring multiple technical indicators, trading strategies, and backtesting capabilities.

## Features

- **Data Collection**: Automated Tesla stock data fetching
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, ATR, and more
- **Trading Strategies**: 
  - Trend Following Strategy
  - Mean Reversion Strategy
  - Momentum Strategy
  - Combined Multi-Signal Strategy
  - **NEW: Valuation Strategy** - Daily Long/Short signals
- **Valuation Analysis**: Determines if Tesla is overpriced or underpriced
- **Daily Signals**: Automated long/short recommendations with confidence levels
- **Backtesting Engine**: Comprehensive performance evaluation
- **Visualization**: Interactive charts and performance dashboards

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
TeslaQuant/
├── data/                      # Data storage
├── src/
│   ├── data_fetcher.py       # Data collection module
│   ├── indicators.py         # Technical indicators
│   ├── strategies.py         # Trading strategies
│   ├── valuation_strategy.py # Valuation analysis (NEW)
│   ├── backtester.py         # Backtesting engine
│   └── visualizer.py         # Visualization tools
├── main.py                   # Main execution script
├── daily_signal.py           # Daily signal generator (NEW)
└── requirements.txt          # Dependencies
```

## Strategy Overview

### 1. Trend Following Strategy
- Uses moving average crossovers (50/200 day)
- ADX for trend strength confirmation
- Aims to capture major price trends

### 2. Mean Reversion Strategy
- Bollinger Bands for overbought/oversold signals
- RSI confirmation
- Profits from price returning to mean

### 3. Momentum Strategy
- MACD crossovers
- Volume confirmation
- Rate of change analysis

### 4. Valuation Strategy (NEW)
- Statistical fair value calculation
- Z-score analysis
- Historical percentile ranking
- Bollinger Band positioning
- Fundamental metrics (P/E, P/S, P/B)
- Multi-factor valuation scoring
- Daily LONG/SHORT signal generation

## Performance Metrics

- Total Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor
- Number of Trades

## Disclaimer

This is for educational purposes only. Not financial advice. Always do your own research before trading.
