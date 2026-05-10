# 🏦 MDB Project & Loan Portfolio Monitor

## AIIB Demonstration Dashboard

A comprehensive Streamlit-based dashboard for monitoring Multilateral Development Bank (MDB) projects and loan portfolios, specifically designed as a demonstration for the Asian Infrastructure Investment Bank (AIIB).

![Dashboard](https://img.shields.io/badge/Status-Demonstration-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red)
![Visualization](https://img.shields.io/badge/Viz-Plotly-green)
![Data](https://img.shields.io/badge/Data-Synthetic-orange)

---

## 📋 Overview

The **MDB Project & Loan Portfolio Monitor** is an interactive web application that provides real-time visualization and analysis of development bank project portfolios. This demonstration showcases key metrics, risk assessments, financial tracking, and data quality reconciliation for infrastructure investment projects across multiple countries.

### Key Features

- **🌍 Geographic Distribution**: Visualize project allocation across Asia-Pacific countries
- **🏗️ Sector Analysis**: Track investments in Energy, Transport, Water, and Digital Infrastructure
- **💰 Financial Monitoring**: Monitor loan disbursements, commitments, and utilization rates
- **⚠️ Risk Assessment**: Evaluate portfolio risk ratings and compliance metrics
- **📊 Interactive Dashboards**: Dynamic charts and filters for deep-dive analysis
- **✅ Data Quality Reconciliation**: Track and resolve data discrepancies
- **📖 Terminology Reference**: Comprehensive loan terminology glossary

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd /workspace
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

4. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:8501`

---

## 📦 Dependencies

The application requires the following Python packages:

```txt
streamlit
pandas
plotly
numpy
```

All dependencies are listed in `requirements.txt`.

---

## 🎨 Dashboard Sections

### 1. Executive Summary
High-level overview of the entire portfolio including:
- Total project count and financial metrics
- Geographic and sector distribution maps
- Key performance indicators (KPIs)

### 2. Project Pipeline
Detailed view of projects by status:
- Concept stage projects
- Appraisal phase
- Implementation tracking
- Completion status

### 3. Financial Analytics
Comprehensive financial analysis:
- Loan disbursement schedules
- Commitment vs. disbursement comparisons
- Fund utilization rates
- Financial projections

### 4. Risk & Compliance
Risk management dashboard:
- Portfolio risk ratings (AAA to D)
- Compliance metrics
- Environmental and social safeguards
- Risk mitigation strategies

### 5. Data Quality Reconciliation
Data integrity monitoring:
- Discrepancy tracking
- Resolution status
- Issue categorization
- Reconciliation logs

### 6. Loan Terminology Reference
Educational resource with definitions of:
- Sovereign and Non-Sovereign loans
- Tranche structures
- Covenants and conditions
- Disbursement mechanisms

---

## 🎯 Target Audience

- **MDB Executives**: Strategic portfolio oversight
- **Project Managers**: Operational tracking and reporting
- **Risk Officers**: Compliance and risk monitoring
- **Analysts**: Data-driven insights and trend analysis
- **Stakeholders**: Transparent project information access

---

## 💡 Technical Highlights

### Synthetic Data Generation
The dashboard uses realistically generated synthetic data representing:
- 25 infrastructure projects across 8 countries
- Multiple sectors: Energy, Transport, Water, Digital Infrastructure
- Various project stages from concept to completion
- Diverse risk ratings and loan types

### Interactive Visualizations
Built with Plotly for:
- Choropleth maps showing geographic distribution
- Sunburst diagrams for sector-country breakdowns
- Time-series charts for financial tracking
- Gauge charts for KPI monitoring
- Treemaps for portfolio composition

### Responsive Design
- Wide layout optimized for desktop viewing
- Custom CSS styling with professional color scheme
- Mobile-friendly responsive components

---

## 🏛️ Use Cases

This demonstration illustrates how AIIB and other MDBs can leverage modern data visualization tools to:

1. **Enhance Transparency**: Provide stakeholders with clear, accessible project information
2. **Improve Decision-Making**: Enable data-driven strategic planning
3. **Monitor Performance**: Track project progress and financial health in real-time
4. **Manage Risk**: Identify and address potential issues proactively
5. **Streamline Reporting**: Automate routine portfolio reports

---

## ⚠️ Disclaimer

**This dashboard is for demonstration purposes only.** All data displayed is synthetically generated and does not represent actual AIIB portfolio information, real projects, or genuine financial data. The application serves as a technical proof-of-concept for dashboard capabilities.

---

## 🛠️ Development

### File Structure
```
/workspace
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README_MDB_Dashboard.md  # This documentation file
└── .gitignore            # Git ignore rules
```

### Customization

To adapt this dashboard for specific use cases:

1. **Replace synthetic data**: Modify the `generate_synthetic_data()` function in `app.py`
2. **Connect to databases**: Integrate with actual MDB data sources
3. **Add authentication**: Implement user authentication for sensitive data
4. **Extend visualizations**: Add custom charts specific to your needs
5. **Automate updates**: Set up scheduled data refreshes

---

## 📞 Support

For questions about this demonstration dashboard or technical implementation details, please refer to the Streamlit and Plotly documentation:

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Library](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## 📄 License

This demonstration project is provided as-is for educational and illustrative purposes.

---

## 🙏 Acknowledgments

This dashboard was created as a demonstration for the Asian Infrastructure Investment Bank (AIIB) to showcase modern data visualization capabilities for Multilateral Development Bank operations.

**Built with ❤️ using Streamlit & Plotly**

---

*Last Updated: 2024*
