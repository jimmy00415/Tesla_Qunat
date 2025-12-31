"""
Tesla Quantitative Trading Analysis - Main Script
Run complete analysis pipeline with multiple strategies
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_fetcher import DataFetcher
from src.indicators import TechnicalIndicators
from src.strategies import (
    TrendFollowingStrategy,
    MeanReversionStrategy,
    MomentumStrategy,
    CombinedStrategy,
    BreakoutStrategy
)
from src.backtester import Backtester
from src.visualizer import Visualizer
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def main():
    """Main execution function"""
    
    print_header("TESLA QUANTITATIVE TRADING ANALYSIS")
    
    # Configuration
    SYMBOL = 'TSLA'
    PERIOD = '2y'  # 2 years of data
    INITIAL_CAPITAL = 100000
    COMMISSION = 0.001  # 0.1%
    
    print(f"Symbol: {SYMBOL}")
    print(f"Period: {PERIOD}")
    print(f"Initial Capital: ${INITIAL_CAPITAL:,}")
    print(f"Commission Rate: {COMMISSION*100}%")
    
    # Step 1: Fetch Data
    print_header("STEP 1: FETCHING DATA")
    fetcher = DataFetcher(symbol=SYMBOL)
    data = fetcher.fetch_data(period=PERIOD, save=True)
    
    if data is None or len(data) == 0:
        print("Error: Unable to fetch data. Exiting.")
        return
    
    fetcher.summary()
    
    # Step 2: Calculate Technical Indicators
    print_header("STEP 2: CALCULATING TECHNICAL INDICATORS")
    indicators = TechnicalIndicators(data)
    data = indicators.add_all_indicators()
    data = indicators.add_custom_signals()
    
    print(f"✓ Added {len(data.columns) - 6} technical indicators")
    
    # Display current signals
    current_signals = indicators.get_current_signals()
    print("\nCurrent Market Signals:")
    for key, value in current_signals.items():
        print(f"  {key}: {value}")
    
    # Step 3: Test Multiple Strategies
    print_header("STEP 3: TESTING TRADING STRATEGIES")
    
    strategies_dict = {
        'Trend Following': TrendFollowingStrategy(data),
        'Mean Reversion': MeanReversionStrategy(data),
        'Momentum': MomentumStrategy(data),
        'Combined': CombinedStrategy(data),
        'Breakout': BreakoutStrategy(data)
    }
    
    # Generate signals for each strategy
    signals_dict = {}
    for name, strategy in strategies_dict.items():
        print(f"\nGenerating signals for {name} strategy...")
        signals = strategy.generate_signals()
        signals_dict[name] = signals
        
        total_signals = (signals['Signal'] != 0).sum()
        buy_signals = (signals['Signal'] == 1).sum()
        sell_signals = (signals['Signal'] == -1).sum()
        
        print(f"  Total signals: {total_signals}")
        print(f"  Buy signals: {buy_signals}")
        print(f"  Sell signals: {sell_signals}")
    
    # Step 4: Backtest Each Strategy
    print_header("STEP 4: BACKTESTING STRATEGIES")
    
    backtest_results = {}
    
    for name, signals in signals_dict.items():
        print(f"\nBacktesting {name} Strategy...")
        backtester = Backtester(data, signals, INITIAL_CAPITAL, COMMISSION)
        portfolio = backtester.run_backtest()
        metrics = backtester.calculate_metrics()
        
        backtest_results[name] = {
            'backtester': backtester,
            'portfolio': portfolio,
            'metrics': metrics
        }
        
        # Print brief summary
        print(f"  Final Value: ${metrics['Final Portfolio Value']:,.2f}")
        print(f"  Total Return: {metrics['Total Return']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['Sharpe Ratio']:.2f}")
        print(f"  Max Drawdown: {metrics['Maximum Drawdown']:.2f}%")
    
    # Step 5: Compare Strategies
    print_header("STEP 5: STRATEGY COMPARISON")
    
    comparison_data = []
    for name, results in backtest_results.items():
        metrics = results['metrics']
        comparison_data.append({
            'Strategy': name,
            'Total Return (%)': metrics['Total Return'],
            'Sharpe Ratio': metrics['Sharpe Ratio'],
            'Max Drawdown (%)': metrics['Maximum Drawdown'],
            'Win Rate (%)': metrics['Win Rate'],
            'Number of Trades': metrics['Number of Trades'],
            'Final Value ($)': metrics['Final Portfolio Value']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('Total Return (%)', ascending=False)
    
    print("\nStrategy Comparison (Ranked by Total Return):")
    print(comparison_df.to_string(index=False))
    
    # Find best strategy
    best_strategy_name = comparison_df.iloc[0]['Strategy']
    print(f"\n🏆 Best Performing Strategy: {best_strategy_name}")
    
    # Step 6: Detailed Results for Best Strategy
    print_header(f"STEP 6: DETAILED RESULTS - {best_strategy_name.upper()} STRATEGY")
    
    best_results = backtest_results[best_strategy_name]
    best_results['backtester'].print_results()
    
    # Get trades log
    trades_log = best_results['backtester'].get_trades_log()
    if len(trades_log) > 0:
        print("\nTrade History (Last 10 Trades):")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(trades_log.tail(10).to_string(index=False))
        
        # Save trades log
        trades_log.to_csv('data/trades_log.csv', index=False)
        print(f"\n✓ Full trade history saved to data/trades_log.csv")
    
    # Step 7: Generate Visualizations
    print_header("STEP 7: GENERATING VISUALIZATIONS")
    
    print("Creating charts for best strategy...")
    
    # Get best strategy signals
    best_signals = signals_dict[best_strategy_name]
    best_portfolio = best_results['portfolio']
    
    # Create visualizer
    viz = Visualizer(data, best_portfolio)
    
    try:
        print("\n1. Creating price and indicators chart...")
        viz.plot_price_and_indicators(save_path='data/price_indicators.png')
    except Exception as e:
        print(f"  Warning: Could not create chart - {e}")
    
    try:
        print("2. Creating backtest results chart...")
        viz.plot_backtest_results(save_path='data/backtest_results.png')
    except Exception as e:
        print(f"  Warning: Could not create chart - {e}")
    
    try:
        print("3. Creating strategy comparison chart...")
        viz.plot_strategy_comparison(comparison_df, save_path='data/strategy_comparison.png')
    except Exception as e:
        print(f"  Warning: Could not create chart - {e}")
    
    try:
        print("4. Creating interactive chart...")
        viz.create_interactive_chart(signals=best_signals, save_path='data/interactive_chart.html')
        print("  ✓ Interactive chart saved to data/interactive_chart.html")
    except Exception as e:
        print(f"  Warning: Could not create interactive chart - {e}")
    
    # Step 8: Save Results
    print_header("STEP 8: SAVING RESULTS")
    
    # Save comparison to CSV
    comparison_df.to_csv('data/strategy_comparison.csv', index=False)
    print("✓ Strategy comparison saved to data/strategy_comparison.csv")
    
    # Save best strategy portfolio
    best_portfolio.to_csv('data/best_strategy_portfolio.csv')
    print("✓ Best strategy portfolio saved to data/best_strategy_portfolio.csv")
    
    # Save data with indicators
    data.to_csv('data/TSLA_with_indicators.csv')
    print("✓ Data with indicators saved to data/TSLA_with_indicators.csv")
    
    # Final Summary
    print_header("ANALYSIS COMPLETE")
    
    print("Summary:")
    print(f"  ✓ Analyzed {len(data)} days of Tesla stock data")
    print(f"  ✓ Tested {len(strategies_dict)} different trading strategies")
    print(f"  ✓ Best strategy: {best_strategy_name}")
    print(f"  ✓ Best return: {comparison_df.iloc[0]['Total Return (%)']:.2f}%")
    print(f"  ✓ All results saved to 'data/' directory")
    
    print("\nNext Steps:")
    print("  1. Review the generated charts in the 'data/' directory")
    print("  2. Open 'data/interactive_chart.html' in a browser for interactive analysis")
    print("  3. Check 'data/trades_log.csv' for detailed trade history")
    print("  4. Consider adjusting strategy parameters for optimization")
    
    print("\n" + "="*80)
    print("Thank you for using Tesla Quantitative Trading Analysis!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()
