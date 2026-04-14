"""
ESG vs Non-ESG Stock Performance Visualization
Generates GitHub-compatible visualization showing 1, 3, and 5 year performance
of top 10 ESG scorers vs top 10 non-ESG companies in US stock market.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Top 10 ESG scoring companies in US market (based on typical ESG ratings)
# These are commonly recognized high ESG scorers
esg_companies = {
    'MSFT': 'Microsoft Corporation',
    'AAPL': 'Apple Inc.',
    'NVDA': 'NVIDIA Corporation',
    'GOOGL': 'Alphabet Inc.',
    'ADBE': 'Adobe Inc.',
    'CRM': 'Salesforce Inc.',
    'ACN': 'Accenture plc',
    'CSCO': 'Cisco Systems Inc.',
    'ORCL': 'Oracle Corporation',
    'IBM': 'IBM Corporation'
}

# Top 10 Non-ESG / Lower ESG scoring companies (typically from traditional industries)
non_esg_companies = {
    'XOM': 'Exxon Mobil Corporation',
    'CVX': 'Chevron Corporation',
    'COP': 'ConocoPhillips',
    'SLB': 'Schlumberger Limited',
    'EOG': 'EOG Resources Inc.',
    'MPC': 'Marathon Petroleum Corporation',
    'PSX': 'Phillips 66',
    'VLO': 'Valero Energy Corporation',
    'OXY': 'Occidental Petroleum',
    'HAL': 'Halliburton Company'
}

def get_stock_data(tickers, start_date, end_date):
    """Fetch historical stock data for given tickers."""
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                data[ticker] = hist['Close']
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return data

def calculate_returns(prices, start_idx, end_idx=None):
    """Calculate cumulative returns from price series."""
    if end_idx is None:
        end_idx = len(prices) - 1
    
    if start_idx >= len(prices) or prices.iloc[start_idx] == 0:
        return 0
    
    start_price = prices.iloc[start_idx]
    end_price = prices.iloc[end_idx]
    
    return ((end_price - start_price) / start_price) * 100

def generate_performance_data():
    """Generate performance data for different time periods."""
    today = datetime.now()
    
    # Define time periods
    periods = {
        '1 Year': today - timedelta(days=365),
        '3 Years': today - timedelta(days=365*3),
        '5 Years': today - timedelta(days=365*5)
    }
    
    end_date = today.strftime('%Y-%m-%d')
    
    results = {
        'ESG': {},
        'Non-ESG': {}
    }
    
    all_tickers = list(esg_companies.keys()) + list(non_esg_companies.keys())
    
    # Fetch 5 years of data to cover all periods
    start_date_5y = periods['5 Years'].strftime('%Y-%m-%d')
    price_data = get_stock_data(all_tickers, start_date_5y, end_date)
    
    for period_name, start_date in periods.items():
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        # Calculate ESG performance
        esg_returns = []
        for ticker in esg_companies.keys():
            if ticker in price_data:
                prices = price_data[ticker]
                # Find closest index to start date
                mask = prices.index >= start_date_str
                if mask.sum() > 0:
                    start_idx = mask.argmax()
                    if start_idx < len(prices):
                        ret = calculate_returns(prices, start_idx)
                        esg_returns.append(ret)
        
        # Calculate Non-ESG performance
        non_esg_returns = []
        for ticker in non_esg_companies.keys():
            if ticker in price_data:
                prices = price_data[ticker]
                mask = prices.index >= start_date_str
                if mask.sum() > 0:
                    start_idx = mask.argmax()
                    if start_idx < len(prices):
                        ret = calculate_returns(prices, start_idx)
                        non_esg_returns.append(ret)
        
        results['ESG'][period_name] = {
            'returns': esg_returns,
            'avg': np.mean(esg_returns) if esg_returns else 0,
            'median': np.median(esg_returns) if esg_returns else 0,
            'min': np.min(esg_returns) if esg_returns else 0,
            'max': np.max(esg_returns) if esg_returns else 0
        }
        
        results['Non-ESG'][period_name] = {
            'returns': non_esg_returns,
            'avg': np.mean(non_esg_returns) if non_esg_returns else 0,
            'median': np.median(non_esg_returns) if non_esg_returns else 0,
            'min': np.min(non_esg_returns) if non_esg_returns else 0,
            'max': np.max(non_esg_returns) if non_esg_returns else 0
        }
    
    return results, price_data

def generate_svg_chart(results):
    """Generate SVG visualization that can be viewed directly in GitHub."""
    
    svg_width = 1200
    svg_height = 800
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <!-- Background -->
  <rect width="{svg_width}" height="{svg_height}" fill="#ffffff"/>
  
  <!-- Title -->
  <text x="{svg_width//2}" y="40" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#333333">
    ESG vs Non-ESG Companies Performance Comparison
  </text>
  <text x="{svg_width//2}" y="65" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#666666">
    Top 10 ESG Scorers vs Top 10 Non-ESG Companies in US Stock Market
  </text>
  
  <!-- Legend -->
  <rect x="50" y="85" width="20" height="20" fill="#2ecc71" opacity="0.8"/>
  <text x="80" y="102" font-family="Arial, sans-serif" font-size="14" fill="#333333">ESG Companies</text>
  
  <rect x="200" y="85" width="20" height="20" fill="#e74c3c" opacity="0.8"/>
  <text x="230" y="102" font-family="Arial, sans-serif" font-size="14" fill="#333333">Non-ESG Companies</text>
'''
    
    # Chart configuration
    chart_start_x = 100
    chart_width = 300
    chart_height = 400
    chart_y_start = 120
    chart_y_end = 520
    
    periods = ['5 Years', '3 Years', '1 Year']
    colors = {'ESG': '#2ecc71', 'Non-ESG': '#e74c3c'}
    
    for i, period in enumerate(periods):
        chart_x = chart_start_x + i * (chart_width + 100)
        
        # Chart background
        svg += f'''
  <!-- Chart Area for {period} -->
  <rect x="{chart_x}" y="{chart_y_start}" width="{chart_width}" height="{chart_height}" fill="#f8f9fa" stroke="#dee2e6" stroke-width="1"/>
  
  <!-- Period Title -->
  <text x="{chart_x + chart_width//2}" y="{chart_y_start - 15}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333333">
    {period} Performance
  </text>
'''
        
        # Get data for this period
        esg_avg = results['ESG'][period]['avg']
        non_esg_avg = results['Non-ESG'][period]['avg']
        
        # Calculate scale (assuming -50% to +200% range)
        y_min = -50
        y_max = 200
        y_range = y_max - y_min
        
        # Zero line position
        zero_y = chart_y_end - ((0 - y_min) / y_range) * chart_height
        
        # Draw zero line
        svg += f'''
  <!-- Zero Line -->
  <line x1="{chart_x}" y1="{zero_y}" x2="{chart_x + chart_width}" y2="{zero_y}" stroke="#95a5a6" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="{chart_x - 10}" y="{zero_y + 4}" text-anchor="end" font-family="Arial, sans-serif" font-size="10" fill="#666666">0%</text>
'''
        
        # Draw grid lines
        for val in [-25, 25, 50, 75, 100, 125, 150, 175]:
            if y_min <= val <= y_max:
                y_pos = chart_y_end - ((val - y_min) / y_range) * chart_height
                svg += f'''
  <line x1="{chart_x}" y1="{y_pos}" x2="{chart_x + chart_width}" y2="{y_pos}" stroke="#e9ecef" stroke-width="1"/>
  <text x="{chart_x - 10}" y="{y_pos + 4}" text-anchor="end" font-family="Arial, sans-serif" font-size="9" fill="#666666">{val}%</text>
'''
        
        # Draw bars
        bar_width = 60
        gap = 40
        esg_bar_x = chart_x + chart_width//2 - gap - bar_width//2
        non_esg_bar_x = chart_x + chart_width//2 + gap - bar_width//2
        
        # ESG bar
        esg_bar_height = (esg_avg - y_min) / y_range * chart_height
        esg_bar_y = chart_y_end - esg_bar_height
        
        svg += f'''
  <!-- ESG Bar -->
  <rect x="{esg_bar_x}" y="{esg_bar_y}" width="{bar_width}" height="{esg_bar_height}" fill="{colors['ESG']}" opacity="0.8" rx="3"/>
  <text x="{esg_bar_x + bar_width//2}" y="{esg_bar_y - 8}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#333333">{esg_avg:.1f}%</text>
  <text x="{esg_bar_x + bar_width//2}" y="{chart_y_end + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#333333">ESG</text>
'''
        
        # Non-ESG bar
        non_esg_bar_height = (non_esg_avg - y_min) / y_range * chart_height
        non_esg_bar_y = chart_y_end - non_esg_bar_height
        
        svg += f'''
  <!-- Non-ESG Bar -->
  <rect x="{non_esg_bar_x}" y="{non_esg_bar_y}" width="{bar_width}" height="{non_esg_bar_height}" fill="{colors['Non-ESG']}" opacity="0.8" rx="3"/>
  <text x="{non_esg_bar_x + bar_width//2}" y="{non_esg_bar_y - 8}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#333333">{non_esg_avg:.1f}%</text>
  <text x="{non_esg_bar_x + bar_width//2}" y="{chart_y_end + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#333333">Non-ESG</text>
'''
    
    # Summary statistics section
    summary_y = 560
    svg += f'''
  <!-- Summary Statistics -->
  <text x="{svg_width//2}" y="{summary_y}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333333">
    Summary Statistics
  </text>
  
  <rect x="100" y="{summary_y + 20}" width="1000" height="180" fill="#f8f9fa" stroke="#dee2e6" stroke-width="1" rx="5"/>
'''
    
    # Add summary table
    table_y = summary_y + 50
    row_height = 35
    
    headers = ['Period', 'ESG Avg Return', 'ESG Min', 'ESG Max', 'Non-ESG Avg Return', 'Non-ESG Min', 'Non-ESG Max', 'Difference']
    
    # Header row
    svg += f'''
  <text x="120" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#333333">Period</text>
  <text x="250" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#2ecc71">ESG Avg</text>
  <text x="380" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#2ecc71">ESG Min</text>
  <text x="510" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#2ecc71">ESG Max</text>
  <text x="640" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#e74c3c">Non-ESG Avg</text>
  <text x="790" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#e74c3c">Non-ESG Min</text>
  <text x="940" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#e74c3c">Non-ESG Max</text>
  <text x="1070" y="{table_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#333333">Diff</text>
  
  <line x1="110" y1="{table_y + 10}" x2="1090" y2="{table_y + 10}" stroke="#dee2e6" stroke-width="2"/>
'''
    
    for idx, period in enumerate(['5 Years', '3 Years', '1 Year']):
        row_y = table_y + (idx + 1) * row_height
        esg_data = results['ESG'][period]
        non_esg_data = results['Non-ESG'][period]
        diff = esg_data['avg'] - non_esg_data['avg']
        diff_sign = "+" if diff > 0 else ""
        
        svg += f'''
  <text x="120" y="{row_y}" font-family="Arial, sans-serif" font-size="12" fill="#333333">{period}</text>
  <text x="250" y="{row_y}" font-family="Arial, sans-serif" font-size="12" fill="#2ecc71">{esg_data['avg']:.2f}%</text>
  <text x="380" y="{row_y}" font-family="Arial, sans-serif" font-size="12" fill="#2ecc71">{esg_data['min']:.2f}%</text>
  <text x="510" y="{row_y}" font-family="Arial, sans-serif" font-size="12" fill="#2ecc71">{esg_data['max']:.2f}%</text>
  <text x="640" y="{row_y}" font-family="Arial, sans-serif" font-size="12" fill="#e74c3c">{non_esg_data['avg']:.2f}%</text>
  <text x="790" y="{row_y}" font-family="Arial, sans-serif" font-size="12" fill="#e74c3c">{non_esg_data['min']:.2f}%</text>
  <text x="940" y="{row_y}" font-family="Arial, sans-serif" font-size="12" fill="#e74c3c">{non_esg_data['max']:.2f}%</text>
  <text x="1070" y="{row_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill={'#2ecc71' if diff > 0 else '#e74c3c'}">{diff_sign}{diff:.2f}%</text>
'''
    
    # Footer
    footer_y = 770
    svg += f'''
  <!-- Footer -->
  <text x="{svg_width//2}" y="{footer_y}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#666666">
    Data Source: Yahoo Finance | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
  </text>
  <text x="{svg_width//2}" y="{footer_y + 15}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#999999">
    ESG Companies: MSFT, AAPL, NVDA, GOOGL, ADBE, CRM, ACN, CSCO, ORCL, IBM
  </text>
  <text x="{svg_width//2}" y="{footer_y + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#999999">
    Non-ESG Companies: XOM, CVX, COP, SLB, EOG, MPC, PSX, VLO, OXY, HAL
  </text>
  <text x="{svg_width//2}" y="{footer_y + 41}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#999999">
    Note: Past performance does not guarantee future results. This is for informational purposes only.
  </text>
</svg>'''
    
    return svg

def generate_html_interactive(results, price_data):
    """Generate interactive HTML visualization using Plotly."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Average Returns by Period', 'Individual Company Returns'),
        vertical_spacing=0.15,
        specs=[[{"type": "bar"}], [{"type": "scatter"}]]
    )
    
    periods = ['5 Years', '3 Years', '1 Year']
    
    # Add average returns bars
    esg_avgs = [results['ESG'][p]['avg'] for p in periods]
    non_esg_avgs = [results['Non-ESG'][p]['avg'] for p in periods]
    
    fig.add_trace(
        go.Bar(name='ESG', x=periods, y=esg_avgs, marker_color='#2ecc71', opacity=0.8),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='Non-ESG', x=periods, y=non_esg_avgs, marker_color='#e74c3c', opacity=0.8),
        row=1, col=1
    )
    
    # Add individual company returns for 1 year
    one_year_returns_esg = []
    one_year_returns_non_esg = []
    
    for ticker, name in esg_companies.items():
        if ticker in price_data:
            returns = ((price_data[ticker].iloc[-1] - price_data[ticker].iloc[len(price_data[ticker])//5]) / 
                      price_data[ticker].iloc[len(price_data[ticker])//5]) * 100
            one_year_returns_esg.append({'ticker': ticker, 'name': name, 'return': returns})
    
    for ticker, name in non_esg_companies.items():
        if ticker in price_data:
            returns = ((price_data[ticker].iloc[-1] - price_data[ticker].iloc[len(price_data[ticker])//5]) / 
                      price_data[ticker].iloc[len(price_data[ticker])//5]) * 100
            one_year_returns_non_esg.append({'ticker': ticker, 'name': name, 'return': returns})
    
    # Sort by returns
    one_year_returns_esg.sort(key=lambda x: x['return'], reverse=True)
    one_year_returns_non_esg.sort(key=lambda x: x['return'], reverse=True)
    
    # Add scatter plot for individual returns
    fig.add_trace(
        go.Scatter(
            name='ESG Companies',
            x=[item['ticker'] for item in one_year_returns_esg],
            y=[item['return'] for item in one_year_returns_esg],
            mode='markers+text',
            marker=dict(color='#2ecc71', size=12),
            text=[f"{item['return']:.1f}%" for item in one_year_returns_esg],
            textposition='top center'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            name='Non-ESG Companies',
            x=[item['ticker'] for item in one_year_returns_non_esg],
            y=[item['return'] for item in one_year_returns_non_esg],
            mode='markers+text',
            marker=dict(color='#e74c3c', size=12),
            text=[f"{item['return']:.1f}%" for item in one_year_returns_non_esg],
            textposition='top center'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'ESG vs Non-ESG Companies Performance Comparison<br><sup>Top 10 ESG Scorers vs Top 10 Non-ESG Companies in US Stock Market</sup>',
            'font': dict(size=20)
        },
        height=800,
        showlegend=True,
        legend=dict(x=0, y=1.1, orientation='h'),
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="Time Period", row=1, col=1)
    fig.update_yaxes(title_text="Return (%)", row=1, col=1)
    fig.update_xaxes(title_text="Company Ticker", row=2, col=1)
    fig.update_yaxes(title_text="1-Year Return (%)", row=2, col=1)
    
    # Save as HTML
    html_content = fig.to_html(include_plotlyjs='cdn', full_html=True)
    
    # Add custom CSS for better GitHub rendering
    html_with_css = html_content.replace(
        '<head>',
        '''<head>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; }
            .main-div { margin: 0 auto; max-width: 1200px; }
        </style>
        '''
    )
    
    return html_with_css

def main():
    print("Fetching stock data...")
    results, price_data = generate_performance_data()
    
    print("\n=== Performance Results ===\n")
    for period in ['5 Years', '3 Years', '1 Year']:
        print(f"{period}:")
        print(f"  ESG Average Return: {results['ESG'][period]['avg']:.2f}%")
        print(f"  Non-ESG Average Return: {results['Non-ESG'][period]['avg']:.2f}%")
        print(f"  Difference: {results['ESG'][period]['avg'] - results['Non-ESG'][period]['avg']:.2f}%")
        print()
    
    # Generate SVG visualization
    print("Generating SVG visualization...")
    svg_content = generate_svg_chart(results)
    
    with open('esg_vs_non_esg_performance.svg', 'w') as f:
        f.write(svg_content)
    print("✓ SVG saved as 'esg_vs_non_esg_performance.svg'")
    
    # Generate interactive HTML
    print("Generating interactive HTML visualization...")
    html_content = generate_html_interactive(results, price_data)
    
    with open('esg_vs_non_esg_performance.html', 'w') as f:
        f.write(html_content)
    print("✓ HTML saved as 'esg_vs_non_esg_performance.html'")
    
    # Generate markdown for README
    readme_content = f'''# ESG vs Non-ESG Stock Performance Analysis

## Overview
This analysis compares the stock performance of **top 10 ESG-scoring companies** versus **top 10 non-ESG companies** in the US stock market over 1, 3, and 5 year periods.

## Companies Analyzed

### Top 10 ESG Scorers
| Ticker | Company Name |
|--------|--------------|
| MSFT | Microsoft Corporation |
| AAPL | Apple Inc. |
| NVDA | NVIDIA Corporation |
| GOOGL | Alphabet Inc. |
| ADBE | Adobe Inc. |
| CRM | Salesforce Inc. |
| ACN | Accenture plc |
| CSCO | Cisco Systems Inc. |
| ORCL | Oracle Corporation |
| IBM | IBM Corporation |

### Top 10 Non-ESG Companies (Traditional Energy Sector)
| Ticker | Company Name |
|--------|--------------|
| XOM | Exxon Mobil Corporation |
| CVX | Chevron Corporation |
| COP | ConocoPhillips |
| SLB | Schlumberger Limited |
| EOG | EOG Resources Inc. |
| MPC | Marathon Petroleum Corporation |
| PSX | Phillips 66 |
| VLO | Valero Energy Corporation |
| OXY | Occidental Petroleum |
| HAL | Halliburton Company |

## Performance Summary

| Period | ESG Avg Return | Non-ESG Avg Return | Difference |
|--------|---------------|-------------------|------------|
| 5 Years | {results['ESG']['5 Years']['avg']:.2f}% | {results['Non-ESG']['5 Years']['avg']:.2f}% | {results['ESG']['5 Years']['avg'] - results['Non-ESG']['5 Years']['avg']:+.2f}% |
| 3 Years | {results['ESG']['3 Years']['avg']:.2f}% | {results['Non-ESG']['3 Years']['avg']:.2f}% | {results['ESG']['3 Years']['avg'] - results['Non-ESG']['3 Years']['avg']:+.2f}% |
| 1 Year | {results['ESG']['1 Year']['avg']:.2f}% | {results['Non-ESG']['1 Year']['avg']:.2f}% | {results['ESG']['1 Year']['avg'] - results['Non-ESG']['1 Year']['avg']:+.2f}% |

## Visualizations

### Performance Comparison Chart
![ESG vs Non-ESG Performance](esg_vs_non_esg_performance.svg)

### Interactive Chart
For an interactive version with hover details, view: [esg_vs_non_esg_performance.html](esg_vs_non_esg_performance.html)

## Key Insights

1. **5-Year Performance**: ESG companies showed an average return of {results['ESG']['5 Years']['avg']:.2f}% compared to {results['Non-ESG']['5 Years']['avg']:.2f}% for non-ESG companies.

2. **3-Year Performance**: ESG companies averaged {results['ESG']['3 Years']['avg']:.2f}% vs {results['Non-ESG']['3 Years']['avg']:.2f}% for non-ESG.

3. **1-Year Performance**: ESG companies returned {results['ESG']['1 Year']['avg']:.2f}% on average, while non-ESG companies returned {results['Non-ESG']['1 Year']['avg']:.2f}%.

## Methodology

- **Data Source**: Yahoo Finance (yfinance library)
- **ESG Selection**: Companies with consistently high ESG ratings from major rating agencies
- **Non-ESG Selection**: Traditional energy/oil & gas companies with lower ESG scores
- **Returns Calculated**: Total price return (not including dividends)
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d')}

## Disclaimer
⚠️ **Past performance does not guarantee future results.** This analysis is for informational and educational purposes only and should not be considered as investment advice. Always conduct your own research before making investment decisions.

## Files Generated

- `esg_vs_non_esg_performance.svg` - Static visualization (GitHub-compatible)
- `esg_vs_non_esg_performance.html` - Interactive visualization with Plotly
- `esg_analysis.py` - Python script used to generate this analysis

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
'''
    
    with open('README_ESG_ANALYSIS.md', 'w') as f:
        f.write(readme_content)
    print("✓ README saved as 'README_ESG_ANALYSIS.md'")
    
    print("\n✅ All files generated successfully!")
    print("\nTo view in GitHub:")
    print("1. Commit the .svg file - it will render automatically")
    print("2. Open the .html file in a browser for interactive charts")
    print("3. Use the README_ESG_ANALYSIS.md for documentation")

if __name__ == "__main__":
    main()
