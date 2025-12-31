"""
Visualization Module
Create charts and visualizations for trading analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set style
sns.set_style('darkgrid')
plt.style.use('seaborn-v0_8-darkgrid')


class Visualizer:
    """Create visualizations for trading analysis"""
    
    def __init__(self, data, portfolio=None):
        """
        Initialize visualizer
        
        Args:
            data: DataFrame with stock data and indicators
            portfolio: DataFrame with portfolio backtest results (optional)
        """
        self.data = data
        self.portfolio = portfolio
    
    def plot_price_and_indicators(self, figsize=(16, 12), save_path=None):
        """
        Plot price with technical indicators
        
        Args:
            figsize: Figure size
            save_path: Path to save figure (optional)
        """
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.3)
        
        # Plot 1: Price and Moving Averages
        ax1 = fig.add_subplot(gs[0])
        ax1.plot(self.data.index, self.data['Close'], label='Close Price', linewidth=2, color='black')
        ax1.plot(self.data.index, self.data['SMA_50'], label='SMA 50', alpha=0.7, color='blue')
        ax1.plot(self.data.index, self.data['SMA_200'], label='SMA 200', alpha=0.7, color='red')
        
        # Bollinger Bands
        ax1.fill_between(self.data.index, self.data['BB_Upper'], self.data['BB_Lower'], 
                         alpha=0.2, color='gray', label='Bollinger Bands')
        
        ax1.set_title('Tesla Stock Price with Technical Indicators', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: RSI
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax2.plot(self.data.index, self.data['RSI'], label='RSI', color='purple', linewidth=1.5)
        ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought')
        ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold')
        ax2.fill_between(self.data.index, 30, 70, alpha=0.1, color='gray')
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: MACD
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        ax3.plot(self.data.index, self.data['MACD'], label='MACD', color='blue', linewidth=1.5)
        ax3.plot(self.data.index, self.data['MACD_Signal'], label='Signal', color='red', linewidth=1.5)
        ax3.bar(self.data.index, self.data['MACD_Histogram'], label='Histogram', 
                color='gray', alpha=0.3)
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax3.set_ylabel('MACD', fontsize=12)
        ax3.legend(loc='best')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Volume
        ax4 = fig.add_subplot(gs[3], sharex=ax1)
        colors = ['g' if self.data['Close'].iloc[i] >= self.data['Close'].iloc[i-1] 
                  else 'r' for i in range(1, len(self.data))]
        colors = ['gray'] + colors
        ax4.bar(self.data.index, self.data['Volume'], color=colors, alpha=0.5)
        ax4.set_ylabel('Volume', fontsize=12)
        ax4.set_xlabel('Date', fontsize=12)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        
        plt.show()
    
    def plot_backtest_results(self, figsize=(16, 10), save_path=None):
        """
        Plot backtest results
        
        Args:
            figsize: Figure size
            save_path: Path to save figure (optional)
        """
        if self.portfolio is None:
            print("No portfolio data available")
            return
        
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(3, 2, height_ratios=[2, 1, 1], hspace=0.3, wspace=0.3)
        
        # Plot 1: Portfolio Value vs Buy & Hold
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.portfolio.index, self.portfolio['Portfolio_Value'], 
                label='Strategy', linewidth=2, color='blue')
        ax1.plot(self.portfolio.index, self.portfolio['BuyHold_Value'], 
                label='Buy & Hold', linewidth=2, color='gray', alpha=0.7)
        ax1.fill_between(self.portfolio.index, self.portfolio['Portfolio_Value'], 
                        self.portfolio['BuyHold_Value'], 
                        where=self.portfolio['Portfolio_Value'] >= self.portfolio['BuyHold_Value'],
                        alpha=0.2, color='green', label='Outperformance')
        ax1.fill_between(self.portfolio.index, self.portfolio['Portfolio_Value'], 
                        self.portfolio['BuyHold_Value'], 
                        where=self.portfolio['Portfolio_Value'] < self.portfolio['BuyHold_Value'],
                        alpha=0.2, color='red', label='Underperformance')
        ax1.set_title('Portfolio Value: Strategy vs Buy & Hold', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Cumulative Returns
        ax2 = fig.add_subplot(gs[1, :])
        ax2.plot(self.portfolio.index, self.portfolio['Cumulative_Returns'] * 100, 
                label='Strategy Returns', linewidth=2, color='blue')
        ax2.plot(self.portfolio.index, self.portfolio['BuyHold_Cumulative'] * 100, 
                label='Buy & Hold Returns', linewidth=2, color='gray', alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('Cumulative Returns Comparison', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cumulative Returns (%)', fontsize=12)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Drawdown
        ax3 = fig.add_subplot(gs[2, 0])
        cumulative = self.portfolio['Portfolio_Value']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        ax3.fill_between(self.portfolio.index, drawdown, 0, alpha=0.3, color='red')
        ax3.plot(self.portfolio.index, drawdown, linewidth=1, color='darkred')
        ax3.set_title('Drawdown', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Drawdown (%)', fontsize=12)
        ax3.set_xlabel('Date', fontsize=12)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Position
        ax4 = fig.add_subplot(gs[2, 1])
        ax4.fill_between(self.portfolio.index, self.portfolio['Position'], 0, 
                        where=self.portfolio['Position'] > 0, alpha=0.5, color='green', 
                        label='Long Position')
        ax4.fill_between(self.portfolio.index, self.portfolio['Position'], 0, 
                        where=self.portfolio['Position'] == 0, alpha=0.5, color='gray', 
                        label='Flat')
        ax4.set_title('Position Over Time', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Position', fontsize=12)
        ax4.set_xlabel('Date', fontsize=12)
        ax4.set_ylim(-0.1, 1.1)
        ax4.legend(loc='best')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        
        plt.show()
    
    def plot_strategy_comparison(self, strategies_comparison, figsize=(12, 6), save_path=None):
        """
        Plot comparison of multiple strategies
        
        Args:
            strategies_comparison: DataFrame with strategy comparison
            figsize: Figure size
            save_path: Path to save figure (optional)
        """
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Plot 1: Total Return
        strategies_comparison.plot(x='Strategy', y='Total Return (%)', kind='bar', 
                                   ax=axes[0, 0], color='steelblue', legend=False)
        axes[0, 0].set_title('Total Return by Strategy', fontweight='bold')
        axes[0, 0].set_ylabel('Return (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Sharpe Ratio
        strategies_comparison.plot(x='Strategy', y='Sharpe Ratio', kind='bar', 
                                   ax=axes[0, 1], color='green', legend=False)
        axes[0, 1].set_title('Sharpe Ratio by Strategy', fontweight='bold')
        axes[0, 1].set_ylabel('Sharpe Ratio')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Good (>1)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Max Drawdown
        strategies_comparison.plot(x='Strategy', y='Max Drawdown (%)', kind='bar', 
                                   ax=axes[1, 0], color='red', legend=False)
        axes[1, 0].set_title('Maximum Drawdown by Strategy', fontweight='bold')
        axes[1, 0].set_ylabel('Max Drawdown (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Win Rate
        strategies_comparison.plot(x='Strategy', y='Win Rate (%)', kind='bar', 
                                   ax=axes[1, 1], color='purple', legend=False)
        axes[1, 1].set_title('Win Rate by Strategy', fontweight='bold')
        axes[1, 1].set_ylabel('Win Rate (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].axhline(y=50, color='black', linestyle='--', alpha=0.5, label='50%')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        
        plt.show()
    
    def create_interactive_chart(self, signals=None, save_path=None):
        """
        Create interactive Plotly chart
        
        Args:
            signals: DataFrame with trading signals (optional)
            save_path: Path to save HTML file (optional)
        """
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=('Price & Indicators', 'RSI', 'MACD', 'Volume')
        )
        
        # Price and Moving Averages
        fig.add_trace(go.Candlestick(
            x=self.data.index,
            open=self.data['Open'],
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            name='TSLA'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['SMA_50'],
            name='SMA 50', line=dict(color='blue', width=1)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['SMA_200'],
            name='SMA 200', line=dict(color='red', width=1)
        ), row=1, col=1)
        
        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['BB_Upper'],
            name='BB Upper', line=dict(color='gray', width=1, dash='dash')
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['BB_Lower'],
            name='BB Lower', line=dict(color='gray', width=1, dash='dash'),
            fill='tonexty', fillcolor='rgba(128, 128, 128, 0.2)'
        ), row=1, col=1)
        
        # Trading signals if provided
        if signals is not None:
            buy_signals = signals[signals['Signal'] == 1]
            sell_signals = signals[signals['Signal'] == -1]
            
            fig.add_trace(go.Scatter(
                x=buy_signals.index, y=self.data.loc[buy_signals.index, 'Close'],
                mode='markers', name='Buy Signal',
                marker=dict(symbol='triangle-up', size=12, color='green')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=sell_signals.index, y=self.data.loc[sell_signals.index, 'Close'],
                mode='markers', name='Sell Signal',
                marker=dict(symbol='triangle-down', size=12, color='red')
            ), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['RSI'],
            name='RSI', line=dict(color='purple', width=2)
        ), row=2, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['MACD'],
            name='MACD', line=dict(color='blue', width=2)
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['MACD_Signal'],
            name='Signal', line=dict(color='red', width=2)
        ), row=3, col=1)
        
        fig.add_trace(go.Bar(
            x=self.data.index, y=self.data['MACD_Histogram'],
            name='Histogram', marker_color='gray', opacity=0.3
        ), row=3, col=1)
        
        # Volume
        colors = ['green' if self.data['Close'].iloc[i] >= self.data['Close'].iloc[i-1] 
                  else 'red' for i in range(1, len(self.data))]
        colors = ['gray'] + colors
        
        fig.add_trace(go.Bar(
            x=self.data.index, y=self.data['Volume'],
            name='Volume', marker_color=colors, opacity=0.5
        ), row=4, col=1)
        
        # Update layout
        fig.update_layout(
            title='Tesla (TSLA) Technical Analysis - Interactive Chart',
            xaxis_rangeslider_visible=False,
            height=1000,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="Volume", row=4, col=1)
        
        if save_path:
            fig.write_html(save_path)
            print(f"Interactive chart saved to {save_path}")
        
        fig.show()


if __name__ == "__main__":
    # Test visualizer
    from data_fetcher import DataFetcher
    from indicators import TechnicalIndicators
    from strategies import TrendFollowingStrategy
    from backtester import Backtester
    
    print("Testing Visualizer...\n")
    
    # Fetch and prepare data
    fetcher = DataFetcher()
    data = fetcher.fetch_data(period='1y')
    
    indicators = TechnicalIndicators(data)
    data = indicators.add_all_indicators()
    data = indicators.add_custom_signals()
    
    # Generate strategy signals
    strategy = TrendFollowingStrategy(data)
    signals = strategy.generate_signals()
    
    # Run backtest
    backtester = Backtester(data, signals)
    portfolio = backtester.run_backtest()
    
    # Create visualizations
    viz = Visualizer(data, portfolio)
    
    print("Creating visualizations...")
    viz.plot_price_and_indicators()
    viz.plot_backtest_results()
