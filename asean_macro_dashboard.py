import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from pandas_datareader import wb
import yfinance as yf
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="ASEAN Macro Dashboard", layout="wide")
st.title("📊 ASEAN Macro Dashboard: Fiscal Deficit & Current Account")
st.markdown("**Real Data from World Bank & Market Sources** | Built for ASEAN Economist Role")

# ==========================================
# 1. DATA FETCHING FUNCTIONS (Real Data)
# ==========================================
@st.cache_data(ttl=86400)  # Cache for 1 day
def load_worldbank_data(indicator, country_codes, start_year=2010, end_year=2024):
    """Fetch real data from World Bank API"""
    try:
        df = wb.download(indicator=indicator, country=country_codes, start=start_year, end=end_year)
        df = df.reset_index()
        # Clean and pivot
        df = df.pivot(index='year', columns='country', values=indicator)
        return df
    except Exception as e:
        st.warning(f"Could not fetch {indicator}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_market_data(ticker, period="5y"):
    """Fetch bond yields / exchange rates as real-time economic indicators"""
    try:
        data = yf.download(ticker, period=period, progress=False)
        return data['Close']
    except:
        return pd.Series()

# ==========================================
# 2. ASEAN COUNTRY CONFIGURATION
# ==========================================
asean_countries = {
    "Indonesia": {"wb_code": "IDN", "bond_ticker": "ID10Y.GOV", "fx_ticker": "USDIDR=X", "currency": "IDR"},
    "Thailand": {"wb_code": "THA", "bond_ticker": "TH10Y.GOV", "fx_ticker": "USDTHB=X", "currency": "THB"},
    "Singapore": {"wb_code": "SGP", "bond_ticker": "SG10Y.GOV", "fx_ticker": "USDSGD=X", "currency": "SGD"},
    "Malaysia": {"wb_code": "MYS", "bond_ticker": "MY10Y.GOV", "fx_ticker": "USDMYR=X", "currency": "MYR"},
    "Philippines": {"wb_code": "PHL", "bond_ticker": "PH10Y.GOV", "fx_ticker": "USDPHP=X", "currency": "PHP"},
    "Vietnam": {"wb_code": "VNM", "bond_ticker": "VN10Y.GOV", "fx_ticker": "USDVND=X", "currency": "VND"}
}

# World Bank Indicators
CURRENT_ACCOUNT_IND = "BN.CAB.XOKA.GD.ZS"  # Current Account Balance (% of GDP)
FISCAL_DEFICIT_IND = "GC.BAL.CASH.GD.ZS"    # Cash surplus/deficit (% of GDP) - Negative = Deficit

# ==========================================
# 3. SIDEBAR: COUNTRY SELECTION
# ==========================================
st.sidebar.header("🌏 Select Country")
selected_country = st.sidebar.selectbox("Choose ASEAN Economy", list(asean_countries.keys()))
country_data = asean_countries[selected_country]

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Sources:**")
st.sidebar.markdown("- World Bank API (Fiscal Deficit, Current Account)")
st.sidebar.markdown("- Yahoo Finance (Bond Yields, Exchange Rates)")
st.sidebar.markdown("- SARIMA Model for Forecast (Next 4 Quarters)")

# ==========================================
# 4. MAIN DATA LOADING
# ==========================================
with st.spinner(f"Loading real macroeconomic data for {selected_country}..."):
    # Load Fiscal & External Data
    fiscal_df = load_worldbank_data(FISCAL_DEFICIT_IND, [country_data["wb_code"]])
    ca_df = load_worldbank_data(CURRENT_ACCOUNT_IND, [country_data["wb_code"]])
    
    # Load Market Sentiment Data
    bond_series = get_market_data(country_data["bond_ticker"])
    fx_series = get_market_data(country_data["fx_ticker"])

# ==========================================
# 5. VISUALIZATION & FORECASTING
# ==========================================
if not fiscal_df.empty and not ca_df.empty:
    
    # --- Prepare Data for Modeling ---
    # Align fiscal and current account data
    combined = pd.DataFrame(index=fiscal_df.index)
    combined['Fiscal Balance (% of GDP)'] = fiscal_df[country_data["wb_code"]]
    combined['Current Account (% of GDP)'] = ca_df[country_data["wb_code"]]
    combined = combined.dropna()
    
    if len(combined) > 4:  # Enough data to forecast
        # --- Forecast Logic (SARIMA) ---
        # We forecast using the Current Account, as it is the target for the job description
        
        st.subheader(f"🔮 {selected_country}: Current Account Forecast (Next 4 Quarters)")
        
        # Fit SARIMA model
        model = SARIMAX(combined['Current Account (% of GDP)'], 
                        order=(1,1,1), 
                        seasonal_order=(1,1,1,4),
                        simple_differencing=False)
        model_fit = model.fit(disp=False)
        
        # Make forecast
        forecast_steps = 4
        forecast = model_fit.forecast(steps=forecast_steps)
        forecast_index = pd.date_range(start=combined.index[-1], periods=forecast_steps+1, freq='Q')[1:]
        
        # Create plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Historical
        fig.add_trace(go.Scatter(x=combined.index, y=combined['Current Account (% of GDP)'],
                                 mode='lines+markers', name='Historical Current Account',
                                 line=dict(color='blue', width=2)), secondary_y=False)
        
        # Forecast
        fig.add_trace(go.Scatter(x=forecast_index, y=forecast,
                                 mode='lines+markers', name='Forecast',
                                 line=dict(color='red', width=2, dash='dot')), secondary_y=False)
        
        # Add Market Sentiment (Bond Yield) on secondary axis
        if bond_series is not None and not bond_series.empty:
            fig.add_trace(go.Scatter(x=bond_series.index, y=bond_series.values,
                                     mode='lines', name=f'{selected_country} 10Y Bond Yield',
                                     line=dict(color='gray', width=1, dash='dash')),
                                     secondary_y=True)
            fig.update_yaxes(title_text="Current Account (% of GDP)", secondary_y=False)
            fig.update_yaxes(title_text="Bond Yield (%, market sentiment)", secondary_y=True)
        
        fig.update_layout(title=f"{selected_country} External Balance & Market Sentiment",
                          xaxis_title="Year", hovermode="x unified", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display Forecast Table
        forecast_df = pd.DataFrame({'Quarter': forecast_index.strftime('%Y-Q%q'), 
                                    'Forecasted Current Account (% of GDP)': forecast.values.round(2)})
        st.table(forecast_df)
        
        # --- Fiscal Deficit Analysis ---
        st.subheader(f"💰 {selected_country}: Fiscal Deficit Analysis")
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=combined.index, y=combined['Fiscal Balance (% of GDP)'],
                              name='Fiscal Balance (% of GDP)',
                              marker_color=['red' if x < 0 else 'green' for x in combined['Fiscal Balance (% of GDP)']]))
        fig2.add_hline(y=0, line_dash="dash", line_color="black")
        fig2.update_layout(title=f"{selected_country} Government Fiscal Balance (Negative = Deficit)",
                           xaxis_title="Year", yaxis_title="% of GDP", height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        # --- Executive Summary (AI Commentary) ---
        st.subheader("📝 Executive Summary & Policy Insight")
        latest_fiscal = combined['Fiscal Balance (% of GDP)'].iloc[-1]
        latest_ca = combined['Current Account (% of GDP)'].iloc[-1]
        forecast_ca = forecast.iloc[-1]
        
        status_fiscal = "Surplus" if latest_fiscal > 0 else "Deficit"
        status_ca = "Surplus" if latest_ca > 0 else "Deficit"
        
        st.markdown(f"""
        - **Fiscal Position ({combined.index[-1].year})**: The government is running a **{status_fiscal}** of **{abs(latest_fiscal):.2f}% of GDP**.
        - **External Position ({combined.index[-1].year})**: Current Account is in **{status_ca}** at **{latest_ca:.2f}% of GDP**.
        - **4-Quarter Outlook**: Current Account is forecasted to move to **{forecast_ca:.2f}%** over the next year.
        - **Market View**: Bond yields reflect market expectations for fiscal health and monetary policy.
        """)
        
        if latest_fiscal < -3:
            st.warning(f"⚠️ {selected_country} is running a significant fiscal deficit (>3% of GDP). Monitor debt sustainability and structural reform progress.")
        else:
            st.success(f"✅ {selected_country}'s fiscal deficit is within manageable territory.")

    else:
        st.warning(f"Not enough historical data for {selected_country} to generate a robust forecast. Try a different country.")
else:
    st.error(f"Could not retrieve World Bank data for {selected_country}. The API may be temporarily unavailable or the country code is missing data for these indicators.")
    st.markdown("Try selecting a different country or refresh the page.")

# ==========================================
# 6. FOOTER & DATA REFRESH
# ==========================================
st.markdown("---")
st.caption(f"Data refreshed: World Bank (Annual) | Market Data (Daily). Dashboard built with Python, Streamlit, and real APIs.")
if st.button("🔄 Refresh Data (Clear Cache)"):
    st.cache_data.clear()
    st.rerun()
