#!/usr/bin/env python3
"""
Generate GitHub-compatible visualization comparing ESG vs Non-ESG companies in Hong Kong Stock Market.
Creates static PNG images that can be directly displayed in GitHub README files.
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Top 10 ESG scored companies in HK
ESG_COMPANIES = {
    '0005.HK': 'HSBC Holdings',
    '0941.HK': 'China Mobile',
    '0388.HK': 'HKEX',
    '0001.HK': 'CK Hutchison',
    '0002.HK': 'CLP Holdings',
    '0003.HK': 'HK & China Gas',
    '0016.HK': 'Sun Hung Kai Properties',
    '0006.HK': 'Power Assets',
    '2318.HK': 'Ping An Insurance',
    '0939.HK': 'CCB'
}

# Top 10 Non-ESG / Lower ESG scored companies
NON_ESG_COMPANIES = {
    '0857.HK': 'PetroChina',
    '0386.HK': 'Sinopec',
    '0883.HK': 'CNOOC',
    '1088.HK': 'Shenhua Energy',
    '0291.HK': 'China Resources Beer',
    '0288.HK': 'WH Group',
    '1919.HK': 'COSCO Shipping',
    '2628.HK': 'China Life Insurance',
    '1398.HK': 'ICBC',
    '3988.HK': 'Bank of China'
}

def fetch_stock_data(tickers, period='5y'):
    """Fetch historical stock data for given tickers."""
    data = {}
    print(f"Fetching {period} data for {len(tickers)} companies...")
    
    for ticker, name in tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if not hist.empty and 'Close' in hist.columns:
                # Remove timezone info to avoid comparison issues
                hist.index = hist.index.tz_localize(None)
                data[ticker] = hist['Close']
                print(f"  ✓ {name} ({ticker})")
            else:
                print(f"  ✗ {name} ({ticker}) - No data")
        except Exception as e:
            print(f"  ✗ {name} ({ticker}) - Error: {str(e)}")
    
    return data

def calculate_performance(esg_data, non_esg_data, periods_days):
    """Calculate performance metrics for different time periods."""
    results = {}
    now = pd.Timestamp.now().tz_localize(None)
    
    for period_name, days in periods_days.items():
        cutoff_date = now - pd.Timedelta(days=days)
        
        esg_returns = []
        non_esg_returns = []
        
        for ticker, prices in esg_data.items():
            filtered = prices[prices.index >= cutoff_date]
            if len(filtered) >= 2:
                start_price = filtered.iloc[0]
                end_price = filtered.iloc[-1]
                if start_price > 0:
                    ret = ((end_price - start_price) / start_price) * 100
                    esg_returns.append(ret)
        
        for ticker, prices in non_esg_data.items():
            filtered = prices[prices.index >= cutoff_date]
            if len(filtered) >= 2:
                start_price = filtered.iloc[0]
                end_price = filtered.iloc[-1]
                if start_price > 0:
                    ret = ((end_price - start_price) / start_price) * 100
                    non_esg_returns.append(ret)
        
        if esg_returns and non_esg_returns:
            results[period_name] = {
                'esg_avg': sum(esg_returns) / len(esg_returns),
                'esg_std': pd.Series(esg_returns).std(),
                'non_esg_avg': sum(non_esg_returns) / len(non_esg_returns),
                'non_esg_std': pd.Series(non_esg_returns).std()
            }
    
    return results

def create_comparison_chart(esg_data, non_esg_data, output_file='esg_vs_non_esg_performance.png'):
    """Create a comprehensive comparison chart."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('ESG vs Non-ESG Companies Performance\nHong Kong Stock Market Comparison', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    esg_normalized = {}
    non_esg_normalized = {}
    
    for ticker, prices in esg_data.items():
        if len(prices) > 0 and prices.iloc[0] > 0:
            esg_normalized[ticker] = (prices / prices.iloc[0]) * 100
    
    for ticker, prices in non_esg_data.items():
        if len(prices) > 0 and prices.iloc[0] > 0:
            non_esg_normalized[ticker] = (prices / prices.iloc[0]) * 100
    
    # Plot 1: ESG Companies
    ax1 = axes[0, 0]
    colors_esg = plt.cm.Set1(range(len(esg_normalized)))
    for i, (ticker, prices) in enumerate(esg_normalized.items()):
        ax1.plot(prices.index, prices.values, label=ESG_COMPANIES.get(ticker, ticker), 
                color=colors_esg[i % len(colors_esg)], linewidth=1.5, alpha=0.8)
    ax1.set_title('Top 10 ESG Companies (Normalized to Base 100)', fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price (Base 100)')
    ax1.legend(loc='upper left', fontsize=7, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 2: Non-ESG Companies
    ax2 = axes[0, 1]
    colors_non_esg = plt.cm.Set2(range(len(non_esg_normalized)))
    for i, (ticker, prices) in enumerate(non_esg_normalized.items()):
        ax2.plot(prices.index, prices.values, label=NON_ESG_COMPANIES.get(ticker, ticker),
                color=colors_non_esg[i % len(colors_non_esg)], linewidth=1.5, alpha=0.8)
    ax2.set_title('Top 10 Non-ESG Companies (Normalized to Base 100)', fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Price (Base 100)')
    ax2.legend(loc='upper left', fontsize=7, ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 3: Average Performance
    ax3 = axes[1, 0]
    if esg_normalized:
        esg_df = pd.DataFrame(esg_normalized)
        esg_avg = esg_df.mean(axis=1)
        esg_std = esg_df.std(axis=1)
        ax3.plot(esg_avg.index, esg_avg.values, 'g-', linewidth=3, label='ESG Average', marker='o', markersize=3)
        ax3.fill_between(esg_avg.index, esg_avg - esg_std, esg_avg + esg_std, alpha=0.3, color='green')
    
    if non_esg_normalized:
        non_esg_df = pd.DataFrame(non_esg_normalized)
        non_esg_avg = non_esg_df.mean(axis=1)
        non_esg_std = non_esg_df.std(axis=1)
        ax3.plot(non_esg_avg.index, non_esg_avg.values, 'r-', linewidth=3, label='Non-ESG Average', marker='s', markersize=3)
        ax3.fill_between(non_esg_avg.index, non_esg_avg - non_esg_std, non_esg_avg + non_esg_std, alpha=0.3, color='red')
    
    ax3.set_title('Average Performance: ESG vs Non-ESG', fontweight='bold')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Average Price (Base 100)')
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 4: Returns Bar Chart
    ax4 = axes[1, 1]
    periods = {'1 Year': 365, '3 Years': 1095, '5 Years': 1825}
    x_positions = range(len(periods))
    width = 0.35
    now = pd.Timestamp.now().tz_localize(None)
    
    esg_returns = []
    non_esg_returns = []
    
    for period_name, days in periods.items():
        cutoff = now - pd.Timedelta(days=days)
        
        esg_rets = []
        for ticker, prices in esg_data.items():
            filtered = prices[prices.index >= cutoff]
            if len(filtered) >= 2:
                ret = ((filtered.iloc[-1] - filtered.iloc[0]) / filtered.iloc[0]) * 100
                esg_rets.append(ret)
        esg_returns.append(sum(esg_rets)/len(esg_rets) if esg_rets else 0)
        
        non_esg_rets = []
        for ticker, prices in non_esg_data.items():
            filtered = prices[prices.index >= cutoff]
            if len(filtered) >= 2:
                ret = ((filtered.iloc[-1] - filtered.iloc[0]) / filtered.iloc[0]) * 100
                non_esg_rets.append(ret)
        non_esg_returns.append(sum(non_esg_rets)/len(non_esg_rets) if non_esg_rets else 0)
    
    bars1 = ax4.bar([p - width/2 for p in x_positions], esg_returns, width, 
                   label='ESG', color='green', alpha=0.7, edgecolor='darkgreen')
    bars2 = ax4.bar([p + width/2 for p in x_positions], non_esg_returns, width,
                   label='Non-ESG', color='red', alpha=0.7, edgecolor='darkred')
    
    ax4.set_title('Returns by Time Period (%)', fontweight='bold')
    ax4.set_xlabel('Time Period')
    ax4.set_ylabel('Return (%)')
    ax4.set_xticks(x_positions)
    ax4.set_xticklabels(periods.keys())
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    for bar in bars1:
        height = bar.get_height()
        ax4.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax4.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\n✓ Chart saved: {output_file}")

def main():
    print("="*70)
    print("ESG vs Non-ESG Performance Analysis - Hong Kong Stock Market")
    print("="*70)
    
    print("\nFetching ESG companies data (5 years)...")
    esg_data = fetch_stock_data(ESG_COMPANIES, '5y')
    
    print("\nFetching Non-ESG companies data (5 years)...")
    non_esg_data = fetch_stock_data(NON_ESG_COMPANIES, '5y')
    
    if not esg_data or not non_esg_data:
        print("Error: Could not fetch sufficient data")
        return
    
    print(f"\nSuccessfully fetched data for:")
    print(f"  - {len(esg_data)} ESG companies")
    print(f"  - {len(non_esg_data)} Non-ESG companies")
    
    print("\nGenerating visualization...")
    create_comparison_chart(esg_data, non_esg_data)
    
    periods = {'1 Year': 365, '3 Years': 1095, '5 Years': 1825}
    results = calculate_performance(esg_data, non_esg_data, periods)
    
    print("\n" + "="*70)
    print("PERFORMANCE SUMMARY")
    print("="*70)
    print(f"{'Period':<12} {'ESG Avg %':<12} {'Non-ESG Avg %':<15} {'Difference':<12}")
    print("-"*70)
    for period, data in results.items():
        diff = data['esg_avg'] - data['non_esg_avg']
        print(f"{period:<12} {data['esg_avg']:>10.2f}%   {data['non_esg_avg']:>13.2f}%   {diff:>+10.2f}%")
    print("="*70)
    
    print("\nFiles generated:")
    print("  - esg_vs_non_esg_performance.png (GitHub-compatible visualization)")
    print("\nTo embed in GitHub README:")
    print("  ![ESG vs Non-ESG Performance](esg_vs_non_esg_performance.png)")

if __name__ == "__main__":
    main()
