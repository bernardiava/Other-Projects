# 🇮🇩 Indonesian Stock Market Optimizer & Forecaster

## Overview
A professional-grade portfolio optimization and AI-powered forecasting tool for Indonesian stocks (IDX), designed with top-tier CFA methodology and cutting-edge data science techniques.

## Features

### 🎯 Multi-Strategy Portfolio Optimization
- **Max Sharpe Ratio**: Optimize for best risk-adjusted returns
- **Min Volatility**: Minimum variance portfolio for risk-averse investors
- **Max Sortino Ratio**: Focus on downside risk adjustment
- **Min Drawdown**: Protect against maximum losses
- **Balanced**: Customizable risk-return tradeoff
- **Aggressive**: Higher risk tolerance for growth seekers
- **Conservative**: Capital preservation focus

### 🔮 Advanced Forecasting Models
- **LSTM (Long Short-Term Memory)**: Deep learning neural networks for sequence prediction
- **ARIMA/SARIMA**: Statistical time series modeling with seasonality
- **GARCH**: Volatility clustering and conditional heteroskedasticity
- **Ensemble**: Combined predictions from multiple models

### 📊 Professional Risk Metrics (CFA Standards)
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Value at Risk (VaR 95%)
- Conditional VaR (CVaR/Expected Shortfall)
- Beta & Alpha
- Calmar Ratio
- Annualized Volatility

### 💡 Smart Recommendations
- Risk-profile based stock recommendations (Conservative/Moderate/Aggressive)
- Detailed rationale and risk commentary
- Forecast-based scoring system
- Exportable reports

### 🎨 Premium UI/UX Design
- Interactive Plotly visualizations
- Clean, modern Streamlit interface
- Responsive layout with custom CSS styling
- Intuitive sidebar configuration
- Real-time progress indicators

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas numpy scipy scikit-learn plotly streamlit yfinance statsmodels arch tensorflow joblib
```

## Usage

### Launch the Application
```bash
streamlit run indo_stock_optimizer.py
```

### Configuration Options

1. **Date Range**: Select historical period for analysis
2. **Risk Appetite**: Choose Conservative, Moderate, or Aggressive
3. **Portfolio Strategy**: Select optimization objective
4. **Forecast Horizon**: 5, 10, 20, or 30 trading days
5. **Forecast Models**: Choose LSTM, ARIMA, GARCH, or combination

### Output Sections

1. **Portfolio Performance Metrics**: Key risk-return statistics
2. **Portfolio Allocation**: Interactive pie chart of optimal weights
3. **Risk-Return Profile**: Efficient frontier visualization
4. **Strategy Comparison**: Compare all optimization strategies
5. **Correlation Matrix**: Asset correlation heatmap
6. **Individual Stock Analysis**: Detailed metrics table
7. **AI Forecasting**: Price predictions with multiple models
8. **Smart Recommendations**: BUY/HOLD/AVOID signals with commentary
9. **Export**: Download CSV reports

## Indonesian Stocks Covered

### Banking & Financial Services
- BBCA.JK: Bank Central Asia Tbk
- BBRI.JK: Bank Rakyat Indonesia Tbk
- BMRI.JK: Bank Mandiri Tbk
- BBNI.JK: Bank Negara Indonesia Tbk
- BRIS.JK: Bank Syariah Indonesia Tbk

### Telecommunications
- TLKM.JK: Telkom Indonesia Tbk
- EXCL.JK: XL Axiata Tbk
- ISAT.JK: Indosat Tbk

### Consumer Goods
- ICBP.JK: Indofood CBP Sukses Makmur Tbk
- INDF.JK: Indofood Sukses Makmur Tbk
- UNVR.JK: Unilever Indonesia Tbk
- KLBF.JK: Kalbe Farma Tbk

### Energy & Mining
- ANTM.JK: Aneka Tambang Tbk
- ADRO.JK: Adaro Energy Indonesia Tbk
- ITMG.JK: Indo Tambangraya Megah Tbk
- PTBA.JK: Bukit Asam Tbk

### Infrastructure & Property
- ASII.JK: Astra International Tbk
- UNTR.JK: United Tractors Tbk
- BSDE.JK: Bumi Serpong Damai Tbk

### Technology
- GOTO.JK: GoTo Gojek Tokopedia Tbk
- BUKA.JK: Bukalapak.com Tbk

## Best Practices

### Forecasting Period
- **Short-term (5-10 days)**: Trading opportunities, higher uncertainty
- **Medium-term (20 days)**: Monthly outlook, balanced reliability
- **Long-term (30+ days)**: Strategic positioning, use with caution

### Risk Management
1. Diversify across sectors (banking, consumer, energy, tech)
2. Rebalance quarterly based on new optimizations
3. Implement stop-loss protocols
4. Monitor macroeconomic indicators (BI rate, IDR/USD, inflation)

### Investment Strategy
- **Dollar-Cost Averaging**: Build positions gradually
- **Core-Satellite Approach**: Core holdings (BBCA, TLKM, UNVR) + satellite picks
- **Sector Rotation**: Adjust based on economic cycle

## Disclaimer

⚠️ **This tool is for educational and informational purposes only.**

- Past performance does not guarantee future results
- All investments carry risks, including potential loss of principal
- Indonesian equities are subject to emerging market volatility
- Currency risk exists for USD-based investors (IDR fluctuations)
- Consult with a licensed financial advisor before making investment decisions
- Data sourced from Yahoo Finance; delays may occur

## Technical Architecture

```
indo_stock_optimizer.py
├── Data Fetching Layer (yfinance)
├── Preprocessing Module
├── RiskMetrics Class (CFA standards)
├── PortfolioOptimizer Class (scipy.optimize)
├── ForecastingEngine Class
│   ├── LSTM (TensorFlow/Keras)
│   ├── ARIMA/SARIMA (statsmodels)
│   └── GARCH (arch package)
├── VisualizationEngine Class (Plotly)
├── RecommendationEngine Class
└── Streamlit UI Layer
```

## Performance Optimizations

1. **Caching**: Streamlit @st.cache_data for data fetching
2. **Parallel Processing**: Multi-threaded data downloads
3. **Efficient Algorithms**: SLSQP optimization with analytical gradients
4. **Memory Management**: Limited ticker universe for responsiveness
5. **Early Stopping**: LSTM training with validation monitoring

## Author Notes

Built following:
- CFA Institute portfolio management standards
- Quantitative finance best practices
- Modern UI/UX design principles
- Production-ready code architecture

---

**Version**: 1.0.0  
**Last Updated**: 2025  
**License**: MIT License
