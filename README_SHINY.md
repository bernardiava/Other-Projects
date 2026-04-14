# Indonesian Stock Market Optimizer & Forecaster
## Shiny Application for Portfolio Optimization with AI Forecasting

### Overview
This is a production-grade Shiny application for analyzing Indonesian stocks with:
- **Portfolio Optimization**: Max Sharpe, Min Volatility, Risk-Parity strategies
- **AI Forecasting**: ARIMA, GARCH, LSTM-inspired ensemble models
- **CFA-Standard Metrics**: Sharpe Ratio, Sortino, VaR, CVaR, Maximum Drawdown
- **Interactive Visualizations**: Plotly charts, dynamic risk profiling
- **Smart Recommendations**: BUY/HOLD/AVOID signals with rationale

---

## Installation Instructions

### Step 1: Install R (if not already installed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y r-base r-base-dev libcurl4-openssl-dev libssl-dev libxml2-dev libfontconfig1-dev libharfbuzz-dev libfreetype6-dev
```

**macOS:**
```bash
brew install r
```

**Windows:**
Download from https://cran.r-project.org/bin/windows/base/

---

### Step 2: Install Required R Packages

Open R or RStudio and run:

```r
# Install CRAN packages
install.packages(c(
  "shiny", "shinydashboard", "shinythemes", "shinyWidgets",
  "plotly", "ggplot2", "DT", "scales", "viridis",
  "quantmod", "TTR", "PerformanceAnalytics", "zoo", "xts",
  "forecast", "tseries", "rugarch", "fGarch",
  "PortfolioAnalytics", "ROI", "ROI.plugin.quadprog",
  "corrplot", "heatmaply", "dplyr", "tidyr", "lubridate",
  "jsonlite", "httr", "readr"
), dependencies = TRUE)

# For better performance (optional but recommended)
install.packages(c("data.table", "Rcpp"))
```

---

### Step 3: Run the Application

**Option A: From RStudio**
1. Open `app.R` in RStudio
2. Click "Run App" button

**Option B: From Command Line**
```bash
cd /path/to/indo_stock_shiny
Rscript -e "shiny::runApp(port = 3838, host = '0.0.0.0')"
```

Then open browser to: `http://localhost:3838`

---

## Application Features

### 1. Dashboard Overview
- Real-time portfolio metrics
- Interactive asset allocation charts
- Risk-return scatter plot with efficient frontier
- Correlation heatmap

### 2. Optimization Strategies
- **Max Sharpe Ratio**: Optimal risk-adjusted returns
- **Min Volatility**: Minimum variance portfolio
- **Risk Parity**: Equal risk contribution
- **Custom Risk Profile**: Conservative/Moderate/Aggressive presets

### 3. AI Forecasting Models
- **ARIMA/SARIMA**: Statistical time series forecasting
- **GARCH**: Volatility clustering analysis
- **Ensemble**: Combined model predictions
- Forecast horizons: 5, 10, 20, 30 days

### 4. Stock Recommendations
- BUY/HOLD/AVOID signals
- Risk commentary per stock
- Expected return vs drawdown analysis
- CFA-style investment thesis

### 5. Indonesian Stocks Covered
- **Banking**: BBCA.JK, BBRI.JK, BMRI.JK, BBNI.JK
- **Telecom**: TLKM.JK, EXCL.JK
- **Consumer**: ICBP.JK, UNVR.JK, INDF.JK
- **Energy**: ADRO.JK, PTBA.JK, ANTM.JK
- **Conglomerate**: ASII.JK, UNTR.JK
- **Property**: BSDE.JK, SMRA.JK

---

## File Structure

```
indo_stock_shiny/
├── app.R                 # Main Shiny application
├── global.R              # Global functions and data loading
├── ui.R                  # User interface definition
├── server.R              # Server logic and reactivity
├── modules/
│   ├── optimization.R    # Portfolio optimization functions
│   ├── forecasting.R     # AI forecasting models
│   ├── visualization.R   # Plotly/ggplot2 visualizations
│   └── recommendations.R # Stock recommendation engine
├── www/
│   ├── style.css         # Custom CSS styling
│   └── logo.png          # Optional logo
├── data/
│   └── historical_data.csv # Cached historical data
└── README.md             # This file
```

---

## Usage Guide

### Quick Start
1. Launch the application
2. Select date range in sidebar (default: 2 years)
3. Choose your risk appetite:
   - **Conservative**: Low volatility, stable returns
   - **Moderate**: Balanced risk-return
   - **Aggressive**: Higher returns, higher volatility
4. Select optimization strategy
5. Set forecast horizon (5-30 days)
6. Click "Run Analysis"

### Understanding Outputs

#### Portfolio Metrics Panel
- **Expected Annual Return**: Projected yearly return
- **Annual Volatility**: Standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Sortino Ratio**: Downside risk-adjusted return
- **Max Drawdown**: Worst peak-to-trough decline
- **VaR (95%)**: Value at Risk - worst 5% daily loss
- **CVaR (95%)**: Conditional VaR - expected loss beyond VaR

#### Asset Allocation Chart
- Pie chart showing optimal weight distribution
- Hover for exact percentages
- Color-coded by sector

#### Forecast Charts
- Historical prices (black line)
- Forecasted prices (blue line with confidence interval)
- Shaded area shows 95% confidence band

#### Recommendations Table
- **Signal**: BUY (green), HOLD (yellow), AVOID (red)
- **Confidence**: Model confidence level
- **Expected Return**: Forecasted return over horizon
- **Risk Note**: Commentary on potential drawdowns

---

## Advanced Configuration

### Adding Custom Stocks
Edit `global.R` and add to the stock list:

```r
custom_stocks <- c(
  "YOUR_STOCK.JK"  # Format: SYMBOL.JK
)
```

### Adjusting Risk-Free Rate
In `modules/optimization.R`, modify:

```r
risk_free_rate <- 0.0575  # Current BI rate (5.75%)
```

### Changing Forecast Models
In `modules/forecasting.R`, enable/disable models:

```r
models_to_use <- c("ARIMA", "GARCH", "Ensemble")
# Remove "GARCH" to disable GARCH modeling
```

---

## Performance Optimization Tips

1. **Cache Historical Data**: First run downloads data; subsequent runs use cache
2. **Limit Date Range**: Shorter ranges = faster computation
3. **Use Reactive Values**: Only recalculate when inputs change
4. **Parallel Processing**: For large portfolios, consider `future` package

---

## Troubleshooting

### Common Issues

**Error: Package not found**
```r
# Solution: Install missing package
install.packages("packageName")
```

**Error: Cannot download stock data**
- Check internet connection
- Yahoo Finance may be temporarily unavailable
- Try again later or use cached data

**Error: Insufficient memory**
- Reduce date range
- Limit number of stocks
- Close other R sessions

**Shiny app won't start**
```r
# Check if port is available
shiny::runApp(port = 3839)  # Try different port
```

---

## Disclaimer

⚠️ **Important Notice**:
- This application is for **educational and research purposes only**
- Past performance does not guarantee future results
- Indonesian stock market involves significant risks
- Consult with licensed financial advisors before investing
- The authors are not responsible for any investment losses
- Forecasting models have inherent limitations
- Emerging markets like Indonesia have higher volatility

---

## References & Methodology

### Portfolio Optimization
- Modern Portfolio Theory (Markowitz, 1952)
- Black-Litterman Model extensions
- Risk Parity framework (Qian, 2005)

### Forecasting Models
- ARIMA: Box-Jenkins methodology
- GARCH: Engle (1982), Bollerslev (1986)
- Ensemble methods: Model averaging

### Risk Metrics
- CFA Institute standards
- Basel III VaR requirements
- Best practices for emerging markets

---

## Version History

- **v1.0.0** (2024): Initial release
  - Core optimization engine
  - ARIMA/GARCH forecasting
  - Interactive dashboards
  - Stock recommendations

---

## Support & Contributions

For issues, questions, or contributions:
- Review code in `app.R`, `server.R`, `ui.R`
- Check module files for specific functionality
- Ensure all dependencies are installed

---

## License

MIT License - Free for educational and personal use.
Commercial use requires proper licensing and compliance.

---

**Built with ❤️ for Indonesian Capital Market Analysis**
*Combining CFA rigor with cutting-edge data science*
