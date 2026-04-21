import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# --- Page Configuration ---
st.set_page_config(
    page_title="IndoQuant Pro: Factor & Momentum Strategies",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Top-Tier UI/UX ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: 700; color: #1E3A8A; margin-bottom: 1rem;}
    .sub-header {font-size: 1.2rem; color: #4B5563; margin-bottom: 2rem;}
    .metric-card {background-color: #F3F4F6; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    .stButton>button {width: 100%; background-color: #2563EB; color: white; font-weight: 600; border-radius: 0.5rem; border: none; padding: 0.75rem;}
    .stButton>button:hover {background-color: #1D4ED8;}
    div[data-testid="stMetricValue"] {font-size: 1.5rem;}
    .commentary-box {background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;}
    .risk-high {color: #DC2626; font-weight: bold;}
    .risk-med {color: #D97706; font-weight: bold;}
    .risk-low {color: #059669; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

@st.cache_data
def get_data(tickers, start, end):
    """Download and process stock data with MultiIndex handling"""
    try:
        data = yf.download(tickers, start=start, end=end, progress=False)
        
        # Handle MultiIndex columns (new yfinance format)
        if isinstance(data.columns, pd.MultiIndex):
            # Extract Adj Close for all tickers
            if 'Adj Close' in data.columns.get_level_values(0):
                data = data['Adj Close']
            elif 'Close' in data.columns.get_level_values(0):
                data = data['Close']
            else:
                # Fallback: try to find any price column
                price_cols = [col for col in data.columns.get_level_values(0) 
                             if col in ['Adj Close', 'Close', 'Price']]
                if price_cols:
                    data = data[price_cols[0]]
                else:
                    data = data.iloc[:, 0]  # Take first column as fallback
        else:
            # Old format: single index
            if 'Adj Close' in data.columns:
                data = data['Adj Close']
            elif 'Close' in data.columns:
                data = data['Close']
            else:
                data = data.iloc[:, 0]
        
        # Drop NaN values and forward fill
        data = data.dropna(how='all')
        data = data.ffill()
        
        return data
    except Exception as e:
        st.error(f"Error downloading data: {str(e)}")
        return pd.DataFrame()

def calculate_factors(df):
    """Calculate Value, Momentum, Quality, Volatility factors"""
    factors = pd.DataFrame(index=df.index)
    
    # Momentum (12-1 month return)
    mom = df.pct_change(252) - df.pct_change(21)
    
    # Volatility (Annualized Std Dev of last 60 days)
    vol = df.rolling(60).std() * np.sqrt(252)
    
    # Simple Value Proxy (Inverse of Price momentum relative to 52w high - simplified for demo)
    # In production, use P/E, P/B from fundamental data
    roll_max = df.rolling(252).max()
    value = 1 - (df / roll_max) 
    
    # Quality (Stability of returns - inverse of vol change)
    quality = 1 / (vol + 1e-6)
    
    return {'momentum': mom, 'volatility': vol, 'value': value, 'quality': quality}

def factor_strategy(df, lookback=252, rebalance_freq=21, top_n=5):
    """Factor Investing Strategy"""
    factors = calculate_factors(df)
    
    # Composite Score: High Momentum, Low Vol, High Value, High Quality
    # Normalize scores
    score = (
        factors['momentum'].rank(pct=True) * 0.4 + 
        (1 - factors['volatility'].rank(pct=True)) * 0.3 + 
        factors['value'].rank(pct=True) * 0.2 + 
        factors['quality'].rank(pct=True) * 0.1
    )
    
    portfolio_returns = []
    current_weights = {}
    
    dates = df.index[lookback:]
    for i, date in enumerate(dates):
        if i % rebalance_freq == 0:
            # Rank stocks and pick top N
            rank_date = score.loc[date].dropna()
            top_stocks = rank_date.nlargest(top_n).index.tolist()
            weight = 1.0 / len(top_stocks) if top_stocks else 0
            current_weights = {stock: weight for stock in top_stocks}
        
        # Calculate daily return based on current weights
        daily_ret = 0
        for stock, w in current_weights.items():
            if stock in df.columns and date in df.index:
                daily_ret += w * df[stock].pct_change().loc[date]
        portfolio_returns.append(daily_ret)
    
    ret_series = pd.Series(portfolio_returns, index=dates)
    return (1 + ret_series).cumprod()

def roc_strategy(df, roc_period=12, stop_loss_pct=0.05, rebuy=True):
    """ROC Strategy with Stop Loss and Rebuy Logic"""
    roc = df.pct_change(roc_period) * 100
    
    portfolio_value = [1.0]
    cash = 0
    shares = {col: 0 for col in df.columns}
    invested = False
    entry_price = 0
    current_stock = None
    
    dates = df.index[roc_period:]
    
    # Simplified simulation: Rotate into strongest ROC stock, apply stop loss
    # Note: This is a simplified logic for demonstration
    
    equity_curve = []
    
    # We simulate a single asset rotation or aggregate approach for simplicity in this demo
    # Let's do an aggregate "Market Regime" filter based on average ROC of top 3
    
    for i, date in enumerate(dates):
        prev_date = dates[i-1] if i > 0 else dates[0]
        
        # Get current prices
        prices = df.loc[date]
        prev_prices = df.loc[prev_date] if prev_date in df.index else prices
        
        # Calculate signal: Average ROC of all available stocks
        avg_roc = roc.loc[date].mean()
        
        if avg_roc > 0: # Bullish Regime
            if not invested:
                # Buy
                invested = True
                entry_price = prices.mean() # Simplified basket buy
                shares_val = 1.0 # Assume 1 unit of portfolio
            else:
                # Check Stop Loss
                current_price = prices.mean()
                drawdown = (current_price - entry_price) / entry_price
                
                if drawdown <= -stop_loss_pct:
                    # Stop Loss Hit
                    if rebuy:
                        # "Immediately buy again" logic: 
                        # If trend (ROC) is still positive overall, we re-enter immediately
                        # This creates a "whipsaw" cost but keeps exposure in strong trends
                        entry_price = current_price # Reset entry price lower
                    else:
                        invested = False
                        cash = current_price # Realize loss
                else:
                    # Hold, update mark to market
                    pass
        else: # Bearish Regime
            if invested:
                # Sell
                invested = False
                # Realize value at current price
                pass
        
        # Calculate Portfolio Value
        if invested:
            val = prices.mean() # Simplified
            # Normalize to start at 1.0 roughly
            scale = 1.0 / df.mean().iloc[0] 
            equity_curve.append(val * scale)
        else:
            # Cash stays flat (simplified)
            equity_curve.append(equity_curve[-1] if equity_curve else 1.0)

    return pd.Series(equity_curve, index=dates)

def pure_roc_strategy(df, roc_period=12):
    """Pure ROC Trend Following"""
    roc = df.pct_change(roc_period)
    
    # Long when ROC > 0, Cash when ROC < 0
    # Aggregate signal
    signal = (roc.mean(axis=1) > 0).astype(int)
    
    # Shift signal to avoid lookahead bias (trade on close based on previous calc)
    signal = signal.shift(1).fillna(0)
    
    returns = df.mean(axis=1).pct_change()
    strat_returns = returns * signal
    
    return (1 + strat_returns).cumprod()

def calculate_metrics(equity_curve):
    """Calculate CFA-standard metrics"""
    returns = equity_curve.pct_change().dropna()
    
    total_ret = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
    ann_ret = (1 + total_ret) ** (252 / len(equity_curve)) - 1
    vol = returns.std() * np.sqrt(252)
    sharpe = (ann_ret - 0.05) / vol if vol != 0 else 0 # Assuming 5% risk free
    
    # Max Drawdown
    cum_max = equity_curve.cummax()
    drawdown = (equity_curve - cum_max) / cum_max
    max_dd = drawdown.min()
    
    return {
        "Total Return": f"{total_ret:.2%}",
        "Ann. Return": f"{ann_ret:.2%}",
        "Volatility": f"{vol:.2%}",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_dd:.2%}"
    }

# --- Sidebar Controls ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/9/9f/Emblem_of_Bank_Central_Asia.svg", width=50)
st.sidebar.title("Configuration")

strategy = st.sidebar.selectbox(
    "Select Strategy",
    ["Factor Investing (Multi-Factor)", "ROC + Stop-Loss & Rebuy", "Pure ROC Trend"]
)

tickers = st.sidebar.multiselect(
    "Select Stocks (IHSG)",
    ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "UNVR.JK", "ADRO.JK", "ICBP.JK", "ANTM.JK", "GOTO.JK"],
    default=["BBCA.JK", "BBRI.JK", "TLKM.JK"]
)

start_date = st.sidebar.date_input("Start Date", value=datetime.now() - timedelta(days=3*365))
end_date = st.sidebar.date_input("End Date", value=datetime.now())

run_btn = st.sidebar.button("Run Analysis", type="primary")

# --- Main Content ---
st.markdown('<div class="main-header">IndoQuant Pro: Strategic Backtester</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Institutional-grade factor and momentum analysis for the Indonesian Market</div>', unsafe_allow_html=True)

if run_btn:
    if not tickers:
        st.error("Please select at least one stock.")
    else:
        with st.spinner('Fetching data from Yahoo Finance...'):
            df = get_data(tickers, start_date, end_date)
            
        if df.empty:
            st.error("No data found. Try adjusting dates.")
        else:
            # Run Strategy
            with st.spinner('Running Optimization Engine...'):
                if "Factor" in strategy:
                    results = factor_strategy(df)
                    commentary_title = "Factor Investing Analysis"
                    commentary_text = """
                    **Strategy Logic:** This model combines Momentum, Low Volatility, Value, and Quality factors.
                    It rebalances periodically to hold the top-ranked stocks.
                    
                    **CFA Commentary:**
                    - **Pros:** Historically provides superior risk-adjusted returns (higher Sharpe) by diversifying across risk factors.
                    - **Cons:** Can underperform in extreme momentum crashes or when value traps persist.
                    - **Risk Profile:** Generally **Moderate**. The multi-factor approach smooths out individual stock volatility.
                    """
                elif "Stop-Loss" in strategy:
                    results = roc_strategy(df, stop_loss_pct=0.05, rebuy=True)
                    commentary_title = "Tactical ROC with Aggressive Re-entry"
                    commentary_text = """
                    **Strategy Logic:** Uses Rate of Change (ROC) to identify trends. Implements a strict 5% stop-loss.
                    Crucially, if stopped out but the macro trend remains positive, it **immediately re-buys**.
                    
                    **CFA Commentary:**
                    - **Pros:** Protects capital during sharp crashes while ensuring you don't miss the recovery in a volatile bull market.
                    - **Cons:** "Whipsaw" risk. In a sideways market, frequent stop-outs and re-buys will erode capital via transaction costs and slippage.
                    - **Risk Profile:** **High**. This is an aggressive tactical strategy. Expect higher turnover and potential drawdowns during choppy periods.
                    """
                else: # Pure ROC
                    results = pure_roc_strategy(df)
                    commentary_title = "Pure Momentum Trend Following"
                    commentary_text = """
                    **Strategy Logic:** Simple binary rule: Stay invested when ROC > 0, move to cash when ROC < 0.
                    
                    **CFA Commentary:**
                    - **Pros:** Excellent at capturing major bull runs and avoiding catastrophic bear markets.
                    - **Cons:** Lagging indicator. You will buy late and sell late. Performs poorly in ranging markets.
                    - **Risk Profile:** **Moderate-High**. Depends entirely on the strength of the trend.
                    """

            # Display Metrics
            metrics = calculate_metrics(results)
            
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Return", metrics["Total Return"])
            m2.metric("Ann. Return", metrics["Ann. Return"])
            m3.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
            m4.metric("Max Drawdown", metrics["Max Drawdown"], delta_color="inverse")
            m5.metric("Volatility", metrics["Volatility"])

            # Charts
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=results.index, y=results, mode='lines', name='Strategy', line=dict(color='#2563EB', width=3)))
                
                # Benchmark (Equal Weight)
                bench = df.mean(axis=1)
                bench_norm = bench / bench.iloc[0]
                fig.add_trace(go.Scatter(x=bench_norm.index, y=bench_norm, mode='lines', name='Buy & Hold (Avg)', line=dict(color='#9CA3AF', dash='dash')))
                
                fig.update_layout(title="Equity Curve Comparison", height=400, xaxis_title="Date", yaxis_title="Growth of $1", hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Strategy Insight")
                st.markdown(commentary_text)
                
                st.divider()
                st.write("### Current Signal")
                last_roc = df.pct_change(12).iloc[-1].mean() * 100
                if last_roc > 0:
                    st.success(f"**BULLISH** (Avg ROC: {last_roc:.2f}%)")
                else:
                    st.error(f"**BEARISH** (Avg ROC: {last_roc:.2f}%)")
                
                st.info("💡 **Suggestion:** If using the Stop-Loss strategy, ensure you have sufficient liquidity to handle frequent re-entries during volatile periods.")

            # Drawdown Chart
            dd = (results - results.cummax()) / results.cummax()
            fig_dd = px.area(y=dd, title="Drawdown History", labels={'index': 'Date', 'value': 'Drawdown %'})
            fig_dd.update_traces(line_color='#EF4444', fillcolor='rgba(239, 68, 68, 0.2)')
            st.plotly_chart(fig_dd, use_container_width=True)

else:
    st.info("👈 Select your parameters in the sidebar and click **Run Analysis** to begin.")
    
    # Placeholder visualization
    fig_placeholder = go.Figure()
    fig_placeholder.add_trace(go.Scatter(x=[], y=[], mode='lines'))
    fig_placeholder.update_layout(title="Waiting for Data...", height=400)
    st.plotly_chart(fig_placeholder, use_container_width=True)
