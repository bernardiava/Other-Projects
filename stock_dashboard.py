import pandas as pd
import yfinance as yf
import numpy as np
import streamlit as st

# Dictionary mapping tickers to company names
company_names = {
    'TSM': 'Taiwan Semiconductor Manufacturing Co. Ltd.',
    'SSNLF': 'Samsung Electronics Co Ltd',
    'TCEHY': 'Tencent Holdings Limited',
    'BABA': 'Alibaba Group Holding Ltd',
    'SONY': 'Sony Group Corp.',
    'KYCCF': 'Keyence Corp',
    'MPNGF': 'Meituan',
    'JD': 'JD.com Inc',
    'NTDOY': 'Nintendo Co Ltd',
    'TOELY': 'Tokyo Electron Ltd',
    'HXSCL': 'SK Hynix Inc.',
    'HNHPF': 'Hon Hai Precision Industry Co Ltd.',
    'MRAAY': 'Murata Manufacturing Co Ltd',
    'NTES': 'Netease Inc',
    'SSDIY': 'Samsung SDI Co. Ltd.',
    'BIDU': 'Baidu Inc.',
    'CAJ': 'Canon Inc.',
    'MDTKF': 'MediaTek Inc.',
    'FJTSY': 'Fujitsu Ltd',
    'NHNCF': 'NAVER Corp.',
    'FUJIY': 'FUJIFILM Holdings Corp.',
    'XIACY': 'Xiaomi Corporation',
    'KYOCY': 'Kyocera Corp',
    'DLEGF': 'Delta Electronics Inc.',
    'KAKOF': 'Kakao Corp',
    'KUASF': 'Kuaishou Technology',
    'RNECY': 'Renesas Electronics Corp.',
    'LGCLF': 'LG Energy Solution. Ltd.',
    'NTDTY': 'NTT Data Corp',
    'YAHOY': 'Z Holdings Corporation'
}

# List of stock tickers
tickers = list(company_names.keys())

# Define the start and end dates
start_date = '2024-01-01'
end_date = '2024-12-31'

# Suppress all FutureWarnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Create an empty list to store results
results = []

# Loop through each ticker
for ticker in tickers:
    # Fetch the historical data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Check if data is available
    if data.empty:
        continue
    
    # Calculate the stock return for the entire period in percentage
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]
    stock_return = ((end_price - start_price) / start_price) * 100

    # Calculate daily returns
    data['Return'] = data['Close'].pct_change()

    # Calculate Sharpe Ratio (Assuming risk-free rate = 0 for simplicity)
    risk_free_rate = 0  # Annual risk-free rate in decimal form (e.g., 2% = 0.02)
    sharpe_ratio = (data['Return'].mean() * 252 - risk_free_rate) / (data['Return'].std() * np.sqrt(252))

    # Calculate Max Drawdown
    peak = data['Close'].cummax()
    drawdown = (data['Close'] / peak) - 1
    max_drawdown = drawdown.min() * 100

    # Calculate Annualized Standard Deviation of Returns
    annualized_std_dev = data['Return'].std() * np.sqrt(252) * 100

    # Append results to the list
    results.append({
        'Ticker': ticker,
        'Company Name': company_names[ticker],
        'Stock Return (%)': stock_return,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown (%)': abs(max_drawdown),
        'Annualized Std Dev (%)': annualized_std_dev
    })

# Convert the results list to a DataFrame
results_df = pd.DataFrame(results)

# Streamlit dashboard
st.title("2024 APAC Tech Stock Performance Dashboard")

# Display the results
st.subheader("Stock Performance Summary")
st.dataframe(results_df)

# Recommendation based on highest stock return
best_performer = results_df.loc[results_df['Stock Return (%)'].idxmax()]

st.subheader("Recommendation")
st.write(f"The recommended stock to buy based on the highest performance in the year is **{best_performer['Company Name']}** "
         f"({best_performer['Ticker']}) with a stock return of **{best_performer['Stock Return (%)']:.2f}%**.")

st.subheader("Notes")
st.write("1. The Sharpe Ratio indicates the risk-adjusted return. A higher Sharpe Ratio is preferable.")
st.write("2. Max Drawdown reflects the largest observed loss from a peak to a trough. Lower values are better.")
st.write("3. Annualized Standard Deviation provides insight into the volatility of returns.")
st.write("4. Past performance is not indicative of future results. Always conduct thorough research.")
