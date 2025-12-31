"""
Daily Signal Generator
Quick script to get today's long/short signal for Tesla
Run this daily to get trading signals
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.valuation_strategy import ValuationStrategy
import warnings
warnings.filterwarnings('ignore')


def main():
    """Generate and display daily trading signal"""
    
    print("\n" + "🚀"*40)
    print("TESLA DAILY SIGNAL GENERATOR")
    print("🚀"*40 + "\n")
    
    # Initialize strategy
    print("Initializing valuation strategy...")
    strategy = ValuationStrategy(symbol='TSLA', lookback_period=252)
    
    # Fetch latest data
    print("Fetching latest market data...")
    strategy.fetch_comprehensive_data(period='2y')
    
    # Generate signal
    print("Analyzing valuation metrics...\n")
    strategy.generate_daily_signals()
    
    # Print comprehensive report
    strategy.print_signal_report()
    
    # Quick summary
    signals = strategy.signals
    
    print("📊 QUICK TRADING SUMMARY:")
    print("─" * 80)
    
    if "LONG" in signals['signal']:
        print("📈 POSITION: LONG (BUY)")
        print(f"💰 Target Entry: ${signals['current_price']:.2f}")
        print(f"🎯 Fair Value: ${signals['fair_value_estimate']:.2f}")
        print(f"📉 Support: ${signals['bb_lower']:.2f}")
        print(f"📈 Resistance: ${signals['bb_upper']:.2f}")
    elif "SHORT" in signals['signal']:
        print("📉 POSITION: SHORT (SELL)")
        print(f"💰 Target Entry: ${signals['current_price']:.2f}")
        print(f"🎯 Fair Value: ${signals['fair_value_estimate']:.2f}")
        print(f"📈 Resistance: ${signals['bb_upper']:.2f}")
        print(f"📉 Support: ${signals['bb_lower']:.2f}")
    else:
        print("⏸️ POSITION: NEUTRAL (HOLD)")
        print(f"💰 Current Price: ${signals['current_price']:.2f}")
        print(f"🎯 Fair Value: ${signals['fair_value_estimate']:.2f}")
        print("⏳ Wait for better entry point")
    
    print("─" * 80)
    
    # Historical context
    print("\n📅 RECENT SIGNAL HISTORY (Last 10 Days):")
    historical = strategy.create_signal_dataframe(days=10)
    if len(historical) > 0:
        print(historical.to_string(index=False))
    
    print("\n" + "="*80)
    print("⚠️  DISCLAIMER: This is for educational purposes only.")
    print("    Always do your own research before making investment decisions.")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSignal generation interrupted by user.")
    except Exception as e:
        print(f"\n\nError occurred: {e}")
        import traceback
        traceback.print_exc()
