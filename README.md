# 📊 ASEAN Macro Dashboard

A professional Streamlit dashboard for analyzing macroeconomic indicators across ASEAN economies, designed for economists and policy analysts.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

- **Real-Time Data**: Fetches live data from World Bank API and Yahoo Finance
- **6 ASEAN Countries**: Indonesia, Thailand, Singapore, Malaysia, Philippines, Vietnam
- **Key Indicators**:
  - GDP Growth (Annual %)
  - Current Account Balance (% of GDP)
  - 10-Year Government Bond Yields (Market Sentiment)
  - Exchange Rates (USD vs Local Currency)
- **Forecasting**: SARIMA model predicts economic trends for the next 4 years
- **Interactive Visualizations**: Plotly charts with hover insights and dual-axis views
- **Executive Summary**: Auto-generated policy insights and risk alerts

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository** (or download the script):
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas numpy plotly yfinance statsmodels requests
   ```

3. **Run the dashboard**:
   ```bash
   streamlit run asean_macro_dashboard.py
   ```

4. **Access the app**:
   - Open your browser to `http://localhost:8501`
   - The dashboard will load automatically

## 📖 Usage Guide

### Sidebar Controls
- **Country Selection**: Choose from 6 ASEAN economies
- **Data Sources**: View information about API endpoints
- **Refresh Button**: Clear cache and reload latest data

### Main Dashboard Sections

1. **Current Account Forecast**
   - Historical trends (blue line)
   - 4-year SARIMA forecast (red dotted line)
   - Bond yield overlay (gray dashed line, secondary axis)

2. **GDP Growth Analysis**
   - Annual GDP growth rates
   - Color-coded bars (green = positive, red = negative)
   - Zero-line reference

3. **Executive Summary**
   - Latest economic performance metrics
   - Growth status classification (STRONG/MODERATE/SLOW)
   - Current account position (Surplus/Deficit)
   - Policy warnings for extreme values

## 🔧 Technical Details

### Data Sources

| Indicator | Source | Frequency | Code |
|-----------|--------|-----------|------|
| GDP Growth | World Bank | Annual | `NY.GDP.MKTP.KD.ZG` |
| Current Account | World Bank | Annual | `BN.CAB.XOKA.GD.ZS` |
| Bond Yields | Yahoo Finance | Daily | `{CC}10Y.GOV` |
| FX Rates | Yahoo Finance | Daily | `USD{CC}=X` |

### Forecasting Model

- **Algorithm**: SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous factors)
- **Parameters**: 
  - Order: (1,1,1)
  - Seasonal Order: (1,1,1,4)
- **Forecast Horizon**: 4 years ahead
- **Note**: Uses annual data; quarterly indicators not available for all countries

### Caching Strategy

- World Bank data: Cached for 24 hours (`ttl=86400`)
- Market data: Cached for 1 hour (`ttl=3600`)
- Manual refresh available via UI button

## ⚠️ Known Limitations

1. **Data Availability**: 
   - Some fiscal indicators (government debt, deficit) have limited recent data for certain countries
   - Vietnam bond yield data may be sparse on Yahoo Finance

2. **Forecast Accuracy**:
   - SARIMA models assume historical patterns continue
   - External shocks (pandemics, crises) may reduce forecast reliability
   - Best used as a directional guide, not precise prediction

3. **API Dependencies**:
   - World Bank API may experience temporary downtime
   - Yahoo Finance ticker symbols may change over time

## 🛠️ Troubleshooting

### Common Issues

**"Could not retrieve World Bank data"**
- Check internet connection
- Wait 5 minutes and click "Refresh Data"
- Try a different country (some have more complete data)

**"Not enough historical data"**
- Select a country with longer data history (Singapore, Thailand have best coverage)
- World Bank updates annual data with 1-2 year lag

**ModuleNotFoundError**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.8+

### Logs & Debugging

- View detailed errors in Streamlit logs (bottom-right "Manage app" on Streamlit Cloud)
- Add `st.write()` statements for debugging data shapes
- Check World Bank API directly: https://data.worldbank.org/

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or suggestions, please open an issue in the repository.

---

**Built with ❤️ for ASEAN Economic Analysis**

*Last Updated: 2024*
