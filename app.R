# ================================================================================
# INDONESIAN STOCK MARKET OPTIMIZER & FORECASTER
# Production-Grade Shiny Application with CFA Methodology
# ================================================================================
# 
# This application provides:
# - Portfolio optimization (Max Sharpe, Min Vol, Risk Parity)
# - AI forecasting (ARIMA, GARCH, Ensemble)
# - CFA-standard risk metrics
# - Interactive visualizations
# - Smart stock recommendations
#
# Author: Top 0.000001% CFA Holder & Data Scientist
# License: MIT
# ================================================================================

library(shiny)
library(shinydashboard)
library(shinythemes)
library(shinyWidgets)
library(plotly)
library(ggplot2)
library(DT)
library(scales)
library(viridis)
library(quantmod)
library(TTR)
library(PerformanceAnalytics)
library(zoo)
library(xts)
library(forecast)
library(tseries)
library(rugarch)
library(PortfolioAnalytics)
library(corrplot)
library(dplyr)
library(tidyr)
library(lubridate)
library(jsonlite)

# ================================================================================
# GLOBAL VARIABLES & CONFIGURATION
# ================================================================================

# Indonesian stocks universe (IDX/Indonesia Stock Exchange)
INDONESIAN_STOCKS <- c(
  "BBCA.JK",  # Bank Central Asia
  "BBRI.JK",  # Bank Rakyat Indonesia
  "BMRI.JK",  # Bank Mandiri
  "BBNI.JK",  # Bank Negara Indonesia
  "TLKM.JK",  # Telkom Indonesia
  "ASII.JK",  # Astra International
  "UNVR.JK",  # Unilever Indonesia
  "ICBP.JK",  # Indofood CBP
  "ADRO.JK",  # Adaro Energy
  "PTBA.JK",  # Bukit Asam
  "ANTM.JK",  # Aneka Tambang
  "UNTR.JK",  # United Tractors
  "BSDE.JK",  # Bumi Serpong Damai
  "INDF.JK",  # Indofood Sukses Makmur
  "EXCL.JK"   # XL Axiata
)

# Sector mapping
SECTOR_MAP <- list(
  "BBCA.JK" = "Banking", "BBRI.JK" = "Banking", "BMRI.JK" = "Banking", "BBNI.JK" = "Banking",
  "TLKM.JK" = "Telecom", "EXCL.JK" = "Telecom",
  "UNVR.JK" = "Consumer", "ICBP.JK" = "Consumer", "INDF.JK" = "Consumer",
  "ADRO.JK" = "Energy", "PTBA.JK" = "Energy", "ANTM.JK" = "Materials",
  "ASII.JK" = "Conglomerate", "UNTR.JK" = "Conglomerate",
  "BSDE.JK" = "Property"
)

# Color palette by sector
SECTOR_COLORS <- list(
  "Banking" = "#1f77b4",
  "Telecom" = "#ff7f0e",
  "Consumer" = "#2ca02c",
  "Energy" = "#d62728",
  "Materials" = "#9467bd",
  "Conglomerate" = "#8c564b",
  "Property" = "#e377c2"
)

# Risk-free rate (BI 7-day Reverse Repo Rate ~5.75%)
RISK_FREE_RATE <- 0.0575

# ================================================================================
# DATA LOADING FUNCTIONS
# ================================================================================

#' Download historical stock data from Yahoo Finance
#' @param ticker Stock ticker symbol (e.g., "BBCA.JK")
#' @param from Start date
#' @param to End date
#' @return xts object with OHLCV data
download_stock_data <- function(ticker, from, to) {
  tryCatch({
    cat(sprintf("Downloading %s...\n", ticker))
    data <- getSymbols(ticker, from = from, to = to, 
                       auto.assign = FALSE, 
                       src = "yahoo",
                       periodicity = "daily")
    
    # Handle missing data
    if (is.null(data) || nrow(data) == 0) {
      warning(sprintf("No data for %s", ticker))
      return(NULL)
    }
    
    # Clean column names
    colnames(data) <- gsub("\\.[JK]$", "", colnames(data))
    
    return(data)
  }, error = function(e) {
    warning(sprintf("Error downloading %s: %s", ticker, e$message))
    return(NULL)
  })
}

#' Load multiple stocks and combine into portfolio
#' @param tickers Vector of stock tickers
#' @param from Start date
#' @param to End date
#' @return list containing prices and returns
load_portfolio_data <- function(tickers, from, to) {
  cat(sprintf("Loading portfolio data from %s to %s\n", from, to))
  
  # Download all stocks
  stock_list <- lapply(tickers, function(t) {
    data <- download_stock_data(t, from, to)
    if (!is.null(data)) {
      adj_close <- data[, grep("Adjusted|Adj Close", colnames(data), ignore.case = TRUE)[1]]
      if (!is.null(adj_close)) {
        return(Ad(data))  # Use adjusted close
      }
    }
    return(NULL)
  })
  
  # Remove NULL entries
  valid_idx <- !sapply(stock_list, is.null)
  stock_list <- stock_list[valid_idx]
  valid_tickers <- tickers[valid_idx]
  
  if (length(stock_list) == 0) {
    stop("No valid stock data downloaded")
  }
  
  # Merge all price series
  prices <- do.call(merge, stock_list)
  colnames(prices) <- valid_tickers
  
  # Remove rows with NA
  prices <- na.omit(prices)
  
  # Calculate daily returns
  returns <- diff(prices) / lag(prices, k = 1)
  returns <- na.omit(returns)
  
  cat(sprintf("Successfully loaded %d stocks with %d observations\n", 
              ncol(prices), nrow(prices)))
  
  return(list(
    prices = prices,
    returns = returns,
    tickers = valid_tickers
  ))
}

# ================================================================================
# PORTFOLIO OPTIMIZATION FUNCTIONS
# ================================================================================

#' Calculate portfolio metrics
#' @param weights Portfolio weights
#' @param returns Return matrix
#' @param rf Risk-free rate
#' @return Named vector of metrics
calculate_portfolio_metrics <- function(weights, returns, rf = RISK_FREE_RATE) {
  # Portfolio returns
  port_returns <- as.numeric(returns %*% weights)
  
  # Annualized metrics (assuming 252 trading days)
  ann_return <- mean(port_returns) * 252
  ann_volatility <- sd(port_returns) * sqrt(252)
  
  # Sharpe Ratio
  sharpe_ratio <- (ann_return - rf) / ann_volatility
  
  # Sortino Ratio (downside deviation)
  downside_returns <- port_returns[port_returns < 0]
  downside_dev <- if (length(downside_returns) > 0) {
    sd(downside_returns) * sqrt(252)
  } else {
    ann_volatility
  }
  sortino_ratio <- (ann_return - rf) / downside_dev
  
  # Maximum Drawdown
  cum_returns <- cumprod(1 + port_returns)
  running_max <- cummax(cum_returns)
  drawdown <- (cum_returns - running_max) / running_max
  max_drawdown <- min(drawdown)
  
  # Value at Risk (95%)
  var_95 <- quantile(port_returns, 0.05) * sqrt(252)
  
  # Conditional VaR (Expected Shortfall)
  cvar_95 <- mean(port_returns[port_returns <= var_95 / sqrt(252)]) * sqrt(252)
  
  return(c(
    Expected_Return = ann_return,
    Volatility = ann_volatility,
    Sharpe_Ratio = sharpe_ratio,
    Sortino_Ratio = sortino_ratio,
    Max_Drawdown = max_drawdown,
    VaR_95 = var_95,
    CVaR_95 = cvar_95
  ))
}

#' Optimize portfolio using different strategies
#' @param returns Return matrix
#' @param strategy Optimization strategy
#' @param risk_aversion Risk aversion parameter (for custom strategy)
#' @return Optimal weights
optimize_portfolio <- function(returns, strategy = "max_sharpe", risk_aversion = 3) {
  n_assets <- ncol(returns)
  tickers <- colnames(returns)
  
  # Covariance matrix
  cov_matrix <- cov(returns)
  mean_returns <- colMeans(returns) * 252  # Annualized
  
  # Initial equal weights
  init_weights <- rep(1/n_assets, n_assets)
  
  # Objective functions
  if (strategy == "max_sharpe") {
    # Maximize Sharpe Ratio
    objective <- function(w) {
      port_return <- sum(w * mean_returns)
      port_vol <- sqrt(t(w) %*% cov_matrix %*% w)
      -((port_return - RISK_FREE_RATE) / port_vol)  # Negative for minimization
    }
  } else if (strategy == "min_volatility") {
    # Minimize Volatility
    objective <- function(w) {
      sqrt(t(w) %*% cov_matrix %*% w)
    }
  } else if (strategy == "risk_parity") {
    # Risk Parity - equal risk contribution
    objective <- function(w) {
      port_vol <- sqrt(t(w) %*% cov_matrix %*% w)
      marginal_risk <- (cov_matrix %*% w) / port_vol
      risk_contrib <- w * marginal_risk
      target_risk <- port_vol / n_assets
      sum((risk_contrib - target_risk)^2)
    }
  } else if (strategy == "custom") {
    # Custom risk-return tradeoff
    objective <- function(w) {
      port_return <- sum(w * mean_returns)
      port_vol <- sqrt(t(w) %*% cov_matrix %*% w)
      risk_aversion * port_vol - port_return
    }
  }
  
  # Constraints
  constraints <- list(
    lower = rep(0, n_assets),  # No short selling
    upper = rep(0.4, n_assets),  # Max 40% per asset
    meq = 1  # Weights sum to 1
  )
  
  # Optimization using optim
  opt_result <- tryCatch({
    constrOptim(
      theta = init_weights,
      fn = objective,
      ui = rbind(rep(1, n_assets), diag(n_assets)),
      ci = c(1, rep(0, n_assets)),
      method = "L-BFGS-B",
      lower = constraints$lower,
      upper = constraints$upper,
      control = list(maxit = 1000)
    )
  }, error = function(e) {
    # Fallback to equal weights
    list(par = init_weights, value = NA)
  })
  
  weights <- opt_result$par
  
  # Normalize to ensure sum = 1
  weights <- weights / sum(weights)
  
  return(setNames(weights, tickers))
}

# ================================================================================
# FORECASTING FUNCTIONS
# ================================================================================

#' ARIMA forecast for a time series
#' @param prices Price series
#' @param horizon Forecast horizon
#' @return Forecast object
forecast_arima <- function(prices, horizon = 10) {
  tryCatch({
    # Convert to numeric vector
    price_vec <- as.numeric(prices)
    
    # Fit ARIMA model with auto selection
    fit <- auto.arima(price_vec, seasonal = FALSE, 
                      stepwise = TRUE, 
                      approximation = TRUE)
    
    # Generate forecast
    fc <- forecast(fit, h = horizon)
    
    return(fc)
  }, error = function(e) {
    warning(sprintf("ARIMA forecast failed: %s", e$message))
    return(NULL)
  })
}

#' GARCH forecast for volatility
#' @param returns Return series
#' @param horizon Forecast horizon
#' @return List with volatility forecast
forecast_garch <- function(returns, horizon = 10) {
  tryCatch({
    # Specify GARCH(1,1) model
    spec <- ugarchspec(
      variance.model = list(model = "sGARCH", garchOrder = c(1, 1)),
      mean.model = list(armaOrder = c(0, 0), include.mean = TRUE),
      distribution.model = "std"
    )
    
    # Fit model
    fit <- ugarchfit(spec = spec, data = as.numeric(returns), 
                     solver = "hybrid")
    
    # Forecast
    fc <- ugarchforecast(fit, n.ahead = horizon)
    
    # Extract forecasts
    sigma_forecast <- sigma(fc)
    mu_forecast <- fitted(fc)
    
    return(list(
      volatility = sigma_forecast,
      mean = mu_forecast,
      model = fit
    ))
  }, error = function(e) {
    warning(sprintf("GARCH forecast failed: %s", e$message))
    return(NULL)
  })
}

#' Ensemble forecast combining ARIMA and GARCH
#' @param prices Price series
#' @param returns Return series
#' @param horizon Forecast horizon
#' @return Combined forecast
forecast_ensemble <- function(prices, returns, horizon = 10) {
  # Get ARIMA forecast
  arima_fc <- forecast_arima(prices, horizon)
  
  # Get GARCH forecast
  garch_fc <- forecast_garch(returns, horizon)
  
  if (is.null(arima_fc)) {
    return(NULL)
  }
  
  # Simple ensemble: use ARIMA mean, adjust confidence with GARCH vol
  last_price <- as.numeric(last(prices))
  
  # Point forecast from ARIMA
  point_forecast <- arima_fc$mean
  
  # Confidence intervals (using GARCH vol if available)
  if (!is.null(garch_fc)) {
    # Adjust intervals based on GARCH volatility forecast
    avg_garch_vol <- mean(garch_fc$volatility)
    arima_vol <- arima_fc$lower[,2] - arima_fc$lower[,1]  # Width of interval
    adjustment_factor <- avg_garch_vol / sd(as.numeric(returns))
    
    lower_95 <- point_forecast - 1.96 * avg_garch_vol * sqrt(1:horizon) * last_price
    upper_95 <- point_forecast + 1.96 * avg_garch_vol * sqrt(1:horizon) * last_price
  } else {
    lower_95 <- arima_fc$lower[,1]
    upper_95 <- arima_fc$upper[,1]
  }
  
  return(list(
    mean = point_forecast,
    lower = lower_95,
    upper = upper_95,
    last_price = last_price
  ))
}

# ================================================================================
# RECOMMENDATION ENGINE
# ================================================================================

#' Generate stock recommendations based on forecast and risk metrics
#' @param ticker Stock ticker
#' @param forecast Forecast object
#' @param metrics Stock metrics
#' @return Recommendation list
generate_recommendation <- function(ticker, forecast, metrics, current_price) {
  if (is.null(forecast) || is.null(metrics)) {
    return(list(
      ticker = ticker,
      signal = "HOLD",
      confidence = 0.5,
      expected_return = 0,
      rationale = "Insufficient data for analysis"
    ))
  }
  
  # Calculate expected return from forecast
  last_fc <- tail(forecast$mean, 1)
  expected_return <- (last_fc - current_price) / current_price
  
  # Determine signal based on expected return and risk
  if (expected_return > 0.05) {
    signal <- "BUY"
    confidence <- min(0.95, 0.6 + abs(expected_return))
    rationale <- sprintf(
      "Strong upside potential (%.1f%%). %.1f%% Sharpe ratio indicates good risk-adjusted returns.",
      expected_return * 100, metrics["Sharpe_Ratio"]
    )
  } else if (expected_return < -0.05) {
    signal <- "AVOID"
    confidence <- min(0.95, 0.6 + abs(expected_return))
    rationale <- sprintf(
      "Negative outlook (%.1f%% decline expected). High volatility (%.1f%%) increases downside risk.",
      expected_return * 100, metrics["Volatility"] * 100
    )
  } else {
    signal <- "HOLD"
    confidence <- 0.7
    rationale <- sprintf(
      "Neutral outlook. Moderate return (%.1f%%) with acceptable risk profile.",
      expected_return * 100
    )
  }
  
  # Add risk commentary
  if (metrics["Max_Drawdown"] < -0.2) {
    rationale <- paste0(rationale, " WARNING: Historical max drawdown of ",
                        sprintf("%.1f%%", metrics["Max_Drawdown"] * 100),
                        " suggests potential for significant losses.")
  }
  
  if (metrics["VaR_95"] < -0.03) {
    rationale <- paste0(rationale, " Daily VaR(95%) of ",
                        sprintf("%.1f%%", metrics["VaR_95"] * 100),
                        " indicates elevated tail risk.")
  }
  
  return(list(
    ticker = ticker,
    signal = signal,
    confidence = confidence,
    expected_return = expected_return,
    rationale = rationale,
    sector = SECTOR_MAP[[ticker]]
  ))
}

# ================================================================================
# VISUALIZATION FUNCTIONS
# ================================================================================

#' Create interactive portfolio allocation chart
#' @param weights Portfolio weights
#' @return Plotly object
create_allocation_chart <- function(weights) {
  df <- data.frame(
    Stock = names(weights),
    Weight = weights,
    Sector = sapply(names(weights), function(t) SECTOR_MAP[[t]])
  )
  
  df <- df[order(-df$Weight), ]
  
  fig <- plot_ly(
    data = df,
    labels = ~Stock,
    values = ~Weight,
    type = 'pie',
    hole = 0.4,
    marker = list(colors = sapply(df$Sector, function(s) SECTOR_COLORS[[s]])),
    hoverinfo = 'label+value+percent',
    textinfo = 'label+percent'
  ) %>%
    layout(
      title = 'Portfolio Allocation',
      showlegend = TRUE,
      legend = list(x = 1, y = 1),
      annotations = list(
        list(
          text = sprintf("<b>Total Stocks:</b><br>%d", nrow(df)),
          x = 0.5, y = 0.5,
          showarrow = FALSE,
          font = list(size = 12)
        )
      )
    )
  
  return(fig)
}

#' Create risk-return scatter plot
#' @param returns Return matrix
#' @param weights Portfolio weights
#' @return Plotly object
create_risk_return_plot <- function(returns, weights) {
  # Calculate metrics for individual assets
  asset_metrics <- apply(returns, 2, function(x) {
    ann_ret <- mean(x) * 252
    ann_vol <- sd(x) * sqrt(252)
    c(ann_ret, ann_vol)
  })
  
  # Portfolio metrics
  port_metrics <- calculate_portfolio_metrics(weights, returns)
  
  df <- data.frame(
    Asset = colnames(returns),
    Return = asset_metrics[1, ],
    Volatility = asset_metrics[2, ],
    Type = "Asset"
  )
  
  # Add portfolio point
  port_df <- data.frame(
    Asset = "Optimized Portfolio",
    Return = port_metrics["Expected_Return"],
    Volatility = port_metrics["Volatility"],
    Type = "Portfolio"
  )
  
  df <- rbind(df, port_df)
  
  fig <- plot_ly(
    data = df,
    x = ~Volatility,
    y = ~Return,
    color = ~Type,
    colors = c("#1f77b4", "#ff7f0e"),
    mode = 'markers+text',
    marker = list(size = 12),
    text = ~Asset,
    textposition = 'top center',
    hoverinfo = 'text+x+y'
  ) %>%
    layout(
      title = 'Risk-Return Profile',
      xaxis = list(title = 'Annual Volatility (%)', tickformat = '.1%'),
      yaxis = list(title = 'Annual Return (%)', tickformat = '.1%'),
      showlegend = TRUE,
      hovermode = 'closest'
    )
  
  return(fig)
}

#' Create forecast visualization
#' @param prices Historical prices
#' @param forecast Forecast object
#' @param ticker Stock ticker
#' @return Plotly object
create_forecast_plot <- function(prices, forecast, ticker) {
  # Historical data
  hist_df <- data.frame(
    Date = index(tail(prices, 60)),
    Price = as.numeric(tail(prices, 60)),
    Type = "Historical"
  )
  
  # Forecast data
  fc_horizon <- length(forecast$mean)
  last_date <- last(index(prices))
  fc_dates <- seq(last_date + 1, last_date + fc_horizon, by = "day")
  
  fc_df <- data.frame(
    Date = fc_dates,
    Price = as.numeric(forecast$mean),
    Lower = as.numeric(forecast$lower),
    Upper = as.numeric(forecast$upper),
    Type = "Forecast"
  )
  
  # Combine
  all_df <- rbind(hist_df, fc_df)
  
  # Create plot
  fig <- plot_ly() %>%
    add_trace(
      data = hist_df,
      x = ~Date, y = ~Price,
      type = 'scatter',
      mode = 'lines',
      name = 'Historical',
      line = list(color = '#000000', width = 2)
    ) %>%
    add_trace(
      data = fc_df,
      x = ~Date, y = ~Price,
      type = 'scatter',
      mode = 'lines',
      name = 'Forecast',
      line = list(color = '#1f77b4', width = 3)
    ) %>%
    add_trace(
      data = fc_df,
      x = ~Date, y = ~Upper,
      type = 'scatter',
      mode = 'lines',
      name = 'Upper 95%',
      line = list(color = '#1f77b4', width = 1, dash = 'dash'),
      showlegend = FALSE
    ) %>%
    add_trace(
      data = fc_df,
      x = ~Date, y = ~Lower,
      type = 'scatter',
      mode = 'lines',
      name = 'Lower 95%',
      fillcolor = 'rgba(31, 119, 180, 0.2)',
      fill = 'tonexty',
      line = list(color = '#1f77b4', width = 1, dash = 'dash'),
      showlegend = FALSE
    ) %>%
    layout(
      title = sprintf('%s - Price Forecast', ticker),
      xaxis = list(title = 'Date'),
      yaxis = list(title = 'Price (IDR)', tickformat = '$,.0f'),
      hovermode = 'x unified',
      showlegend = TRUE
    )
  
  return(fig)
}

#' Create correlation heatmap
#' @param returns Return matrix
#' @return Plotly object
create_correlation_heatmap <- function(returns) {
  corr_matrix <- cor(returns)
  
  fig <- plot_ly(
    z = corr_matrix,
    x = colnames(returns),
    y = colnames(returns),
    type = 'heatmap',
    colors = 'RdBu',
    zmid = 0,
    hoverongaps = FALSE
  ) %>%
    layout(
      title = 'Asset Correlation Matrix',
      xaxis = list(title = ''),
      yaxis = list(title = '')
    )
  
  return(fig)
}

# ================================================================================
# UI DEFINITION
# ================================================================================

ui <- dashboardPage(
  skin = "blue",
  
  # Header
  dashboardHeader(
    title = span(
      icon("chart-line"),
      "Indonesian Stock Optimizer",
      style = "font-size: 18px; font-weight: bold;"
    ),
    titleWidth = 300,
    
    # Right header items
    tags$li(class = "dropdown",
      tags$a(href = "#", 
             icon("info-circle"), 
             `data-toggle` = "modal", 
             `data-target` = "#aboutModal",
             title = "About")
    )
  ),
  
  # Sidebar
  dashboardSidebar(
    width = 300,
    
    sidebarMenu(
      id = "tabs",
      
      menuItem("Dashboard", tabName = "dashboard", icon = icon("dashboard")),
      menuItem("Optimization", tabName = "optimization", icon = icon("sliders-h")),
      menuItem("Forecasts", tabName = "forecasts", icon = icon("chart-bar")),
      menuItem("Recommendations", tabName = "recommendations", icon = icon("lightbulb"))
    ),
    
    tags$hr(),
    
    # Configuration Panel
    h4(icon("cog"), " Configuration"),
    
    # Date Range
    dateRangeInput(
      inputId = "dateRange",
      label = "Analysis Period:",
      start = Sys.Date() - years(2),
      end = Sys.Date(),
      min = Sys.Date() - years(5),
      max = Sys.Date()
    ),
    
    # Stock Selection
    pickerInput(
      inputId = "selectedStocks",
      label = "Select Stocks:",
      choices = INDONESIAN_STOCKS,
      selected = head(INDONESIAN_STOCKS, 8),
      multiple = TRUE,
      options = list(`actions-box` = TRUE)
    ),
    
    # Risk Appetite
    radioGroupButtons(
      inputId = "riskAppetite",
      label = "Risk Appetite:",
      choices = c("Conservative", "Moderate", "Aggressive"),
      selected = "Moderate",
      justified = TRUE,
      status = "primary"
    ),
    
    # Optimization Strategy
    selectInput(
      inputId = "optStrategy",
      label = "Optimization Strategy:",
      choices = c(
        "Max Sharpe Ratio" = "max_sharpe",
        "Min Volatility" = "min_volatility",
        "Risk Parity" = "risk_parity",
        "Custom" = "custom"
      ),
      selected = "max_sharpe"
    ),
    
    # Forecast Horizon
    sliderInput(
      inputId = "forecastHorizon",
      label = "Forecast Horizon (days):",
      min = 5,
      max = 30,
      value = 10,
      step = 5
    ),
    
    # Run Button
    actionButton(
      inputId = "runAnalysis",
      label = "Run Analysis",
      class = "btn-primary btn-lg",
      style = "width: 100%; margin-top: 10px;"
    ),
    
    tags$hr(),
    
    # Status indicator
    verbatimTextOutput("statusInfo")
  ),
  
  # Main Body
  dashboardBody(
    theme = "bootstrap.css",
    
    # Custom CSS
    tags$head(
      tags$style(HTML("
        .info-box {
          min-height: 100px;
          margin-bottom: 15px;
        }
        .info-box-icon {
          border-radius: 2px;
        }
        .shiny-notification {
          position: fixed;
          top: calc(50% - 50px);
          left: calc(50% - 150px);
          width: 300px;
          height: 100px;
        }
        .rec-card {
          background: white;
          border-left: 5px solid;
          padding: 15px;
          margin-bottom: 15px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .rec-buy { border-left-color: #28a745; }
        .rec-hold { border-left-color: #ffc107; }
        .rec-avoid { border-left-color: #dc3545; }
      "))
    ),
    
    # Tab Items
    tabItems(
      # Dashboard Tab
      tabItem(tabName = "dashboard",
        fluidRow(
          # Metrics Row
          infoBoxOutput("metricReturn", width = 3),
          infoBoxOutput("metricVolatility", width = 3),
          infoBoxOutput("metricSharpe", width = 3),
          infoBoxOutput("metricDrawdown", width = 3)
        ),
        
        fluidRow(
          # Additional Metrics
          infoBoxOutput("metricSortino", width = 3),
          infoBoxOutput("metricVaR", width = 3),
          infoBoxOutput("metricCVaR", width = 3),
          infoBoxOutput("metricStocks", width = 3)
        ),
        
        fluidRow(
          box(
            title = "Portfolio Allocation",
            status = "primary",
            solidHeader = TRUE,
            width = 6,
            plotlyOutput("allocationChart", height = "400px")
          ),
          
          box(
            title = "Risk-Return Profile",
            status = "primary",
            solidHeader = TRUE,
            width = 6,
            plotlyOutput("riskReturnPlot", height = "400px")
          )
        ),
        
        fluidRow(
          box(
            title = "Correlation Heatmap",
            status = "info",
            solidHeader = TRUE,
            width = 12,
            plotlyOutput("correlationHeatmap", height = "500px")
          )
        )
      ),
      
      # Optimization Tab
      tabItem(tabName = "optimization",
        fluidRow(
          box(
            title = "Optimal Weights",
            status = "success",
            solidHeader = TRUE,
            width = 6,
            DT::dataTableOutput("weightsTable")
          ),
          
          box(
            title = "Strategy Comparison",
            status = "info",
            solidHeader = TRUE,
            width = 6,
            plotlyOutput("strategyComparison", height = "400px")
          )
        ),
        
        fluidRow(
          box(
            title = "Efficient Frontier",
            status = "warning",
            solidHeader = TRUE,
            width = 12,
            plotlyOutput("efficientFrontier", height = "500px")
          )
        )
      ),
      
      # Forecasts Tab
      tabItem(tabName = "forecasts",
        fluidRow(
          column(
            width = 12,
            selectInput(
              inputId = "forecastStock",
              label = "Select Stock for Forecast:",
              choices = NULL,
              selected = NULL
            )
          )
        ),
        
        fluidRow(
          box(
            title = "Price Forecast",
            status = "primary",
            solidHeader = TRUE,
            width = 8,
            plotlyOutput("priceForecast", height = "500px")
          ),
          
          box(
            title = "Forecast Statistics",
            status = "info",
            solidHeader = TRUE,
            width = 4,
            verbatimTextOutput("forecastStats")
          )
        ),
        
        fluidRow(
          box(
            title = "Volatility Forecast (GARCH)",
            status = "warning",
            solidHeader = TRUE,
            width = 12,
            plotlyOutput("volatilityForecast", height = "400px")
          )
        )
      ),
      
      # Recommendations Tab
      tabItem(tabName = "recommendations",
        fluidRow(
          box(
            title = "Stock Recommendations",
            subtitle = "AI-powered investment signals with risk commentary",
            status = "success",
            solidHeader = TRUE,
            width = 12,
            uiOutput("recommendationCards")
          )
        ),
        
        fluidRow(
          box(
            title = "Recommendation Summary",
            status = "info",
            solidHeader = TRUE,
            width = 12,
            DT::dataTableOutput("recommendationTable")
          )
        )
      )
    )
  ),
  
  # About Modal
  tags$div(
    class = "modal fade",
    id = "aboutModal",
    tabindex = "-1",
    role = "dialog",
    tags$div(
      class = "modal-dialog modal-lg",
      tags$div(
        class = "modal-content",
        tags$div(
          class = "modal-header bg-blue",
          tags$h4(class = "modal-title", "About Indonesian Stock Optimizer"),
          tags$button(type = "button", class = "close", `data-dismiss` = "modal", HTML("&times;"))
        ),
        tags$div(
          class = "modal-body",
          p(strong("This application provides institutional-grade portfolio optimization and forecasting for Indonesian stocks.")),
          br(),
          tags$ul(
            tags$li("Portfolio optimization using Modern Portfolio Theory"),
            tags$li("AI forecasting with ARIMA and GARCH models"),
            tags$li("CFA-standard risk metrics (Sharpe, Sortino, VaR, CVaR)"),
            tags$li("Smart BUY/HOLD/AVOID recommendations"),
            tags$li("Interactive visualizations for better decision-making")
          ),
          br(),
          tags$p(class = "bg-warning", style = "padding: 15px;",
            strong("DISCLAIMER:"),
            " This application is for educational and research purposes only. Past performance does not guarantee future results. Indonesian stock market involves significant risks. Always consult with licensed financial advisors before making investment decisions."
          )
        ),
        tags$div(
          class = "modal-footer",
          tags$button(type = "button", class = "btn btn-default", `data-dismiss` = "modal", "Close")
        )
      )
    )
  )
)

# ================================================================================
# SERVER LOGIC
# ================================================================================

server <- function(input, output, session) {
  
  # Reactive values
  rv <- reactiveValues(
    data = NULL,
    optimized_portfolio = NULL,
    forecasts = NULL,
    recommendations = NULL,
    analysis_run = FALSE
  )
  
  # Observe run button click
  observeEvent(input$runAnalysis, {
    showNotification("Starting analysis... This may take a few minutes.", type = "message", duration = 3)
    
    # Update status
    updateStatus("Loading data...")
    
    # Load data
    tryCatch({
      data <- load_portfolio_data(
        input$selectedStocks,
        input$dateRange[1],
        input$dateRange[2]
      )
      
      rv$data <- data
      
      # Optimize portfolio
      updateStatus("Optimizing portfolio...")
      
      # Adjust constraints based on risk appetite
      if (input$riskAppetite == "Conservative") {
        strategy <- "min_volatility"
      } else if (input$riskAppetite == "Aggressive") {
        strategy <- "max_sharpe"
      } else {
        strategy <- input$optStrategy
      }
      
      weights <- optimize_portfolio(data$returns, strategy = strategy)
      
      # Calculate metrics
      metrics <- calculate_portfolio_metrics(weights, data$returns)
      
      rv$optimized_portfolio <- list(
        weights = weights,
        metrics = metrics,
        strategy = strategy
      )
      
      # Generate forecasts for each stock
      updateStatus("Generating forecasts...")
      
      forecasts <- lapply(data$tickers, function(ticker) {
        prices <- data$prices[, ticker]
        returns <- data$returns[, ticker]
        
        fc <- forecast_ensemble(prices, returns, input$forecastHorizon)
        
        if (!is.null(fc)) {
          # Calculate individual stock metrics
          stock_metrics <- calculate_portfolio_metrics(
            rep(1, length(data$tickers)),
            data$returns[, ticker, drop = FALSE]
          )
          
          rec <- generate_recommendation(
            ticker = ticker,
            forecast = fc,
            metrics = stock_metrics,
            current_price = as.numeric(last(prices))
          )
          
          return(list(
            ticker = ticker,
            forecast = fc,
            recommendation = rec
          ))
        }
        return(NULL)
      })
      
      # Remove NULL forecasts
      forecasts <- Filter(Negate(is.null), forecasts)
      rv$forecasts <- forecasts
      
      # Extract recommendations
      recommendations <- lapply(forecasts, function(f) f$recommendation)
      rv$recommendations <- recommendations
      
      rv$analysis_run <- TRUE
      
      updateStatus("Analysis complete!")
      showNotification("Analysis completed successfully!", type = "message", duration = 3)
      
    }, error = function(e) {
      showNotification(paste("Error:", e$message), type = "error", duration = 5)
      updateStatus(paste("Error:", e$message))
    })
  })
  
  # Helper function to update status
  updateStatus <- function(msg) {
    output$statusInfo <- renderText({
      msg
    })
  }
  
  # Update forecast stock selector when data loads
  observeEvent(rv$data, {
    if (!is.null(rv$data)) {
      updateSelectInput(
        session,
        "forecastStock",
        choices = rv$data$tickers,
        selected = rv$data$tickers[1]
      )
    }
  })
  
  # Render metric boxes
  output$metricReturn <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("Return", "N/A", icon = icon("arrow-up"), color = "yellow"))
    
    value <- rv$optimized_portfolio$metrics["Expected_Return"]
    infoBox(
      "Expected Return",
      sprintf("%.2f%%", value * 100),
      icon = icon("arrow-up"),
      color = if(value > 0.1) "green" else if(value > 0.05) "yellow" else "red"
    )
  })
  
  output$metricVolatility <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("Volatility", "N/A", icon = icon("chart-line")))
    
    value <- rv$optimized_portfolio$metrics["Volatility"]
    infoBox(
      "Volatility",
      sprintf("%.2f%%", value * 100),
      icon = icon("chart-line"),
      color = if(value < 0.2) "green" else if(value < 0.3) "yellow" else "red"
    )
  })
  
  output$metricSharpe <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("Sharpe Ratio", "N/A", icon = icon("star")))
    
    value <- rv$optimized_portfolio$metrics["Sharpe_Ratio"]
    infoBox(
      "Sharpe Ratio",
      sprintf("%.2f", value),
      icon = icon("star"),
      color = if(value > 1) "green" else if(value > 0.5) "yellow" else "red"
    )
  })
  
  output$metricDrawdown <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("Max Drawdown", "N/A", icon = icon("arrow-down")))
    
    value <- rv$optimized_portfolio$metrics["Max_Drawdown"]
    infoBox(
      "Max Drawdown",
      sprintf("%.2f%%", value * 100),
      icon = icon("arrow-down"),
      color = "red"
    )
  })
  
  output$metricSortino <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("Sortino Ratio", "N/A", icon = icon("star-half-alt")))
    
    value <- rv$optimized_portfolio$metrics["Sortino_Ratio"]
    infoBox(
      "Sortino Ratio",
      sprintf("%.2f", value),
      icon = icon("star-half-alt"),
      color = if(value > 1.5) "green" else if(value > 0.8) "yellow" else "red"
    )
  })
  
  output$metricVaR <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("VaR (95%)", "N/A", icon = icon("exclamation-triangle")))
    
    value <- rv$optimized_portfolio$metrics["VaR_95"]
    infoBox(
      "VaR (95%)",
      sprintf("%.2f%%", value * 100),
      icon = icon("exclamation-triangle"),
      color = "orange"
    )
  })
  
  output$metricCVaR <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("CVaR (95%)", "N/A", icon = icon("fire")))
    
    value <- rv$optimized_portfolio$metrics["CVaR_95"]
    infoBox(
      "CVaR (95%)",
      sprintf("%.2f%%", value * 100),
      icon = icon("fire"),
      color = "red"
    )
  })
  
  output$metricStocks <- renderInfoBox({
    if (!rv$analysis_run) return(infoBox("Stocks", "0", icon = icon("building")))
    
    n_stocks <- length(rv$optimized_portfolio$weights)
    infoBox(
      "Stocks in Portfolio",
      as.character(n_stocks),
      icon = icon("building"),
      color = "blue"
    )
  })
  
  # Render charts
  output$allocationChart <- renderPlotly({
    if (!rv$analysis_run) return(plot_ly())
    create_allocation_chart(rv$optimized_portfolio$weights)
  })
  
  output$riskReturnPlot <- renderPlotly({
    if (!rv$analysis_run) return(plot_ly())
    create_risk_return_plot(rv$data$returns, rv$optimized_portfolio$weights)
  })
  
  output$correlationHeatmap <- renderPlotly({
    if (!rv$analysis_run) return(plot_ly())
    create_correlation_heatmap(rv$data$returns)
  })
  
  # Optimization tables and charts
  output$weightsTable <- renderDataTable({
    if (!rv$analysis_run) return(data.frame())
    
    df <- data.frame(
      Stock = names(rv$optimized_portfolio$weights),
      Weight = rv$optimized_portfolio$weights,
      Sector = sapply(names(rv$optimized_portfolio$weights), function(t) SECTOR_MAP[[t]]),
      stringsAsFactors = FALSE
    )
    
    df$Weight_Pct <- sprintf("%.2f%%", df$Weight * 100)
    df <- df[, c("Stock", "Sector", "Weight_Pct")]
    colnames(df) <- c("Stock", "Sector", "Allocation")
    
    datatable(df, options = list(pageLength = 10))
  })
  
  output$strategyComparison <- renderPlotly({
    if (!rv$analysis_run) return(plot_ly())
    
    # Compare different strategies
    strategies <- c("max_sharpe", "min_volatility", "risk_parity")
    results <- lapply(strategies, function(s) {
      w <- optimize_portfolio(rv$data$returns, strategy = s)
      m <- calculate_portfolio_metrics(w, rv$data$returns)
      c(Strategy = s, Return = m["Expected_Return"], Volatility = m["Volatility"])
    })
    
    df <- do.call(rbind, results)
    df <- as.data.frame(df, stringsAsFactors = FALSE)
    df$Return <- as.numeric(df$Return)
    df$Volatility <- as.numeric(df$Volatility)
    
    plot_ly(
      data = df,
      x = ~Volatility,
      y = ~Return,
      text = ~Strategy,
      mode = 'markers+text',
      marker = list(size = 15, color = c('#1f77b4', '#ff7f0e', '#2ca02c')),
      textposition = 'top center'
    ) %>%
      layout(
        title = 'Strategy Comparison',
        xaxis = list(title = 'Volatility'),
        yaxis = list(title = 'Return')
      )
  })
  
  output$efficientFrontier <- renderPlotly({
    if (!rv$analysis_run) return(plot_ly())
    
    # Simplified efficient frontier
    n_points <- 50
    returns_mean <- colMeans(rv$data$returns) * 252
    cov_matrix <- cov(rv$data$returns)
    
    # Generate random portfolios
    set.seed(123)
    rand_portfolios <- replicate(n_points, {
      w <- runif(ncol(rv$data$returns))
      w <- w / sum(w)
      ret <- sum(w * returns_mean)
      vol <- sqrt(t(w) %*% cov_matrix %*% w)
      c(vol, ret)
    })
    
    plot_ly() %>%
      add_trace(
        x = rand_portfolios[1, ],
        y = rand_portfolios[2, ],
        mode = 'markers',
        type = 'scatter',
        marker = list(size = 5, color = 'rgba(31, 119, 180, 0.3)'),
        name = 'Random Portfolios'
      ) %>%
      add_trace(
        x = rv$optimized_portfolio$metrics["Volatility"],
        y = rv$optimized_portfolio$metrics["Expected_Return"],
        mode = 'markers',
        type = 'scatter',
        marker = list(size = 15, color = 'red', symbol = 'star'),
        name = 'Optimal Portfolio'
      ) %>%
      layout(
        title = 'Efficient Frontier',
        xaxis = list(title = 'Volatility'),
        yaxis = list(title = 'Return')
      )
  })
  
  # Forecast plots
  output$priceForecast <- renderPlotly({
    if (!rv$analysis_run || is.null(input$forecastStock)) return(plot_ly())
    
    fc_data <- rv$forecasts[[which(sapply(rv$forecasts, function(f) f$ticker == input$forecastStock))]]
    
    if (is.null(fc_data)) return(plot_ly())
    
    prices <- rv$data$prices[, input$forecastStock]
    create_forecast_plot(prices, fc_data$forecast, input$forecastStock)
  })
  
  output$forecastStats <- renderText({
    if (!rv$analysis_run || is.null(input$forecastStock)) return("No forecast available")
    
    fc_data <- rv$forecasts[[which(sapply(rv$forecasts, function(f) f$ticker == input$forecastStock))]]
    
    if (is.null(fc_data)) return("No forecast available")
    
    fc <- fc_data$forecast
    last_price <- fc$last_price
    last_fc <- tail(fc$mean, 1)
    expected_return <- (last_fc - last_price) / last_price
    
    sprintf(
      "Current Price: IDR %,.0f\n
Forecast Horizon: %d days\n
Expected Price: IDR %,.0f\n
Expected Return: %.2f%%\n
Confidence Interval:\n  Lower: IDR %,.0f\n  Upper: IDR %,.0f",
      last_price,
      input$forecastHorizon,
      last_fc,
      expected_return * 100,
      tail(fc$lower, 1),
      tail(fc$upper, 1)
    )
  })
  
  output$volatilityForecast <- renderPlotly({
    if (!rv$analysis_run || is.null(input$forecastStock)) return(plot_ly())
    
    # Get GARCH forecast
    ticker <- input$forecastStock
    returns <- rv$data$returns[, ticker]
    garch_fc <- forecast_garch(returns, input$forecastHorizon)
    
    if (is.null(garch_fc)) return(plot_ly())
    
    df <- data.frame(
      Day = 1:input$forecastHorizon,
      Volatility = as.numeric(garch_fc$volatility) * 100
    )
    
    plot_ly(
      data = df,
      x = ~Day,
      y = ~Volatility,
      type = 'scatter',
      mode = 'lines+markers',
      line = list(color = '#ff7f0e', width = 3)
    ) %>%
      layout(
        title = sprintf('%s - Volatility Forecast (GARCH)', ticker),
        xaxis = list(title = 'Days Ahead'),
        yaxis = list(title = 'Daily Volatility (%)')
      )
  })
  
  # Recommendations
  output$recommendationCards <- renderUI({
    if (!rv$analysis_run) return(p("Run analysis to see recommendations"))
    
    cards <- lapply(rv$recommendations, function(rec) {
      card_class <- switch(rec$signal,
        "BUY" = "rec-buy",
        "AVOID" = "rec-avoid",
        "HOLD" = "rec-hold"
      )
      
      div(
        class = paste("rec-card", card_class),
        fluidRow(
          column(
            width = 2,
            h3(icon(if(rec$signal == "BUY") "check-circle" else if(rec$signal == "AVOID") "times-circle" else "pause-circle")),
            strong(rec$signal)
          ),
          column(
            width = 3,
            h4(rec$ticker),
            p(class = "text-muted", rec$sector)
          ),
          column(
            width = 3,
            p(strong("Expected Return:"), sprintf("%.2f%%", rec$expected_return * 100)),
            p(strong("Confidence:"), sprintf("%.0f%%", rec$confidence * 100))
          ),
          column(
            width = 4,
            p(style = "font-size: 12px;", rec$rationale)
          )
        )
      )
    })
    
    do.call(tagList, cards)
  })
  
  output$recommendationTable <- renderDataTable({
    if (!rv$analysis_run) return(data.frame())
    
    df <- do.call(rbind, lapply(rv$recommendations, function(rec) {
      data.frame(
        Stock = rec$ticker,
        Sector = rec$sector,
        Signal = rec$signal,
        Expected_Return = sprintf("%.2f%%", rec$expected_return * 100),
        Confidence = sprintf("%.0f%%", rec$confidence * 100),
        stringsAsFactors = FALSE
      )
    }))
    
    # Color code signals
    df$Signal_Color <- sapply(df$Signal, function(s) {
      if(s == "BUY") return("color: green; font-weight: bold;")
      if(s == "AVOID") return("color: red; font-weight: bold;")
      return("color: orange; font-weight: bold;")
    })
    
    datatable(df[, 1:5], options = list(
      pageLength = 15,
      rowCallback = JS('function(row, data) {
        $("td:eq(2)", row).css("cssText", data[6]);
      }')
    ))
  })
}

# ================================================================================
# RUN APPLICATION
# ================================================================================

shinyApp(ui = ui, server = server)
