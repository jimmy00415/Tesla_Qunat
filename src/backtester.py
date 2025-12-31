"""
Backtesting Module
Comprehensive backtesting framework for trading strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime


class Backtester:
    """Backtest trading strategies and calculate performance metrics"""
    
    def __init__(self, data, signals, initial_capital=100000, commission=0.001):
        """
        Initialize backtester
        
        Args:
            data: DataFrame with stock data
            signals: DataFrame with trading signals and positions
            initial_capital: Starting capital
            commission: Commission rate per trade (0.001 = 0.1%)
        """
        self.data = data.copy()
        self.signals = signals.copy()
        self.initial_capital = initial_capital
        self.commission = commission
        self.portfolio = None
        self.metrics = {}
    
    def run_backtest(self):
        """Run the backtest simulation"""
        
        # Initialize portfolio
        self.portfolio = pd.DataFrame(index=self.signals.index)
        self.portfolio['Close'] = self.data['Close']
        self.portfolio['Position'] = self.signals['Position']
        
        # Calculate position changes (trades)
        self.portfolio['Trade'] = self.portfolio['Position'].diff()
        
        # Calculate shares held
        self.portfolio['Shares'] = 0.0
        capital = self.initial_capital
        shares = 0
        cash = capital
        
        portfolio_values = []
        cash_values = []
        shares_held = []
        
        for i in range(len(self.portfolio)):
            price = self.portfolio['Close'].iloc[i]
            position = self.portfolio['Position'].iloc[i]
            trade = self.portfolio['Trade'].iloc[i]
            
            # Execute trade
            if trade > 0:  # Buy
                # Calculate shares to buy with available cash
                commission_cost = cash * self.commission
                available_cash = cash - commission_cost
                shares_to_buy = available_cash / price
                shares += shares_to_buy
                cash = 0
            elif trade < 0:  # Sell
                # Sell all shares
                cash = shares * price * (1 - self.commission)
                shares = 0
            
            # Calculate portfolio value
            portfolio_value = cash + (shares * price)
            
            portfolio_values.append(portfolio_value)
            cash_values.append(cash)
            shares_held.append(shares)
        
        self.portfolio['Cash'] = cash_values
        self.portfolio['Shares'] = shares_held
        self.portfolio['Portfolio_Value'] = portfolio_values
        
        # Calculate returns
        self.portfolio['Returns'] = self.portfolio['Portfolio_Value'].pct_change()
        self.portfolio['Cumulative_Returns'] = (
            (1 + self.portfolio['Returns']).cumprod() - 1
        )
        
        # Buy and hold benchmark
        self.portfolio['BuyHold_Value'] = (
            self.initial_capital * 
            (self.portfolio['Close'] / self.portfolio['Close'].iloc[0])
        )
        self.portfolio['BuyHold_Returns'] = self.portfolio['BuyHold_Value'].pct_change()
        self.portfolio['BuyHold_Cumulative'] = (
            (1 + self.portfolio['BuyHold_Returns']).cumprod() - 1
        )
        
        return self.portfolio
    
    def calculate_metrics(self):
        """Calculate comprehensive performance metrics"""
        
        if self.portfolio is None:
            self.run_backtest()
        
        # Basic metrics
        final_value = self.portfolio['Portfolio_Value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Buy and hold comparison
        buyhold_final = self.portfolio['BuyHold_Value'].iloc[-1]
        buyhold_return = (buyhold_final - self.initial_capital) / self.initial_capital
        
        # Number of trades
        trades = self.portfolio['Trade'].abs().sum()
        
        # Winning trades
        trade_returns = []
        entry_price = None
        entry_index = None
        
        for i in range(len(self.portfolio)):
            trade = self.portfolio['Trade'].iloc[i]
            price = self.portfolio['Close'].iloc[i]
            
            if trade > 0:  # Entry
                entry_price = price
                entry_index = i
            elif trade < 0 and entry_price is not None:  # Exit
                exit_price = price
                trade_return = (exit_price - entry_price) / entry_price
                trade_returns.append(trade_return)
                entry_price = None
        
        # Win rate
        if len(trade_returns) > 0:
            winning_trades = sum(1 for r in trade_returns if r > 0)
            win_rate = winning_trades / len(trade_returns)
            avg_win = np.mean([r for r in trade_returns if r > 0]) if winning_trades > 0 else 0
            losing_trades = len(trade_returns) - winning_trades
            avg_loss = np.mean([r for r in trade_returns if r < 0]) if losing_trades > 0 else 0
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
        
        # Sharpe Ratio (annualized)
        returns = self.portfolio['Returns'].dropna()
        if len(returns) > 0 and returns.std() != 0:
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        else:
            sharpe_ratio = 0
        
        # Maximum Drawdown
        cumulative = self.portfolio['Portfolio_Value']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Sortino Ratio (annualized)
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0:
            downside_std = negative_returns.std()
            sortino_ratio = np.sqrt(252) * returns.mean() / downside_std
        else:
            sortino_ratio = 0
        
        # Calmar Ratio
        calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Total commission paid
        total_commission = (trades / 2) * self.initial_capital * self.commission
        
        # Store metrics
        self.metrics = {
            'Initial Capital': self.initial_capital,
            'Final Portfolio Value': final_value,
            'Total Return': total_return * 100,
            'Total Return ($)': final_value - self.initial_capital,
            'Buy & Hold Return': buyhold_return * 100,
            'Buy & Hold Value': buyhold_final,
            'Excess Return vs Buy&Hold': (total_return - buyhold_return) * 100,
            'Number of Trades': int(trades / 2),
            'Win Rate': win_rate * 100,
            'Average Win': avg_win * 100,
            'Average Loss': avg_loss * 100,
            'Profit Factor': profit_factor,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio,
            'Calmar Ratio': calmar_ratio,
            'Maximum Drawdown': max_drawdown * 100,
            'Total Commission Paid': total_commission,
            'Start Date': self.portfolio.index[0],
            'End Date': self.portfolio.index[-1],
            'Trading Days': len(self.portfolio),
        }
        
        return self.metrics
    
    def print_results(self):
        """Print backtest results"""
        
        if not self.metrics:
            self.calculate_metrics()
        
        print("\n" + "="*70)
        print("BACKTEST RESULTS")
        print("="*70)
        
        print(f"\nPeriod: {self.metrics['Start Date']} to {self.metrics['End Date']}")
        print(f"Trading Days: {self.metrics['Trading Days']}")
        
        print("\n--- RETURNS ---")
        print(f"Initial Capital:        ${self.metrics['Initial Capital']:,.2f}")
        print(f"Final Portfolio Value:  ${self.metrics['Final Portfolio Value']:,.2f}")
        print(f"Total Return:           {self.metrics['Total Return']:.2f}%")
        print(f"Total Return ($):       ${self.metrics['Total Return ($)']:,.2f}")
        print(f"Buy & Hold Return:      {self.metrics['Buy & Hold Return']:.2f}%")
        print(f"Buy & Hold Value:       ${self.metrics['Buy & Hold Value']:,.2f}")
        print(f"Excess Return:          {self.metrics['Excess Return vs Buy&Hold']:.2f}%")
        
        print("\n--- RISK METRICS ---")
        print(f"Sharpe Ratio:           {self.metrics['Sharpe Ratio']:.2f}")
        print(f"Sortino Ratio:          {self.metrics['Sortino Ratio']:.2f}")
        print(f"Calmar Ratio:           {self.metrics['Calmar Ratio']:.2f}")
        print(f"Maximum Drawdown:       {self.metrics['Maximum Drawdown']:.2f}%")
        
        print("\n--- TRADING ACTIVITY ---")
        print(f"Number of Trades:       {self.metrics['Number of Trades']}")
        print(f"Win Rate:               {self.metrics['Win Rate']:.2f}%")
        print(f"Average Win:            {self.metrics['Average Win']:.2f}%")
        print(f"Average Loss:           {self.metrics['Average Loss']:.2f}%")
        print(f"Profit Factor:          {self.metrics['Profit Factor']:.2f}")
        print(f"Total Commission:       ${self.metrics['Total Commission Paid']:,.2f}")
        
        print("="*70 + "\n")
    
    def get_trades_log(self):
        """Get detailed log of all trades"""
        
        if self.portfolio is None:
            self.run_backtest()
        
        trades = []
        entry_price = None
        entry_date = None
        
        for i in range(len(self.portfolio)):
            trade = self.portfolio['Trade'].iloc[i]
            price = self.portfolio['Close'].iloc[i]
            date = self.portfolio.index[i]
            
            if trade > 0:  # Entry
                entry_price = price
                entry_date = date
            elif trade < 0 and entry_price is not None:  # Exit
                exit_price = price
                exit_date = date
                profit = ((exit_price - entry_price) / entry_price) * 100
                holding_days = (exit_date - entry_date).days
                
                trades.append({
                    'Entry Date': entry_date,
                    'Entry Price': entry_price,
                    'Exit Date': exit_date,
                    'Exit Price': exit_price,
                    'Return (%)': profit,
                    'Holding Days': holding_days,
                    'Outcome': 'Win' if profit > 0 else 'Loss'
                })
                
                entry_price = None
        
        return pd.DataFrame(trades)
    
    def compare_strategies(self, strategies_dict):
        """
        Compare multiple strategies
        
        Args:
            strategies_dict: Dict of {strategy_name: signals_dataframe}
            
        Returns:
            DataFrame with comparison metrics
        """
        results = []
        
        for name, signals in strategies_dict.items():
            backtester = Backtester(
                self.data, 
                signals, 
                self.initial_capital, 
                self.commission
            )
            metrics = backtester.calculate_metrics()
            
            results.append({
                'Strategy': name,
                'Total Return (%)': metrics['Total Return'],
                'Sharpe Ratio': metrics['Sharpe Ratio'],
                'Max Drawdown (%)': metrics['Maximum Drawdown'],
                'Win Rate (%)': metrics['Win Rate'],
                'Number of Trades': metrics['Number of Trades'],
                'Final Value ($)': metrics['Final Portfolio Value']
            })
        
        comparison = pd.DataFrame(results)
        comparison = comparison.sort_values('Total Return (%)', ascending=False)
        
        return comparison


if __name__ == "__main__":
    # Test backtester
    from data_fetcher import DataFetcher
    from indicators import TechnicalIndicators
    from strategies import TrendFollowingStrategy, MeanReversionStrategy, MomentumStrategy
    
    print("Testing Backtester...\n")
    
    # Fetch and prepare data
    fetcher = DataFetcher()
    data = fetcher.fetch_data(period='2y')
    
    indicators = TechnicalIndicators(data)
    data = indicators.add_all_indicators()
    data = indicators.add_custom_signals()
    
    # Test trend following strategy
    strategy = TrendFollowingStrategy(data)
    signals = strategy.generate_signals()
    
    # Run backtest
    backtester = Backtester(data, signals, initial_capital=100000)
    backtester.run_backtest()
    backtester.print_results()
    
    # Get trades log
    trades_log = backtester.get_trades_log()
    if len(trades_log) > 0:
        print("Sample Trades:")
        print(trades_log.head())
