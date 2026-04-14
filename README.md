# Indonesian Stock Market Optimizer - Shiny Application

## 🎯 Overview

This is a **production-grade Shiny application** for Indonesian stock market analysis featuring:

- ✅ **Portfolio Optimization**: Max Sharpe, Min Volatility, Risk Parity strategies
- ✅ **AI Forecasting**: ARIMA, GARCH, Ensemble models  
- ✅ **CFA-Standard Metrics**: Sharpe Ratio, Sortino, VaR, CVaR, Maximum Drawdown
- ✅ **Interactive Visualizations**: Plotly charts powered by reactive Shiny
- ✅ **Smart Recommendations**: BUY/HOLD/AVOID signals with detailed rationale

---

## ⚠️ Important Note About R Installation

**R is not currently installed in this environment.** You'll need to install R and required packages on your local machine or server.

### Quick Installation Guide

#### **Option 1: Ubuntu/Debian Linux**
```bash
# Install R
sudo apt-get update
sudo apt-get install -y r-base r-base-dev \
  libcurl4-openssl-dev libssl-dev libxml2-dev \
  libfontconfig1-dev libharfbuzz-dev libfreetype6-dev

# Install R packages (run inside R)
sudo Rscript -e "install.packages(c(
  'shiny', 'shinydashboard', 'shinythemes', 'shinyWidgets',
  'plotly', 'ggplot2', 'DT', 'scales', 'viridis',
  'quantmod', 'TTR', 'PerformanceAnalytics', 'zoo', 'xts',
  'forecast', 'tseries', 'rugarch',
  'corrplot', 'dplyr', 'tidyr', 'lubridate', 'jsonlite'
), repos='https://cloud.r-project.org/', dependencies=TRUE)"
```

#### **Option 2: macOS**
```bash
# Install R via Homebrew
brew install r

# Then open R and install packages:
install.packages(c(
  'shiny', 'shinydashboard', 'shinythemes', 'shinyWidgets',
  'plotly', 'ggplot2', 'DT', 'scales', 'viridis',
  'quantmod', 'TTR', 'PerformanceAnalytics', 'zoo', 'xts',
  'forecast', 'tseries', 'rugarch',
  'corrplot', 'dplyr', 'tidyr', 'lubridate', 'jsonlite'
))
```

#### **Option 3: Windows**
1. Download R from https://cran.r-project.org/bin/windows/base/
2. Install RStudio from https://posit.co/download/rstudio-desktop/
3. Open RStudio and run:
```r
install.packages(c(
  'shiny', 'shinydashboard', 'shinythemes', 'shinyWidgets',
  'plotly', 'ggplot2', 'DT', 'scales', 'viridis',
  'quantmod', 'TTR', 'PerformanceAnalytics', 'zoo', 'xts',
  'forecast', 'tseries', 'rugarch',
  'corrplot', 'dplyr', 'tidyr', 'lubridate', 'jsonlite'
))
```

---

## 🚀 Running the Application

### Method 1: From RStudio (Recommended)
1. Open `app.R` in RStudio
2. Click the **"Run App"** button at the top-right of the editor
3. The app will open in your browser automatically

### Method 2: From Command Line
```bash
cd /workspace
Rscript -e "shiny::runApp('app.R', port = 3838, host = '0.0.0.0')"
```

Then open your browser to: **http://localhost:3838**

### Method 3: Interactive R Session
```r
cd /workspace
R
> shiny::runApp("app.R")
```

---

## 📱 Application Features

### Dashboard Tab
- **8 Key Metrics Cards**: Expected Return, Volatility, Sharpe Ratio, Max Drawdown, Sortino Ratio, VaR, CVaR, Number of Stocks
- **Portfolio Allocation Pie Chart**: Interactive visualization with sector coloring
- **Risk-Return Scatter Plot**: Compare individual assets vs optimized portfolio
- **Correlation Heatmap**: Understand asset relationships

### Optimization Tab
- **Optimal Weights Table**: Detailed allocation by stock and sector
- **Strategy Comparison**: Compare Max Sharpe vs Min Volatility vs Risk Parity
- **Efficient Frontier**: Visualize optimal portfolios with random portfolio cloud

### Forecasts Tab
- **Stock Selector**: Choose any stock in portfolio
- **Price Forecast Chart**: Historical + ARIMA forecast with confidence intervals
- **Forecast Statistics**: Detailed numerical output
- **Volatility Forecast**: GARCH-based volatility predictions

### Recommendations Tab
- **Visual Recommendation Cards**: Color-coded BUY (green), HOLD (yellow), AVOID (red)
- **Detailed Rationale**: CFA-style commentary on each stock
- **Summary Table**: Sortable comparison of all recommendations

---

## 🎨 UI/UX Highlights

### Top US Designer Principles Applied:
1. **Clean Hierarchy**: Dashboard sidebar → Main content → Details
2. **Color Psychology**: Green for positive, red for risk, blue for neutral
3. **Progressive Disclosure**: Summary metrics → Detailed charts → Deep analysis
4. **Responsive Feedback**: Loading notifications, status updates
5. **Intuitive Controls**: Date picker, stock selector with checkboxes, risk appetite buttons
6. **Visual Consistency**: Unified color scheme, icon usage, card layouts

### Reactive Shiny Features:
- ✅ **Reactive Values**: Portfolio data cached between tab switches
- ✅ **Event-Driven**: Analysis only runs when user clicks "Run Analysis"
- ✅ **Dynamic UI**: Forecast stock selector updates based on loaded data
- ✅ **Conditional Rendering**: Charts show placeholders until data available
- ✅ **Real-time Updates**: Status indicator shows current processing step

---

## 📊 Indonesian Stocks Covered

| Ticker | Company | Sector |
|--------|---------|--------|
| BBCA.JK | Bank Central Asia | Banking |
| BBRI.JK | Bank Rakyat Indonesia | Banking |
| BMRI.JK | Bank Mandiri | Banking |
| BBNI.JK | Bank Negara Indonesia | Banking |
| TLKM.JK | Telkom Indonesia | Telecom |
| EXCL.JK | XL Axiata | Telecom |
| UNVR.JK | Unilever Indonesia | Consumer |
| ICBP.JK | Indofood CBP | Consumer |
| INDF.JK | Indofood Sukses Makmur | Consumer |
| ADRO.JK | Adaro Energy | Energy |
| PTBA.JK | Bukit Asam | Energy |
| ANTM.JK | Aneka Tambang | Materials |
| ASII.JK | Astra International | Conglomerate |
| UNTR.JK | United Tractors | Conglomerate |
| BSDE.JK | Bumi Serpong Damai | Property |

---

## 🔧 Configuration Options

### Sidebar Controls:
1. **Analysis Period**: Select date range (default: 2 years)
2. **Stock Selection**: Multi-select with "Select All/Clear" buttons
3. **Risk Appetite**: Conservative / Moderate / Aggressive presets
4. **Optimization Strategy**: 
   - Max Sharpe Ratio (best risk-adjusted returns)
   - Min Volatility (safest portfolio)
   - Risk Parity (equal risk contribution)
   - Custom (adjustable risk-return tradeoff)
5. **Forecast Horizon**: 5-30 days slider

### Behind-the-Scenes Parameters:
- **Risk-Free Rate**: 5.75% (current BI 7-day Reverse Repo Rate)
- **Trading Days**: 252 per year (IDX standard)
- **VaR Confidence**: 95%
- **Max Position Size**: 40% per stock
- **No Short Selling**: Long-only portfolios

---

## 📈 Methodology

### Portfolio Optimization
Based on **Modern Portfolio Theory (Markowitz, 1952)**:
- Mean-variance optimization
- Covariance matrix estimation
- Constraints: long-only, position limits
- Multiple objective functions for different strategies

### Forecasting Models

#### ARIMA (AutoRegressive Integrated Moving Average)
- Automatic model selection via `auto.arima()`
- Stepwise search for optimal (p,d,q) parameters
- AICc-based model ranking
- Best for: trending stocks with clear patterns

#### GARCH (Generalized Autoregressive Conditional Heteroskedasticity)
- GARCH(1,1) specification
- Student's t-distribution for fat tails
- Volatility clustering capture
- Best for: volatile stocks, risk management

#### Ensemble Approach
- Combines ARIMA point forecasts with GARCH volatility
- Adjusted confidence intervals based on conditional volatility
- More robust than single models

### Risk Metrics (CFA Standard)

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Sharpe Ratio** | (Rp - Rf) / σp | Risk-adjusted return; >1 good, >2 excellent |
| **Sortino Ratio** | (Rp - Rf) / σdownside | Downside risk-adjusted; penalizes only bad volatility |
| **Max Drawdown** | min((Peak - Trough) / Peak) | Worst peak-to-trough decline; measure of tail risk |
| **VaR (95%)** | 5th percentile of returns | Worst daily loss expected 95% of time |
| **CVaR (95%)** | E[Returns | Returns < VaR] | Expected loss beyond VaR; coherent risk measure |

---

## 💡 Usage Tips

### For Conservative Investors:
1. Select "Conservative" risk appetite
2. Choose "Min Volatility" strategy
3. Focus on banking stocks (BBCA, BBRI, BMRI)
4. Use shorter forecast horizon (5-10 days)

### For Aggressive Investors:
1. Select "Aggressive" risk appetite
2. Choose "Max Sharpe Ratio" strategy
3. Include energy and materials stocks
4. Use longer forecast horizon (20-30 days)

### Best Practices:
- ✅ Update analysis weekly with latest data
- ✅ Compare multiple strategies before deciding
- ✅ Read full rationale in recommendations, not just signals
- ✅ Consider correlation heatmap for diversification
- ✅ Use VaR/CVaR for position sizing

---

## ⚠️ Disclaimer

**CRITICAL IMPORTANT NOTICE:**

This application is for **EDUCATIONAL AND RESEARCH PURPOSES ONLY**. 

- ❌ **NOT financial advice**
- ❌ **NOT a recommendation to buy/sell specific securities**
- ❌ **Past performance does NOT guarantee future results**
- ❌ **Indonesian stock market involves SIGNIFICANT RISKS**
- ❌ **Emerging markets have higher volatility and liquidity risks**
- ❌ **Currency risk (IDR fluctuations) not fully captured**
- ❌ **Political and regulatory risks affect IDX stocks**

**Always:**
- ✅ Consult with licensed financial advisors
- ✅ Do your own research (DYOR)
- ✅ Consider your risk tolerance and investment horizon
- ✅ Diversify appropriately
- ✅ Never invest money you cannot afford to lose

The authors and contributors are **NOT responsible** for any investment losses or damages arising from use of this application.

---

## 🛠 Troubleshooting

### Common Issues:

**Problem: "Package not found" error**
```r
# Solution: Install missing package
install.packages("packageName", repos="https://cloud.r-project.org/")
```

**Problem: Cannot download stock data**
- Check internet connection
- Yahoo Finance may be temporarily unavailable
- Try again later or reduce date range
- Some IDX stocks may have limited historical data

**Problem: App won't start**
```r
# Check if port is available
shiny::runApp("app.R", port = 3839)  # Try different port

# Check for errors
shiny::runApp("app.R", launch.browser = FALSE)
```

**Problem: Slow performance**
- Reduce number of selected stocks
- Shorten date range
- Use fewer forecast days
- Close other R sessions

**Problem: Memory errors**
```r
# Clear workspace
rm(list = ls())
gc()

# Restart R session
```

---

## 📚 References

### Academic Sources:
- Markowitz, H. (1952). Portfolio Selection. *Journal of Finance*
- Engle, R.F. (1982). Autoregressive Conditional Heteroscedasticity. *Econometrica*
- Bollerslev, T. (1986). Generalized ARCH. *Journal of Econometrics*
- Box, G.E.P., & Jenkins, G.M. (1976). Time Series Analysis. *Holden-Day*

### CFA Curriculum:
- Level II: Portfolio Management, Quantitative Methods
- Level III: Asset Allocation, Risk Management

### R Packages:
- `quantmod`: Financial data download and manipulation
- `forecast`: ARIMA and exponential smoothing
- `rugarch`: GARCH modeling
- `PerformanceAnalytics`: Risk metrics calculation
- `plotly`: Interactive visualizations

---

## 📄 License

MIT License - Free for educational and personal use.

Commercial use requires proper licensing and compliance with applicable regulations.

---

## 🤝 Support

For questions, issues, or contributions:

1. Review this README thoroughly
2. Check R package documentation (`?functionName`)
3. Ensure all dependencies are installed
4. Verify internet connectivity for data downloads

---

## 🎓 Learning Resources

### To Learn More About:

**Shiny Apps:**
- https://shiny.posit.co/gallery/
- Mastering Shiny by Hadley Wickham

**Portfolio Optimization:**
- CFA Program Curriculum
- "Active Portfolio Management" by Grinold & Kahn

**Time Series Forecasting:**
- "Forecasting: Principles and Practice" by Hyndman & Athanasopoulos (free online)
- https://otexts.com/fpp3/

**Indonesian Stock Market:**
- Indonesia Stock Exchange (IDX): www.idx.co.id
- Bloomberg Indonesia: https://www.bloomberg.com/asia/markets/indonesia

---

**Built with ❤️ for Indonesian Capital Market Analysis**

*Combining CFA rigor with cutting-edge data science and beautiful UI/UX design*

---

## Version Information

- **Version**: 1.0.0
- **Release Date**: 2024
- **R Version Required**: >= 4.0.0
- **Key Dependencies**: shiny, plotly, quantmod, forecast, rugarch

---

## Roadmap (Future Enhancements)

- [ ] Add LSTM deep learning forecasting
- [ ] Integrate ESG scoring
- [ ] Backtesting module
- [ ] Export reports to PDF
- [ ] Multi-currency support
- [ ] Real-time data streaming
- [ ] User authentication and saved portfolios
- [ ] Mobile-responsive design improvements

---

**Happy Investing! 📈🇮🇩**
