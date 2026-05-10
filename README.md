# 📊 Data Mining & Visualization Projects Repository

A collection of data mining, analysis, and visualization projects including Jupyter notebooks for practical data mining, Google Sheets integration, wordcloud generation, and an interactive MDB (Multilateral Development Bank) dashboard.

---

## 📁 Repository Structure

```
/workspace
├── README.md                              # Main repository documentation
├── README_MDB_Dashboard.md                # Detailed MDB Dashboard documentation
├── app.py                                 # Streamlit web application for MDB Dashboard
├── requirements.txt                       # Python dependencies
├── .gitignore                             # Git ignore configuration
├── Google Sheet/                          # Google Sheets integration notebooks
│   ├── Connect Google Sheet with Pandas.ipynb
│   ├── Read Google Sheet Using Gspread.ipynb
│   └── Read Google Sheet.ipynb
├── Bernardia Vitri - Big Data C - Default of Credit Card Clients Datasets Mining.ipynb
├── Black Friday Practical Data Mining.ipynb
└── Wordcloud maret 2017.ipynb
```

---

## 📋 File Descriptions

### Core Application Files

| File | Description |
|------|-------------|
| **`app.py`** | Main Streamlit application for the MDB Project & Loan Portfolio Monitor dashboard. Contains synthetic data generation, interactive visualizations using Plotly, and multiple dashboard sections including executive summary, project pipeline, financial analytics, risk & compliance, and data quality reconciliation. |
| **`requirements.txt`** | Python package dependencies required to run the applications. Includes: `streamlit`, `pandas`, `plotly`, and `numpy`. |
| **`.gitignore`** | Git configuration file specifying which files and directories should be ignored by version control. |

### Documentation Files

| File | Description |
|------|-------------|
| **`README.md`** | This file - main repository overview and guide. |
| **`README_MDB_Dashboard.md`** | Comprehensive documentation for the MDB Dashboard, including installation instructions, feature descriptions, dashboard sections, technical highlights, and usage guidelines. |

### Jupyter Notebooks

#### Data Mining Projects

| Notebook | Description |
|----------|-------------|
| **`Black Friday Practical Data Mining.ipynb`** | Practical data mining analysis on Black Friday sales dataset. Explores customer behavior, purchase patterns, demographic analysis, and predictive modeling techniques for retail analytics. |
| **`Bernardia Vitri - Big Data C - Default of Credit Card Clients Datasets Mining.ipynb`** | Credit card default prediction analysis using big data mining techniques. Analyzes client demographics, payment history, credit utilization, and builds classification models to predict default risk. |

#### Google Sheets Integration

| Notebook | Description |
|----------|-------------|
| **`Google Sheet/Read Google Sheet.ipynb`** | Basic tutorial on reading data from Google Sheets into Python using various methods and libraries. |
| **`Google Sheet/Read Google Sheet Using Gspread.ipynb`** | Demonstrates how to connect to and read Google Sheets using the `gspread` library, including authentication setup and data retrieval techniques. |
| **`Google Sheet/Connect Google Sheet with Pandas.ipynb`** | Shows how to integrate Google Sheets with Pandas DataFrames for seamless data analysis, manipulation, and visualization workflows. |

#### Text Visualization

| Notebook | Description |
|----------|-------------|
| **`Wordcloud maret 2017.ipynb`** | Word cloud generation project for text visualization. Creates visual representations of word frequency and text patterns from March 2017 data. |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Jupyter Notebook (for running notebooks)

### Installation

1. **Clone or navigate to the repository**:
   ```bash
   cd /workspace
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional packages for notebooks** (if needed):
   ```bash
   pip install jupyter gspread oauth2client wordcloud matplotlib seaborn scikit-learn
   ```

### Running the Applications

#### MDB Dashboard
```bash
streamlit run app.py
```
Then open your browser to `http://localhost:8501`

#### Jupyter Notebooks
```bash
jupyter notebook
```
Then navigate to any `.ipynb` file to explore the analyses.

---

## 🎯 Project Categories

### 1. **Dashboard & Web Applications**
- Interactive Streamlit dashboard for financial portfolio monitoring
- Real-time data visualization with Plotly
- Multi-section analytics interface

### 2. **Data Mining & Analysis**
- Credit risk assessment and default prediction
- Retail consumer behavior analysis
- Classification and predictive modeling

### 3. **Data Integration**
- Google Sheets API integration
- Cloud-based data access patterns
- Pandas DataFrame workflows

### 4. **Text Visualization**
- Word cloud generation
- Text frequency analysis
- Visual text analytics

---

## 📦 Dependencies

Core dependencies (from `requirements.txt`):
- **streamlit** - Web application framework
- **pandas** - Data manipulation and analysis
- **plotly** - Interactive visualizations
- **numpy** - Numerical computing

Additional dependencies for notebooks:
- **jupyter** - Interactive notebook environment
- **gspread** - Google Sheets API client
- **wordcloud** - Word cloud generation
- **matplotlib/seaborn** - Static visualizations
- **scikit-learn** - Machine learning algorithms

---

## 💡 Use Cases

This repository demonstrates:

1. **Financial Analytics**: Monitor loan portfolios, track disbursements, and assess risk
2. **Predictive Modeling**: Build classification models for credit default and customer behavior
3. **Data Integration**: Connect cloud-based spreadsheets with Python analysis tools
4. **Interactive Dashboards**: Create professional web-based data visualization applications
5. **Text Mining**: Generate visual representations of textual data patterns

---

## 🛠️ Technologies Used

- **Python 3.8+**
- **Streamlit** - Dashboard framework
- **Plotly** - Interactive charts and maps
- **Pandas** - Data manipulation
- **Jupyter Notebooks** - Exploratory data analysis
- **Google Sheets API** - Cloud data integration
- **Scikit-learn** - Machine learning (notebooks)

---

## 📄 License

This repository contains demonstration and educational projects. Individual notebooks may have their own licensing terms.

---

## 📞 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Library](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [GSpread Documentation](https://gspread.readthedocs.io/)
- [Jupyter Notebook Guide](https://jupyter-notebook.readthedocs.io/)

---

## ⚠️ Notes

- The MDB Dashboard uses **synthetic data** for demonstration purposes only
- Google Sheets notebooks require proper API credentials and authentication
- Some notebooks may require specific datasets not included in this repository

---

**Last Updated**: 2024
