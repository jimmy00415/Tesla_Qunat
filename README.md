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
├── data/                   # Data storage
├── src/
│   ├── data_fetcher.py    # Data collection module
│   ├── indicators.py      # Technical indicators
│   ├── strategies.py      # Trading strategies
│   ├── backtester.py      # Backtesting engine
│   └── visualizer.py      # Visualization tools
├── main.py                # Main execution script
└── requirements.txt       # Dependencies
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

## Performance Metrics

- Total Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor
- Number of Trades

## Disclaimer

This is for educational purposes only. Not financial advice. Always do your own research before trading.
