# ESG vs Non-ESG Stock Performance Analysis

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
| 5 Years | 163.11% | 186.61% | -23.50% |
| 3 Years | 108.00% | 42.12% | +65.88% |
| 1 Year | 17.15% | 66.18% | -49.02% |

## Visualizations

### Performance Comparison Chart
![ESG vs Non-ESG Performance](esg_vs_non_esg_performance.svg)

### Interactive Chart
For an interactive version with hover details, view: [esg_vs_non_esg_performance.html](esg_vs_non_esg_performance.html)

## Key Insights

1. **5-Year Performance**: ESG companies showed an average return of 163.11% compared to 186.61% for non-ESG companies.

2. **3-Year Performance**: ESG companies averaged 108.00% vs 42.12% for non-ESG.

3. **1-Year Performance**: ESG companies returned 17.15% on average, while non-ESG companies returned 66.18%.

## Methodology

- **Data Source**: Yahoo Finance (yfinance library)
- **ESG Selection**: Companies with consistently high ESG ratings from major rating agencies
- **Non-ESG Selection**: Traditional energy/oil & gas companies with lower ESG scores
- **Returns Calculated**: Total price return (not including dividends)
- **Analysis Date**: 2026-04-14

## Disclaimer
⚠️ **Past performance does not guarantee future results.** This analysis is for informational and educational purposes only and should not be considered as investment advice. Always conduct your own research before making investment decisions.

## Files Generated

- `esg_vs_non_esg_performance.svg` - Static visualization (GitHub-compatible)
- `esg_vs_non_esg_performance.html` - Interactive visualization with Plotly
- `esg_analysis.py` - Python script used to generate this analysis

---
*Generated on 2026-04-14 19:50:09*
