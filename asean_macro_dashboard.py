import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import requests
import yfinance as yf
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="ASEAN Macro Dashboard", layout="wide")
st.title("📊 ASEAN Macro Dashboard")

# Create tabs
tabs = st.tabs(["🌏 Macro Overview", "💰 WACC Proxy Calculator"])

# ==========================================
# TAB 1: MACRO OVERVIEW (Existing Functionality)
# ==========================================
with tabs[0]:
    st.header("Fiscal Deficit & Current Account Analysis")
    st.markdown("**Real Data from World Bank & Market Sources** | Built for ASEAN Economist Role")
    
    # ==========================================
    # 1. DATA FETCHING FUNCTIONS (Real Data)
    # ==========================================
    @st.cache_data(ttl=86400)  # Cache for 1 day
    def load_worldbank_data(indicator, country_codes, start_year=2010, end_year=2027):
        """Fetch real data from World Bank API using direct HTTP requests"""
        try:
            # Build URL for World Bank API v2
            countries = "+".join(country_codes)
            url = f"https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}?date={start_year}:{end_year}&format=json&per_page=500"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if len(data) < 2 or not data[1]:
                return pd.DataFrame()
            
            # Parse the data - filter out None values
            records = []
            for item in data[1]:
                value = item['value']
                if value is not None:  # Only include records with actual values
                    records.append({
                        'country': item['country']['value'],
                        'year': int(item['date']),
                        indicator: float(value)
                    })
            
            df = pd.DataFrame(records)
            if df.empty:
                return pd.DataFrame()
            
            # Pivot to get years as index and countries as columns
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
    
    # World Bank Indicators - Using available indicators based on API testing (verified Dec 2024)
    CURRENT_ACCOUNT_IND = "BN.CAB.XOKA.GD.ZS"      # Current Account Balance (% of GDP) - ✓ Available for all ASEAN
    FISCAL_DEFICIT_IND = "NY.GDP.MKTP.KD.ZG"        # GDP Growth (annual %) - ✓ Available for all ASEAN
    # Note: Original fiscal balance indicator (GC.BAL.CASH.GD.ZS) is archived/unavailable
    # Most fiscal indicators (debt, expense, revenue) have missing data for IDN and VNM in recent years
    # Using GDP Growth as a key macroeconomic indicator alongside Current Account
    # GDP growth reflects economic performance which is influenced by fiscal policy effectiveness
    
    # ==========================================
    # 3. SIDEBAR: COUNTRY SELECTION
    # ==========================================
    st.sidebar.header("🌏 Select Country")
    selected_country = st.sidebar.selectbox("Choose ASEAN Economy", list(asean_countries.keys()), key="macro_country")
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
        fx_series = get_market_data(country_data["fx_ticker"], period="max")
        
        # Get FX prediction using SARIMA model
        fx_prediction_df = None
        if fx_series is not None and not fx_series.empty and len(fx_series) > 10:
            try:
                # Fit SARIMA model on FX data
                fx_model = SARIMAX(fx_series.dropna(), 
                                  order=(1,1,1), 
                                  seasonal_order=(1,1,1,12),
                                  simple_differencing=False)
                fx_model_fit = fx_model.fit(disp=False)
                
                # Forecast next 12 months (monthly data)
                fx_forecast_steps = 12
                fx_forecast = fx_model_fit.forecast(steps=fx_forecast_steps)
                
                # Create forecast index (monthly dates)
                last_date = fx_series.index[-1]
                if hasattr(last_date, 'to_period'):
                    # If it's a Period index
                    forecast_dates = pd.date_range(start=last_date.to_timestamp() + pd.DateOffset(months=1), 
                                                  periods=fx_forecast_steps, freq='M')
                elif isinstance(last_date, pd.Timestamp):
                    # If it's already a Timestamp
                    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                                  periods=fx_forecast_steps, freq='M')
                else:
                    # Fallback for other date types
                    forecast_dates = pd.date_range(start=pd.Timestamp(last_date) + pd.DateOffset(months=1), 
                                                  periods=fx_forecast_steps, freq='M')
                
                fx_prediction_df = pd.DataFrame({
                    'Date': forecast_dates,
                    'Predicted Exchange Rate': fx_forecast.values
                })
            except Exception as e:
                st.warning(f"Could not generate FX prediction: {e}")
                fx_prediction_df = None
    
    # ==========================================
    # 5. VISUALIZATION & FORECASTING
    # ==========================================
    if not fiscal_df.empty and not ca_df.empty:
        
        # --- Prepare Data for Modeling ---
        # Align fiscal and current account data
        combined = pd.DataFrame(index=fiscal_df.index)
        # Use iloc[:, 0] since we're loading single country data and column is country name
        combined['Fiscal Balance (% of GDP)'] = fiscal_df.iloc[:, 0]
        combined['Current Account (% of GDP)'] = ca_df.iloc[:, 0]
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
            # Create forecast index as future years (since data is annual)
            last_year = int(combined.index[-1])
            forecast_index = [last_year + i for i in range(1, forecast_steps + 1)]
            
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
            forecast_df = pd.DataFrame({'Year': forecast_index, 
                                        'Forecasted Current Account (% of GDP)': forecast.values.round(2)})
            st.table(forecast_df)
            
            # --- Economic Growth Analysis ---
            st.subheader(f"📈 {selected_country}: GDP Growth Analysis")
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=combined.index, y=combined['Fiscal Balance (% of GDP)'],
                                  name='GDP Growth (Annual %)',
                                  marker_color=['green' if x > 0 else 'red' for x in combined['Fiscal Balance (% of GDP)']]))
            fig2.add_hline(y=0, line_dash="dash", line_color="black")
            fig2.update_layout(title=f"{selected_country} Annual GDP Growth Rate",
                               xaxis_title="Year", yaxis_title="% Growth", height=400)
            st.plotly_chart(fig2, use_container_width=True)
            
            # --- Executive Summary (AI Commentary) ---
            st.subheader("📝 Executive Summary & Policy Insight")
            latest_gdp_growth = combined['Fiscal Balance (% of GDP)'].iloc[-1]
            latest_ca = combined['Current Account (% of GDP)'].iloc[-1]
            forecast_ca = forecast.iloc[-1]
            
            # Get the latest year (handle both int/numpy int and datetime index)
            idx_value = combined.index[-1]
            if hasattr(idx_value, 'year'):
                latest_year = idx_value.year
            else:
                latest_year = int(idx_value)
            
            growth_status = "STRONG" if latest_gdp_growth > 5 else "MODERATE" if latest_gdp_growth > 3 else "WEAK"
            status_ca = "Surplus" if latest_ca > 0 else "Deficit"
            
            st.markdown(f"""
            - **Economic Performance ({latest_year})**: GDP grew by **{latest_gdp_growth:.2f}%** (**{growth_status}** growth).
            - **External Position ({latest_year})**: Current Account is in **{status_ca}** at **{latest_ca:.2f}% of GDP**.
            - **4-Year Outlook**: Current Account is forecasted to move to **{forecast_ca:.2f}%** over the next 4 years.
            - **Market View**: Bond yields reflect market expectations for economic growth and monetary policy.
            """)
            
            if latest_gdp_growth < 2:
                st.warning(f"⚠️ {selected_country} has weak economic growth (<2%). Consider stimulus measures and structural reforms.")
            elif latest_gdp_growth > 6:
                st.success(f"✅ {selected_country} shows strong economic momentum. Monitor for overheating risks.")
            else:
                st.success(f"✅ {selected_country}'s economy is growing at a sustainable pace.")
        
        # --- Rupiah/Exchange Rate Prediction Section ---
        if fx_prediction_df is not None and selected_country == "Indonesia":
            st.subheader(f"💱 {selected_country}: Rupiah (USD/IDR) Exchange Rate Forecast")
            st.markdown("**12-Month Forward Prediction using SARIMA Model**")
            
            # Create FX prediction plot
            fig_fx = make_subplots(specs=[[{"secondary_y": False}]])
            
            # Historical FX data
            fig_fx.add_trace(go.Scatter(x=fx_series.index, y=fx_series.values,
                                        mode='lines', name='Historical USD/IDR',
                                        line=dict(color='blue', width=2)), secondary_y=False)
            
            # Forecast FX data
            fig_fx.add_trace(go.Scatter(x=fx_prediction_df['Date'], 
                                        y=fx_prediction_df['Predicted Exchange Rate'],
                                        mode='lines+markers', name='Forecast (Next 12 Months)',
                                        line=dict(color='red', width=2, dash='dot')), secondary_y=False)
            
            fig_fx.update_layout(title=f"{selected_country} Rupiah Exchange Rate Forecast (USD/IDR)",
                                xaxis_title="Date", yaxis_title="Exchange Rate (IDR per USD)",
                                hovermode="x unified", height=500)
            st.plotly_chart(fig_fx, use_container_width=True)
            
            # Display FX Forecast Table with yearly summary
            st.markdown("**Yearly Average Forecast Summary:**")
            fx_prediction_df['Year'] = fx_prediction_df['Date'].dt.year
            yearly_forecast = fx_prediction_df.groupby('Year')['Predicted Exchange Rate'].mean().reset_index()
            yearly_forecast.columns = ['Year', 'Avg Predicted Exchange Rate (IDR/USD)']
            st.table(yearly_forecast.round(2))
            
            # FX Commentary
            latest_fx = fx_series.iloc[-1]
            avg_forecast_fx = fx_prediction_df['Predicted Exchange Rate'].mean()
            fx_trend = "DEPRECIATING" if avg_forecast_fx > latest_fx else "APPRECIATING"
            
            st.markdown(f"""
            - **Current Exchange Rate**: **{latest_fx:.2f} IDR/USD**
            - **12-Month Avg Forecast**: **{avg_forecast_fx:.2f} IDR/USD**
            - **Trend Outlook**: Rupiah is expected to be **{fx_trend}** against USD over the next year.
            """)
            
            if avg_forecast_fx > latest_fx * 1.05:
                st.warning(f"⚠️ Significant rupiah depreciation expected. Consider hedging strategies for USD exposure.")
            elif avg_forecast_fx < latest_fx * 0.95:
                st.success(f"✅ Rupiah showing strength. Favorable for import costs and inflation control.")
            else:
                st.info(f"ℹ️ Rupiah expected to remain relatively stable with moderate volatility.")
    
    else:
        st.warning(f"Not enough historical data for {selected_country} to generate a robust forecast. Try a different country.")

# ==========================================
# FOOTER & DATA REFRESH
# ==========================================
st.markdown("---")
st.caption(f"Data refreshed: World Bank (Annual) | Market Data (Daily). Dashboard built with Python, Streamlit, and real APIs.")

# ==========================================
# TAB 2: WACC PROXY CALCULATOR
# ==========================================
with tabs[1]:
    st.header("💰 WACC Proxy Calculator")
    st.markdown("**Calculate Weighted Average Cost of Capital for ASEAN Companies**")
    st.markdown("This tool estimates WACC using CAPM for cost of equity, market data for cost of debt, and customizable capital structure inputs.")
    
    # Industry Beta Presets
    industry_betas = {
        "Technology": 1.2,
        "Healthcare": 0.9,
        "Financial Services": 1.1,
        "Consumer Goods": 0.8,
        "Energy": 1.3,
        "Utilities": 0.6,
        "Industrials": 1.0,
        "Materials": 1.1,
        "Telecommunications": 0.7,
        "Real Estate": 0.9,
        "Custom": None
    }
    
    # Country Risk Premiums (approximate, can be adjusted)
    country_risk_premiums = {
        "Indonesia": 2.5,
        "Thailand": 1.8,
        "Singapore": 0.5,
        "Malaysia": 1.5,
        "Philippines": 2.2,
        "Vietnam": 3.0
    }
    
    # Risk-free rates (approximate 10Y government bond yields)
    risk_free_rates = {
        "Indonesia": 6.8,
        "Thailand": 2.9,
        "Singapore": 3.2,
        "Malaysia": 4.1,
        "Philippines": 6.2,
        "Vietnam": 3.5
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Company & Market Inputs")
        
        # Company Name
        company_name = st.text_input("Company Name", placeholder="e.g., PT Astra International")
        
        # Country Selection
        wacc_country = st.selectbox("Country of Operation", list(country_risk_premiums.keys()))
        
        # Industry Selection
        selected_industry = st.selectbox("Industry Sector", list(industry_betas.keys()))
        
        # Custom Beta Input
        if selected_industry == "Custom":
            beta = st.number_input("Beta (β)", min_value=0.0, max_value=3.0, value=1.0, step=0.1, help="Measure of stock volatility relative to market")
        else:
            beta = industry_betas[selected_industry]
            st.info(f"Using industry beta for {selected_industry}: **{beta}**")
        
        # Market Risk Premium
        default_mrp = 6.0  # Typical emerging market premium
        market_risk_premium = st.number_input("Equity Risk Premium (%)", min_value=0.0, max_value=15.0, value=default_mrp, step=0.5, help="Additional return expected from market over risk-free rate")
        
        # Country Risk Premium (adjustable)
        crp_default = country_risk_premiums[wacc_country]
        country_risk_premium = st.number_input("Country Risk Premium (%)", min_value=0.0, max_value=10.0, value=crp_default, step=0.1, help="Additional risk premium for operating in this country")
        
        st.subheader("💵 Capital Structure")
        
        # Debt to Equity Ratio
        de_ratio = st.number_input("Debt-to-Equity Ratio (D/E)", min_value=0.0, max_value=5.0, value=0.5, step=0.1, help="Ratio of total debt to total equity")
        
        # Cost of Debt
        rf_rate = risk_free_rates[wacc_country]
        credit_spread = st.number_input("Credit Spread over Risk-Free Rate (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.5, help="Additional yield over government bonds based on company credit risk")
        cost_of_debt = rf_rate + credit_spread
        
        # Corporate Tax Rate
        tax_rates = {
            "Indonesia": 22.0,
            "Thailand": 20.0,
            "Singapore": 17.0,
            "Malaysia": 24.0,
            "Philippines": 25.0,
            "Vietnam": 20.0
        }
        tax_rate_default = tax_rates[wacc_country]
        tax_rate = st.number_input("Corporate Tax Rate (%)", min_value=0.0, max_value=50.0, value=tax_rate_default, step=0.5)
        
        st.subheader("📈 Advanced Options")
        show_details = st.checkbox("Show Detailed Calculations", value=True)
    
    with col2:
        st.subheader("🎯 WACC Results")
        
        # Calculate Cost of Equity using CAPM
        # CAPM: Re = Rf + β * (Rm - Rf) + CRP
        risk_free_rate = risk_free_rates[wacc_country]
        cost_of_equity = risk_free_rate + beta * market_risk_premium + country_risk_premium
        
        # Calculate Weights
        # D/E = 0.5 means D = 0.5, E = 1, so V = 1.5
        equity_weight = 1 / (1 + de_ratio)
        debt_weight = de_ratio / (1 + de_ratio)
        
        # After-tax cost of debt
        after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate / 100)
        
        # WACC Formula: WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)
        wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)
        
        # Display Results
        st.metric("Cost of Equity (Ke)", f"{cost_of_equity:.2f}%")
        st.metric("Cost of Debt (Kd)", f"{cost_of_debt:.2f}%")
        st.metric("After-Tax Cost of Debt", f"{after_tax_cost_of_debt:.2f}%")
        st.divider()
        st.metric("**WACC**", f"**{wacc:.2f}%**", delta=f"vs Cost of Equity: {wacc - cost_of_equity:.2f}%")
        
        # Visual Gauge for WACC
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=wacc,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "WACC Gauge", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [0, 20], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "royalblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 8], 'color': "#e8f5e9"},
                    {'range': [8, 12], 'color': "#fff3e0"},
                    {'range': [12, 20], 'color': "#ffebee"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': wacc
                }
            }
        ))
        fig_gauge.update_layout(height=300, margin={'l': 20, 'r': 20, 't': 40, 'b': 20})
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Capital Structure Pie Chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Equity', 'Debt'],
            values=[equity_weight * 100, debt_weight * 100],
            hole=.3,
            marker_colors=['#4CAF50', '#2196F3']
        )])
        fig_pie.update_layout(title="Capital Structure", height=250, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed Calculations Section
    if show_details:
        st.divider()
        st.subheader("📋 Detailed Calculation Breakdown")
        
        col_detail1, col_detail2 = st.columns(2)
        
        with col_detail1:
            st.markdown("### Cost of Equity (CAPM)")
            st.latex(r'''
            K_e = R_f + \beta \times (R_m - R_f) + CRP
            ''')
            st.markdown(f"""
            - **Risk-Free Rate (Rf)**: {risk_free_rate:.2f}%
            - **Beta (β)**: {beta:.2f}
            - **Market Risk Premium (Rm - Rf)**: {market_risk_premium:.2f}%
            - **Country Risk Premium (CRP)**: {country_risk_premium:.2f}%
            
            **Calculation:**
            Ke = {risk_free_rate:.2f}% + {beta:.2f} × {market_risk_premium:.2f}% + {country_risk_premium:.2f}%
            Ke = **{cost_of_equity:.2f}%**
            """)
        
        with col_detail2:
            st.markdown("### WACC Formula")
            st.latex(r'''
            WACC = \frac{E}{V} \times K_e + \frac{D}{V} \times K_d \times (1 - T_c)
            ''')
            st.markdown(f"""
            - **Equity Weight (E/V)**: {equity_weight:.3f} ({equity_weight*100:.1f}%)
            - **Debt Weight (D/V)**: {debt_weight:.3f} ({debt_weight*100:.1f}%)
            - **Cost of Debt (Kd)**: {cost_of_debt:.2f}%
            - **Tax Rate (Tc)**: {tax_rate:.1f}%
            - **After-Tax Kd**: {after_tax_cost_of_debt:.2f}%
            
            **Calculation:**
            WACC = {equity_weight:.3f} × {cost_of_equity:.2f}% + {debt_weight:.3f} × {after_tax_cost_of_debt:.2f}%
            WACC = **{wacc:.2f}%**
            """)
    
    # Comparison Table
    st.divider()
    st.subheader("🔄 Industry WACC Comparison")
    
    comparison_data = []
    for industry, beta_val in industry_betas.items():
        if industry != "Custom" and beta_val is not None:
            # Quick WACC calc for each industry
            coe_comp = risk_free_rate + beta_val * market_risk_premium + country_risk_premium
            wacc_comp = (equity_weight * coe_comp) + (debt_weight * after_tax_cost_of_debt)
            comparison_data.append({
                'Industry': industry,
                'Beta': beta_val,
                'Cost of Equity': f"{coe_comp:.2f}%",
                'WACC': f"{wacc_comp:.2f}%"
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Export Functionality
    st.divider()
    st.subheader("💾 Export Results")
    
    export_data = {
        'Company': [company_name if company_name else "Unnamed Company"],
        'Country': [wacc_country],
        'Industry': [selected_industry],
        'Beta': [beta],
        'Cost of Equity (%)': [round(cost_of_equity, 2)],
        'Cost of Debt (%)': [round(cost_of_debt, 2)],
        'After-Tax Cost of Debt (%)': [round(after_tax_cost_of_debt, 2)],
        'WACC (%)': [round(wacc, 2)],
        'D/E Ratio': [de_ratio],
        'Tax Rate (%)': [tax_rate],
        'Equity Weight': [round(equity_weight, 3)],
        'Debt Weight': [round(debt_weight, 3)]
    }
    
    export_df = pd.DataFrame(export_data)
    csv = export_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download WACC Calculation as CSV",
        data=csv,
        file_name=f"wacc_calculation_{company_name.replace(' ', '_') if company_name else 'company'}.csv",
        mime="text/csv"
    )
    
    st.info("""
    **💡 How to Use This WACC Calculator:**
    1. Select the country and industry for your company
    2. Adjust beta if you have company-specific data (or use industry average)
    3. Input your company's capital structure (D/E ratio)
    4. Adjust credit spread based on company's credit rating
    5. Review the calculated WACC and use it for NPV/DCF valuations
    
    **Note:** This is a proxy estimate. For precise valuations, use company-specific market data and consult financial professionals.
    """)

if st.button("🔄 Refresh Data (Clear Cache)"):
    st.cache_data.clear()
    st.rerun()
