# requirements.txt:
# streamlit
# pandas
# plotly
# numpy

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Set page config
st.set_page_config(
    page_title="MDB Project & Loan Portfolio Monitor",
    page_icon="🏦",
    layout="wide"
)

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Color scheme
DARK_BLUE = "#1a3a5c"
GOLD = "#d4af37"
LIGHT_BLUE = "#2c5282"
WHITE = "#ffffff"

# Custom CSS for styling
st.markdown(f"""
<style>
    .main {{
        background-color: #f5f5f5;
    }}
    .stMetric {{
        background-color: {DARK_BLUE};
        padding: 15px;
        border-radius: 10px;
        color: {WHITE};
    }}
    .stMetric label {{
        color: {GOLD} !important;
    }}
    .stMetric div[data-testid="stMetricValue"] {{
        color: {WHITE} !important;
    }}
    h1, h2, h3 {{
        color: {DARK_BLUE};
    }}
    .card {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)


def generate_synthetic_data():
    """Generate all synthetic data for the dashboard."""
    
    # Define distributions
    countries = ["Indonesia"] * 6 + ["India"] * 5 + ["Bangladesh"] * 4 + \
                ["Pakistan"] * 3 + ["Vietnam"] * 3 + ["Philippines"] * 2 + \
                ["Thailand"] * 1 + ["Mongolia"] * 1
    
    sectors = ["Energy"] * 8 + ["Transport"] * 7 + ["Water"] * 5 + ["Digital Infrastructure"] * 5
    
    statuses = ["Concept"] * 5 + ["Appraisal"] * 5 + ["Implementation"] * 10 + ["Completion"] * 5
    
    loan_types = ["Sovereign"] * 15 + ["Non-Sovereign"] * 10
    
    risk_ratings = ["AAA"] * 2 + ["AA"] * 5 + ["A"] * 6 + ["BBB"] * 5 + \
                   ["BB"] * 3 + ["B"] * 1 + ["CCC"] * 2 + ["D"] * 1
    
    project_names = [
        "National Highway Expansion", "Renewable Energy Grid", "Urban Water Supply",
        "Digital Connectivity Initiative", "Port Modernization", "Solar Power Plant",
        "Rural Electrification", "Metro Rail System", "Wastewater Treatment",
        "Broadband Infrastructure", "Hydropower Development", "Airport Upgrade",
        "Irrigation Modernization", "Smart City Platform", "Wind Farm Project",
        "Railway Electrification", "Clean Water Access", "Data Center Network",
        "Gas Pipeline", "Bridge Construction", "Flood Control System",
        "Telecommunications Tower", "Geothermal Energy", "Expressway Development",
        "Sanitation Infrastructure"
    ]
    
    projects = []
    for i in range(25):
        project_id = f"PRJ-{2024+i:04d}"
        name = project_names[i]
        country = countries[i]
        sector = sectors[i]
        status = statuses[i]
        
        # Project cost between $50M and $2B
        total_cost = round(np.random.uniform(50, 2000), 1)
        
        # Loan amount is 40-80% of project cost
        loan_ratio = np.random.uniform(0.4, 0.8)
        loan_amount = round(total_cost * loan_ratio, 1)
        co_financing = round(total_cost - loan_amount, 1)
        
        # Approval date between 2018-2025
        approval_date = datetime(2018, 1, 1) + timedelta(days=np.random.randint(0, 2555))
        
        # Maturity date between 2025-2045 (10-25 years from approval)
        maturity_years = np.random.randint(10, 26)
        maturity_date = approval_date + timedelta(days=maturity_years * 365)
        
        # Disbursement ratio between 15-95%
        disbursement_ratio = np.random.uniform(0.15, 0.95)
        disbursed = round(loan_amount * disbursement_ratio, 1)
        outstanding = round(disbursed * np.random.uniform(0.5, 0.95), 1)
        
        # Interest rate between 2-8%
        interest_rate = round(np.random.uniform(2.0, 8.0), 2)
        
        # Covenant status - NPLs (CCC or D) should have breach
        loan_type = loan_types[i]
        risk_rating = risk_ratings[i]
        
        if risk_rating == "D":
            covenant_status = "Breach"
        elif risk_rating == "CCC":
            covenant_status = "Breach"
        elif risk_rating in ["B", "BB"]:
            covenant_status = np.random.choice(["Compliant", "Watch", "Watch"], p=[0.3, 0.4, 0.3])
        else:
            covenant_status = np.random.choice(["Compliant", "Watch"], p=[0.85, 0.15])
        
        # NPL flag (CCC or D ratings)
        is_npl = risk_rating in ["CCC", "D"]
        
        projects.append({
            "Project ID": project_id,
            "Project Name": name,
            "Country": country,
            "Sector": sector,
            "Status": status,
            "Total Cost ($M)": total_cost,
            "AIIB Loan Amount ($M)": loan_amount,
            "Co-financing ($M)": co_financing,
            "Approval Date": approval_date.strftime("%Y-%m-%d"),
            "Maturity Date": maturity_date.strftime("%Y-%m-%d"),
            "Loan Type": loan_type,
            "Commitment ($M)": loan_amount,
            "Disbursed ($M)": disbursed,
            "Outstanding ($M)": outstanding,
            "Interest Rate (%)": interest_rate,
            "Covenant Status": covenant_status,
            "Risk Rating": risk_rating,
            "Is NPL": is_npl,
            "Disbursement Ratio": round(disbursement_ratio * 100, 1)
        })
    
    return pd.DataFrame(projects)


def generate_disbursement_schedule(df):
    """Generate disbursement schedule data."""
    schedule_data = []
    
    for _, row in df.iterrows():
        project_id = row["Project ID"]
        project_name = row["Project Name"]
        commitment = row["Commitment ($M)"]
        disbursed = row["Disbursed ($M)"]
        
        # Generate 3-5 tranches per project
        num_tranches = np.random.randint(3, 6)
        remaining = commitment
        
        for t in range(num_tranches):
            tranche_id = f"{project_id}-T{t+1:02d}"
            
            if t < num_tranches - 1:
                tranche_amount = round(remaining / (num_tranches - t) * np.random.uniform(0.8, 1.2), 1)
            else:
                tranche_amount = round(remaining, 1)
            
            remaining -= tranche_amount
            
            # Tranche date
            base_date = datetime.strptime(row["Approval Date"], "%Y-%m-%d")
            tranche_date = base_date + timedelta(days=np.random.randint(30, 365 * 3))
            
            # Status based on whether it's been disbursed
            if tranche_date <= datetime.now() - timedelta(days=30):
                status = np.random.choice(["Disbursed", "Disbursed", "Delayed"], p=[0.7, 0.2, 0.1])
            elif tranche_date <= datetime.now():
                status = np.random.choice(["Pending", "On Time"], p=[0.6, 0.4])
            else:
                status = "Scheduled"
            
            schedule_data.append({
                "Tranche ID": tranche_id,
                "Project ID": project_id,
                "Project Name": project_name,
                "Tranche Amount ($M)": tranche_amount,
                "Scheduled Date": tranche_date.strftime("%Y-%m-%d"),
                "Status": status
            })
    
    return pd.DataFrame(schedule_data)


def generate_data_quality_issues(df):
    """Generate simulated data quality issues."""
    issues = [
        {
            "Issue ID": "DQ-001",
            "Project/Loan Affected": df.iloc[3]["Project ID"],
            "Issue Description": "Project total cost does not match sum of cost categories (variance: $12.5M)",
            "Severity": "Medium",
            "Suggested Remediation": "Review cost breakdown structure and reconcile with financial statements"
        },
        {
            "Issue ID": "DQ-002",
            "Project/Loan Affected": df.iloc[7]["Project ID"],
            "Issue Description": "Loan commitment amount exceeds project total cost by $45M",
            "Severity": "High",
            "Suggested Remediation": "Verify loan agreement terms and update project cost estimates"
        },
        {
            "Issue ID": "DQ-003",
            "Project/Loan Affected": "Multiple (3 loans)",
            "Issue Description": "Missing covenant data for 3 loans in portfolio",
            "Severity": "Medium",
            "Suggested Remediation": "Request updated covenant compliance reports from borrowers"
        },
        {
            "Issue ID": "DQ-004",
            "Project/Loan Affected": df.iloc[15]["Project ID"],
            "Issue Description": "Duplicate project entry detected with matching name and country",
            "Severity": "High",
            "Suggested Remediation": "Merge duplicate records and archive redundant entry"
        },
        {
            "Issue ID": "DQ-005",
            "Project/Loan Affected": df.iloc[21]["Project ID"],
            "Issue Description": "Disbursement amount exceeds remaining loan balance by $8.2M",
            "Severity": "High",
            "Suggested Remediation": "Investigate disbursement records and correct accounting entries"
        },
        {
            "Issue ID": "DQ-006",
            "Project/Loan Affected": df.iloc[10]["Project ID"],
            "Issue Description": "Maturity date precedes approval date (data entry error)",
            "Severity": "Low",
            "Suggested Remediation": "Correct maturity date based on loan agreement terms"
        }
    ]
    return pd.DataFrame(issues)


def calculate_data_completeness(df):
    """Calculate data completeness score per project."""
    required_fields = [
        "Project ID", "Project Name", "Country", "Sector", "Status",
        "Total Cost ($M)", "AIIB Loan Amount ($M)", "Commitment ($M)",
        "Disbursed ($M)", "Outstanding ($M)", "Interest Rate (%)",
        "Covenant Status", "Risk Rating", "Approval Date", "Maturity Date"
    ]
    
    completeness_scores = []
    for _, row in df.iterrows():
        populated = sum([1 for field in required_fields if pd.notna(row.get(field, None)) and row.get(field, None) != ""])
        score = round((populated / len(required_fields)) * 100, 1)
        completeness_scores.append({
            "Project ID": row["Project ID"],
            "Project Name": row["Project Name"],
            "Completeness Score (%)": score
        })
    
    return pd.DataFrame(completeness_scores)


def render_terminology_reference():
    """Render the loan terminology reference section."""
    st.header("📚 Loan Terminology Reference")
    st.markdown("*Quick reference guide for key terms used in MDB lending operations*")
    
    # Loan Types
    with st.expander("📋 Loan Types", expanded=False):
        st.markdown("""
        **Sovereign Loan**
        > Loan to a national government, backed by the sovereign guarantee of that country.
        > These loans carry the credit risk of the borrowing nation and typically require
        > parliamentary approval. They are used for public infrastructure and policy reforms.
        
        **Non-Sovereign Loan**
        > Loan to a sub-national entity, state-owned enterprise, or private company without
        > a central government guarantee. Credit assessment focuses on the borrower's own
        > cash flows and collateral. Common for utilities, ports, and commercial projects.
        """)
    
    # Loan Lifecycle / Disbursement
    with st.expander("🔄 Loan Lifecycle & Disbursement", expanded=False):
        st.markdown("""
        **Commitment**
        > The total amount the lender has formally agreed to lend under a signed loan agreement.
        > This is a legal obligation but funds are not transferred immediately. Commitments
        > appear on the lender's balance sheet as contingent liabilities until disbursed.
        
        **Disbursement**
        > The actual transfer of funds from lender to borrower. Can happen in multiple tranches
        > over time as project milestones are met. Disbursements reduce the undrawn commitment
        > and create the loan asset on the lender's books.
        
        **Outstanding Balance**
        > The portion of the loan that has been disbursed but not yet repaid.
        > Formula: `Outstanding = Cumulative Disbursed - Cumulative Repaid`
        > This represents the current exposure to the borrower.
        
        **Disbursement Ratio**
        > Disbursed Amount / Commitment Amount. Measures how much of the approved loan has
        > actually been drawn down. Low ratios (<50%) may indicate project implementation
        > delays, procurement bottlenecks, or changing borrower needs.
        
        **Tranche**
        > A portion or slice of a loan commitment, disbursed when specific conditions or
        > milestones are met. Tranching allows phased funding aligned with project progress
        > and reduces the lender's exposure during early implementation phases.
        """)
    
    # Loan Performance & Risk
    with st.expander("⚠️ Loan Performance & Risk", expanded=False):
        st.markdown("""
        **Covenant**
        > A condition or promise in a loan agreement that the borrower must fulfill.
        > Examples: maintain certain financial ratios (debt-to-equity < 2x), not take on
        > excessive additional debt, submit quarterly financial statements, maintain
        > insurance coverage. Covenants protect lenders by enabling early intervention.
        
        **Covenant Status**
        > - **Compliant**: Borrower is meeting all covenant conditions. Normal monitoring applies.
        > - **Watch**: Borrower shows early warning signs (e.g., approaching covenant thresholds);
        >   requires closer monitoring and possibly remedial action plans.
        > - **Breach**: Borrower has violated one or more covenant conditions; may trigger
        >   remediation requirements, penalty fees, or loan recall proceedings.
        
        **Non-Performing Loan (NPL)**
        > A loan where the borrower has failed to make scheduled payments for a specified
        > period (typically 90+ days past due). NPLs require increased provisioning and
        > intensive workout efforts. A rising NPL ratio signals deteriorating portfolio quality.
        
        **NPL Ratio**
        > `(Total NPL Outstanding) / (Total Loan Portfolio Outstanding) × 100`
        > Key indicator of portfolio health. MDBs typically target NPL ratios below 2%.
        > Ratios above 5% indicate significant credit quality deterioration.
        
        **Risk Rating**
        > An internal credit score assigned to each loan, reflecting probability of default.
        > Scale: AAA (lowest risk), AA, A, BBB, BB, B, CCC, CC, D (in default).
        > Investment grade: BBB- and above. Below investment grade (BB+) indicates
        > speculative/high-yield credit with elevated default risk.
        
        **Value at Risk (VaR)**
        > The maximum potential loss on a portfolio over a given time period at a specified
        > confidence level. Example: 95% daily VaR of $10M means there is a 5% chance of
        > losing more than $10M in a single day. VaR is widely used for market risk measurement.
        
        **Conditional VaR (CVaR / Expected Shortfall)**
        > The average loss in the worst-case scenarios beyond the VaR threshold.
        > More conservative than VaR because it captures tail risk. Also called
        > Expected Shortfall (ES). If 95% VaR is $10M and CVaR is $15M, the average
        > loss in the worst 5% of cases is $15M.
        """)
    
    # Portfolio Management
    with st.expander("📊 Portfolio Management", expanded=False):
        st.markdown("""
        **Portfolio Concentration**
        > The degree to which a loan portfolio is exposed to a single borrower, sector, or country.
        > High concentration increases risk—if that borrower/sector/country experiences distress,
        > a large portion of the portfolio is affected. Limits are typically set (e.g., no single
        > borrower > 15% of portfolio, no single sector > 30%).
        
        **Maturity Profile**
        > The schedule of when loans are due for repayment. A "maturity wall" occurs when many
        > loans mature at the same time, creating refinancing risk for borrowers and potential
        > liquidity strain. Lenders monitor maturity profiles to ensure balanced cash inflows.
        
        **Currency Exposure**
        > Risk arising from loans denominated in currencies different from the borrower's revenue
        > currency. If a borrower earns local currency but owes USD, currency depreciation can
        > make repayment more expensive in local currency terms, increasing default risk.
        
        **Co-financing**
        > When multiple lenders (e.g., AIIB + ADB + World Bank) jointly fund a project.
        > Benefits: reduces individual lender exposure, shares due diligence burden, leverages
        > complementary expertise, and demonstrates broad donor support for the project.
        """)


def main():
    # Header
    st.title("🏦 MDB Project & Loan Portfolio Monitor")
    st.markdown("**AIIB Demonstration Dashboard** | *Multilateral Development Bank Portfolio Analytics*")
    st.markdown("---")
    
    # Generate all data
    df = generate_synthetic_data()
    schedule_df = generate_disbursement_schedule(df)
    dq_issues = generate_data_quality_issues(df)
    completeness_df = calculate_data_completeness(df)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📁 Project Overview",
        "💰 Loan Portfolio",
        "📅 Disbursement Monitoring",
        "⚠️ Portfolio Risk",
        "🔍 Data Quality & Reconciliation",
        "📚 Loan Terminology Reference"
    ])
    
    # ==================== TAB 1: PROJECT OVERVIEW ====================
    with tab1:
        st.header("Project Overview")
        st.markdown("Dashboard showing portfolio summary and project-level details across all active operations.")
        
        # KPI Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_portfolio = df["Total Cost ($M)"].sum()
        num_projects = len(df[df["Status"].isin(["Implementation", "Completion"])])
        total_committed = df["Commitment ($M)"].sum()
        total_disbursed = df["Disbursed ($M)"].sum()
        overall_disbursement_ratio = round((total_disbursed / total_committed) * 100, 1)
        
        with col1:
            st.metric(
                label="Total Portfolio Value ($M)",
                value=f"${total_portfolio:,.1f}",
                help="Sum of total project costs across all projects in the portfolio. Includes both AIIB financing and co-financing from other development partners."
            )
        with col2:
            st.metric(
                label="Active Projects",
                value=num_projects,
                help="Number of projects currently in Implementation or Completion status. Concept and Appraisal stage projects are not yet active."
            )
        with col3:
            st.metric(
                label="Total Committed ($M)",
                value=f"${total_committed:,.1f}",
                help="Total amount AIIB has formally committed to lend under signed loan agreements. Represents legal obligation to provide funding."
            )
        with col4:
            st.metric(
                label="Total Disbursed ($M)",
                value=f"${total_disbursed:,.1f}",
                help="Cumulative amount actually transferred to borrowers. Disbursements occur in tranches as project milestones are achieved."
            )
        with col5:
            st.metric(
                label="Overall Disbursement Ratio",
                value=f"{overall_disbursement_ratio}%",
                delta=f"{overall_disbursement_ratio - 50:.1f}% vs 50% benchmark",
                help="Disbursed Amount / Commitment Amount. Ratios below 50% may indicate project implementation delays. Target is 60-80% for mature portfolios."
            )
        
        st.markdown("---")
        
        # Filters and Charts
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            sector_filter = st.multiselect(
                "Filter by Sector",
                options=df["Sector"].unique(),
                default=df["Sector"].unique()
            )
        
        with filter_col2:
            country_filter = st.multiselect(
                "Filter by Country",
                options=df["Country"].unique(),
                default=df["Country"].unique()
            )
        
        with filter_col3:
            status_filter = st.multiselect(
                "Filter by Status",
                options=df["Status"].unique(),
                default=df["Status"].unique()
            )
        
        # Apply filters
        filtered_df = df[
            (df["Sector"].isin(sector_filter)) &
            (df["Country"].isin(country_filter)) &
            (df["Status"].isin(status_filter))
        ]
        
        # Charts row
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Sector Distribution")
            sector_pie = px.pie(
                filtered_df,
                names="Sector",
                values="Total Cost ($M)",
                title="Portfolio by Sector (Total Cost $M)",
                color_discrete_sequence=px.colors.sequential.Blues,
                hover_data=["Project ID"]
            )
            sector_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Total Cost: $%{value:.1f}M<br>Projects: %{customdata}<extra></extra>"
            )
            sector_pie.add_annotation(
                text="Energy and Transport dominate portfolio allocation",
                showarrow=False,
                y=1.1
            )
            st.plotly_chart(sector_pie, use_container_width=True)
            st.caption("💡 **Tip:** Hover over segments to see project count. Investment grade sectors typically have higher allocations.")
        
        with chart_col2:
            st.subheader("Portfolio by Country")
            country_bar = px.bar(
                filtered_df.groupby("Country")["Total Cost ($M)"].sum().reset_index(),
                x="Country",
                y="Total Cost ($M)",
                title="Portfolio Exposure by Country ($M)",
                color="Total Cost ($M)",
                color_continuous_scale=px.colors.sequential.YlOrBr
            )
            country_bar.update_layout(
                yaxis_title="Total Cost ($M)",
                xaxis_title="Country"
            )
            country_bar.add_annotation(
                text="High country concentration increases portfolio risk. Monitor exposure limits.",
                showarrow=False,
                y=1.1
            )
            st.plotly_chart(country_bar, use_container_width=True)
            st.caption("💡 **Note:** Country limits typically set at 20-25% of total portfolio to manage sovereign risk concentration.")
        
        st.markdown("---")
        
        # Project Table
        st.subheader("Project Details")
        st.caption("Complete list of projects with key metrics. Use filters above to narrow results.")
        
        display_cols = [
            "Project ID", "Project Name", "Country", "Sector", "Status",
            "Total Cost ($M)", "AIIB Loan Amount ($M)", "Co-financing ($M)"
        ]
        
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            hide_index=True
        )
    
    # ==================== TAB 2: LOAN PORTFOLIO ====================
    with tab2:
        st.header("Loan Portfolio")
        st.markdown("Detailed view of loan book including credit quality, covenant status, and risk metrics.")
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_commitments = df["Commitment ($M)"].sum()
        total_outstanding = df["Outstanding ($M)"].sum()
        npl_loans = df[df["Is NPL"]]["Outstanding ($M)"].sum()
        npl_ratio = round((npl_loans / total_outstanding) * 100, 2) if total_outstanding > 0 else 0
        
        # Calculate simple VaR (parametric approach)
        portfolio_returns = np.random.normal(0.05, 0.15, 10000)
        var_95 = np.percentile(portfolio_returns, 5) * total_outstanding
        var_95_abs = abs(var_95)
        
        with col1:
            st.metric(
                label="Total Loan Commitments ($M)",
                value=f"${total_commitments:,.1f}",
                help="Sum of all committed loan amounts. Represents AIIB's total exposure if all commitments were fully drawn."
            )
        with col2:
            st.metric(
                label="Total Outstanding ($M)",
                value=f"${total_outstanding:,.1f}",
                help="Current outstanding balance across all loans (disbursed minus repaid). This is the actual credit exposure."
            )
        with col3:
            st.metric(
                label="NPL Ratio",
                value=f"{npl_ratio}%",
                delta=f"{npl_ratio - 2:.2f}% vs 2% target",
                help="Non-Performing Loan Ratio = (NPL Outstanding / Total Portfolio Outstanding) × 100. NPL = 90+ days past due. Target <2%, concern >5%."
            )
        with col4:
            st.metric(
                label="Portfolio VaR (95%)",
                value=f"${var_95_abs:,.1f}M",
                help="Value at Risk at 95% confidence level. Maximum expected loss over 1-year horizon with 95% confidence. 5% chance of exceeding this loss."
            )
        
        st.markdown("---")
        
        # Loan Book Table
        st.subheader("Loan Book Details")
        st.caption("Individual loan information including type, terms, and credit quality indicators.")
        
        loan_cols = [
            "Loan ID", "Project", "Type", "Commitment ($M)", "Disbursed ($M)",
            "Outstanding ($M)", "Rate (%)", "Maturity", "Covenant Status", "Risk Rating"
        ]
        
        loan_df = df.copy()
        loan_df["Loan ID"] = loan_df["Project ID"].apply(lambda x: x.replace("PRJ", "LN"))
        loan_df["Project"] = loan_df["Project Name"]
        loan_df["Type"] = loan_df["Loan Type"]
        loan_df["Rate (%)"] = loan_df["Interest Rate (%)"]
        loan_df["Maturity"] = loan_df["Maturity Date"]
        
        st.dataframe(
            loan_df[loan_cols],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Portfolio Concentration")
            
            # By Country
            country_conc = df.groupby("Country")["Outstanding ($M)"].sum().reset_index()
            country_conc["% of Portfolio"] = round(
                (country_conc["Outstanding ($M)"] / country_conc["Outstanding ($M)"].sum()) * 100, 1
            )
            
            conc_fig = go.Figure()
            conc_fig.add_trace(go.Bar(
                x=country_conc["Country"],
                y=country_conc["% of Portfolio"],
                name="By Country",
                marker_color=DARK_BLUE,
                hovertemplate="<b>%{x}</b><br>Exposure: %{y:.1f}%<extra></extra>"
            ))
            
            # Add concentration limit line
            conc_fig.add_hline(
                y=25, line_dash="dash", line_color="red",
                annotation_text="25% Limit", annotation_position="top"
            )
            
            conc_fig.update_layout(
                title="Portfolio Concentration by Country (%)",
                yaxis_title="% of Total Portfolio",
                xaxis_title="Country",
                showlegend=False
            )
            
            st.plotly_chart(conc_fig, use_container_width=True)
            st.caption("⚠️ **Risk Indicator:** Concentration above 25% in any single country exceeds typical risk limits. Diversification reduces sovereign risk.")
        
        with chart_col2:
            st.subheader("Risk Rating Distribution")
            
            rating_order = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "D"]
            rating_counts = df["Risk Rating"].value_counts().reindex(rating_order).fillna(0)
            
            rating_fig = go.Figure()
            rating_fig.add_trace(go.Bar(
                x=rating_counts.index,
                y=rating_counts.values,
                marker_color=[
                    "#006400" if r in ["AAA", "AA", "A"] else
                    "#228B22" if r == "BBB" else
                    "#FFA500" if r in ["BB", "B"] else
                    "#FF4500" if r == "CCC" else
                    "#8B0000"
                    for r in rating_counts.index
                ],
                hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
            ))
            
            # Add investment grade cutoff line
            rating_fig.add_vline(
                x=3.5, line_dash="dash", line_color="gold", line_width=2,
                annotation_text="Investment Grade Cutoff (BBB-/BB+)", 
                annotation_position="top"
            )
            
            rating_fig.update_layout(
                title="Portfolio by Risk Rating",
                yaxis_title="Number of Loans",
                xaxis_title="Risk Rating",
                showlegend=False
            )
            
            st.plotly_chart(rating_fig, use_container_width=True)
            st.caption("📊 **Note:** Investment grade loans are BBB- and above (green/orange left). High concentrations in BB or below (orange/red right) indicate elevated credit risk requiring enhanced monitoring.")
    
    # ==================== TAB 3: DISBURSEMENT MONITORING ====================
    with tab3:
        st.header("Disbursement Monitoring")
        st.markdown("Track disbursement schedules, identify delays, and monitor fund utilization rates.")
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_scheduled = len(schedule_df)
        disbursed_count = len(schedule_df[schedule_df["Status"] == "Disbursed"])
        delayed_count = len(schedule_df[schedule_df["Status"] == "Delayed"])
        pending_count = len(schedule_df[schedule_df["Status"].isin(["Pending", "Scheduled"])])
        
        on_time_rate = round((disbursed_count / (disbursed_count + delayed_count)) * 100, 1) if (disbursed_count + delayed_count) > 0 else 100
        
        with col1:
            st.metric(
                label="Total Tranches",
                value=total_scheduled,
                help="Total number of disbursement tranches across all projects. Each loan typically has 3-5 tranches tied to milestones."
            )
        with col2:
            st.metric(
                label="Disbursed",
                value=disbursed_count,
                help="Number of tranches that have been fully disbursed to borrowers. Represents completed funding events."
            )
        with col3:
            st.metric(
                label="Delayed Tranches",
                value=delayed_count,
                delta=f"-{delayed_count}" if delayed_count > 0 else "On Track",
                help="Tranches that were not disbursed on their scheduled date. Delays may indicate project implementation issues or unmet conditions."
            )
        with col4:
            st.metric(
                label="On-Time Disbursement Rate",
                value=f"{on_time_rate}%",
                delta=f"{on_time_rate - 85:.1f}% vs 85% target",
                help="Percentage of tranches disbursed on or before scheduled date. Target is 85%+. Lower rates suggest operational bottlenecks."
            )
        
        st.markdown("---")
        
        # Disbursement Schedule Table
        st.subheader("Disbursement Schedule")
        st.caption("All scheduled tranches with status indicators. Delayed tranches highlighted in red.")
        
        def color_status(val):
            if val == "Delayed":
                return "background-color: #ffcccc; color: #cc0000"
            elif val == "Disbursed":
                return "background-color: #ccffcc; color: #006600"
            elif val == "Pending":
                return "background-color: #fff3cd; color: #856404"
            return ""
        
        schedule_display = schedule_df.style.applymap(color_status, subset=["Status"])
        st.dataframe(schedule_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Disbursement Progress by Project")
            
            progress_df = df[["Project Name", "Commitment ($M)", "Disbursed ($M)", "Disbursement Ratio"]].copy()
            progress_df = progress_df.sort_values("Disbursement Ratio", ascending=True)
            
            progress_fig = go.Figure()
            progress_fig.add_trace(go.Bar(
                y=progress_df["Project Name"],
                x=progress_df["Disbursement Ratio"],
                orientation="h",
                marker_color=progress_df["Disbursement Ratio"].apply(
                    lambda x: "#228B22" if x >= 70 else "#FFA500" if x >= 40 else "#FF4500"
                ),
                hovertemplate="<b>%{y}</b><br>Progress: %{x:.1f}%<extra></extra>"
            ))
            
            progress_fig.add_vline(
                x=50, line_dash="dash", line_color="gray",
                annotation_text="50% Benchmark", annotation_position="top"
            )
            
            progress_fig.update_layout(
                title="Disbursement Progress by Project (%)",
                xaxis_title="Disbursement Ratio (%)",
                yaxis_title="Project",
                showlegend=False,
                height=600
            )
            
            st.plotly_chart(progress_fig, use_container_width=True)
            st.caption("📈 **Interpretation:** Green bars (>70%) indicate good progress. Orange (40-70%) need monitoring. Red (<40%) may signal implementation problems requiring intervention.")
        
        with chart_col2:
            st.subheader("Monthly Disbursement Trend")
            
            # Generate monthly trend data
            schedule_df["Scheduled Date"] = pd.to_datetime(schedule_df["Scheduled Date"])
            monthly_disb = schedule_df[schedule_df["Status"] == "Disbursed"].groupby(
                schedule_df["Scheduled Date"].dt.to_period("M")
            )["Tranche Amount ($M)"].sum().reset_index()
            monthly_disb["Period"] = monthly_disb["Scheduled Date"].astype(str)
            
            trend_fig = go.Figure()
            trend_fig.add_trace(go.Scatter(
                x=monthly_disb["Period"],
                y=monthly_disb["Tranche Amount ($M)"],
                mode="lines+markers",
                line=dict(color=GOLD, width=3),
                marker=dict(size=8),
                fill="tozeroy",
                fillcolor="rgba(212, 175, 55, 0.2)",
                hovertemplate="<b>%{x}</b><br>Disbursed: $%{y:.1f}M<extra></extra>"
            ))
            
            trend_fig.update_layout(
                title="Monthly Disbursement Trend ($M)",
                xaxis_title="Month",
                yaxis_title="Amount Disbursed ($M)",
                showlegend=False
            )
            
            st.plotly_chart(trend_fig, use_container_width=True)
            st.caption("📊 **Trend Analysis:** Rising trend indicates accelerating project implementation. Declining trend may reflect project completion pipeline or new approval slowdown.")
    
    # ==================== TAB 4: PORTFOLIO RISK ====================
    with tab4:
        st.header("Portfolio Risk Analytics")
        st.markdown("Comprehensive risk measurement including VaR, stress testing, and concentration analysis.")
        
        # VaR and CVaR Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate VaR and CVaR at different confidence levels
        total_exposure = df["Outstanding ($M)"].sum()
        
        # Simulate portfolio losses
        np.random.seed(42)
        simulated_losses = np.random.normal(0.02, 0.12, 100000) * total_exposure
        
        var_95 = np.percentile(simulated_losses, 5)
        var_99 = np.percentile(simulated_losses, 1)
        cvar_95 = simulated_losses[simulated_losses <= var_95].mean()
        cvar_99 = simulated_losses[simulated_losses <= var_99].mean()
        
        with col1:
            st.metric(
                label="VaR (95% Confidence)",
                value=f"${abs(var_95):,.1f}M",
                help="Value at Risk at 95% confidence. Maximum expected 1-year loss with 95% certainty. 5% chance of loss exceeding this amount."
            )
        with col2:
            st.metric(
                label="VaR (99% Confidence)",
                value=f"${abs(var_99):,.1f}M",
                help="Value at Risk at 99% confidence. More conservative measure. Only 1% chance of loss exceeding this amount in a year."
            )
        with col3:
            st.metric(
                label="CVaR (95%)",
                value=f"${abs(cvar_95):,.1f}M",
                help="Conditional VaR / Expected Shortfall at 95%. Average loss in the worst 5% of scenarios. More conservative than VaR."
            )
        with col4:
            st.metric(
                label="CVaR (99%)",
                value=f"${abs(cvar_99):,.1f}M",
                help="Expected Shortfall at 99%. Average loss in the worst 1% of scenarios. Captures extreme tail risk events."
            )
        
        st.markdown("---")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Credit Risk Heatmap")
            
            # Create country x sector matrix
            heatmap_data = df.groupby(["Country", "Sector"])["Outstanding ($M)"].sum().reset_index()
            heatmap_pivot = heatmap_data.pivot(index="Country", columns="Sector", values="Outstanding ($M)").fillna(0)
            
            heatmap_fig = go.Figure(data=go.Heatmap(
                z=heatmap_pivot.values,
                x=heatmap_pivot.columns,
                y=heatmap_pivot.index,
                colorscale="YlOrRd",
                hovertemplate="<b>%{y}</b> - %{x}<br>Outstanding: $%{z:.1f}M<extra></extra>"
            ))
            
            heatmap_fig.update_layout(
                title="Portfolio Exposure by Country and Sector ($M)",
                xaxis_title="Sector",
                yaxis_title="Country"
            )
            
            st.plotly_chart(heatmap_fig, use_container_width=True)
            st.caption("🔥 **Heatmap Guide:** Darker red indicates higher exposure. Concentrated cells (high exposure in single country-sector combination) represent elevated concentration risk.")
        
        with chart_col2:
            st.subheader("Loan Maturity Profile")
            
            # Extract maturity years
            df["Maturity Year"] = pd.to_datetime(df["Maturity Date"]).dt.year
            maturity_profile = df.groupby("Maturity Year")["Outstanding ($M)"].sum().reset_index()
            
            maturity_fig = go.Figure()
            maturity_fig.add_trace(go.Bar(
                x=maturity_profile["Maturity Year"],
                y=maturity_profile["Outstanding ($M)"],
                marker_color=DARK_BLUE,
                hovertemplate="<b>%{x}</b><br>Maturing: $%{y:.1f}M<extra></extra>"
            ))
            
            # Highlight maturity walls (years with >15% of portfolio)
            total_maturing = maturity_profile["Outstanding ($M)"].sum()
            maturity_wall_years = maturity_profile[
                maturity_profile["Outstanding ($M)"] > (total_maturing * 0.15)
            ]["Maturity Year"]
            
            for year in maturity_wall_years:
                maturity_fig.add_vline(
                    x=year, line_dash="dash", line_color="red", line_width=2
                )
            
            maturity_fig.update_layout(
                title="Loan Maturity Profile by Year ($M)",
                xaxis_title="Maturity Year",
                yaxis_title="Outstanding Balance ($M)",
                showlegend=False
            )
            
            st.plotly_chart(maturity_fig, use_container_width=True)
            st.caption("⚠️ **Maturity Wall Alert:** Red dashed lines indicate years where >15% of portfolio matures simultaneously. Creates refinancing risk for borrowers.")
        
        st.markdown("---")
        
        # Stress Test Simulator
        st.subheader("Stress Test Simulator")
        st.caption("Adjust shock parameters to see impact on portfolio value. Based on simplified duration and FX sensitivity models.")
        
        stress_col1, stress_col2 = st.columns(2)
        
        with stress_col1:
            interest_shock = st.slider(
                "Interest Rate Shock (+%)",
                min_value=0.0,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Parallel shift in interest rates. Higher rates reduce present value of fixed-rate loans and increase borrowing costs."
            )
        
        with stress_col2:
            fx_shock = st.slider(
                "Currency Depreciation (%)",
                min_value=0.0,
                max_value=50.0,
                value=10.0,
                step=5.0,
                help="Local currency depreciation against USD. Affects borrowers with USD-denominated debt but local currency revenues."
            )
        
        # Calculate stress impacts (simplified model)
        base_portfolio_value = total_exposure
        
        # Interest rate impact (duration approximation)
        avg_duration = 8.5  # years
        rate_impact = -(avg_duration * interest_shock / 100) * base_portfolio_value
        
        # FX impact (assuming 40% FX-sensitive loans)
        fx_sensitive_portion = 0.4 * base_portfolio_value
        fx_impact = -(fx_shock / 100) * fx_sensitive_portion
        
        total_impact = rate_impact + fx_impact
        stressed_value = base_portfolio_value + total_impact
        
        stress_result_col1, stress_result_col2, stress_result_col3 = st.columns(3)
        
        with stress_result_col1:
            st.metric(
                label="Base Portfolio Value",
                value=f"${base_portfolio_value:,.1f}M",
                help="Current outstanding balance before stress scenarios applied."
            )
        
        with stress_result_col2:
            delta_display = f"${total_impact:,.1f}M"
            st.metric(
                label="Stress Impact",
                value=delta_display,
                delta=f"{(total_impact/base_portfolio_value)*100:.2f}%",
                help="Combined impact of interest rate and FX shocks. Negative values indicate portfolio value decline."
            )
        
        with stress_result_col3:
            st.metric(
                label="Stressed Portfolio Value",
                value=f"${stressed_value:,.1f}M",
                delta=f"{((stressed_value/base_portfolio_value)-1)*100:.2f}%",
                help="Portfolio value after applying stress scenarios. Used for capital adequacy and provisioning assessments."
            )
        
        # Visualize stress test
        stress_fig = go.Figure()
        stress_fig.add_trace(go.Bar(
            x=["Base Value", "Rate Shock Impact", "FX Shock Impact", "Stressed Value"],
            y=[base_portfolio_value, rate_impact, fx_impact, stressed_value],
            marker_color=[DARK_BLUE, "#FF6B6B", "#4ECDC4", "#C44569"],
            hovertemplate="<b>%{x}</b><br>Value: $%{y:.1f}M<extra></extra>"
        ))
        
        stress_fig.update_layout(
            title="Stress Test Visualization ($M)",
            yaxis_title="Portfolio Value ($M)",
            showlegend=False
        )
        
        st.plotly_chart(stress_fig, use_container_width=True)
        st.caption(f"📉 **Scenario:** +{interest_shock}% rates cause ${abs(rate_impact):.1f}M impact. {fx_shock}% FX depreciation causes ${abs(fx_impact):.1f}M impact. Combined: ${abs(total_impact):.1f}M total impact.")
    
    # ==================== TAB 5: DATA QUALITY & RECONCILIATION ====================
    with tab5:
        st.header("🔍 Data Quality & Reconciliation")
        st.markdown("Monitor data integrity, track reconciliation issues, and assess completeness across the portfolio.")
        
        # Methodology Note
        st.info("""
        **Data Quality Framework:** All checks follow a four-step reconciliation methodology:
        1. **Identify inconsistency** - Automated validation rules flag anomalies
        2. **Trace to source** - Link issues to original data entry points or systems
        3. **Determine root cause** - Classify as data entry error, definitional mismatch, or process gap
        4. **Remediate and document** - Correct errors and update procedures to prevent recurrence
        """)
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_issues = len(dq_issues)
        high_severity = len(dq_issues[dq_issues["Severity"] == "High"])
        medium_severity = len(dq_issues[dq_issues["Severity"] == "Medium"])
        low_severity = len(dq_issues[dq_issues["Severity"] == "Low"])
        
        avg_completeness = completeness_df["Completeness Score (%)"].mean()
        
        with col1:
            st.metric(
                label="Total Issues Flagged",
                value=total_issues,
                help="Number of data quality issues identified through automated validation checks. Includes both resolved and unresolved items."
            )
        with col2:
            st.metric(
                label="High Severity Issues",
                value=high_severity,
                delta=f"-{high_severity}" if high_severity > 0 else "None",
                help="Critical issues requiring immediate attention. May affect financial reporting or regulatory compliance."
            )
        with col3:
            st.metric(
                label="Avg Completeness Score",
                value=f"{avg_completeness:.1f}%",
                delta=f"{avg_completeness - 95:.1f}% vs 95% target",
                help="Average percentage of required fields populated across all projects. Target is 95%+ for operational data."
            )
        with col4:
            resolved = 2  # Simulated resolved count
            st.metric(
                label="Resolution Rate",
                value=f"{(resolved/total_issues)*100:.0f}%",
                delta=f"+{(resolved/total_issues)*100:.0f}% resolved",
                help="Percentage of flagged issues that have been resolved. Tracks effectiveness of data governance processes."
            )
        
        st.markdown("---")
        
        # Issue Flag Table
        st.subheader("Data Quality Issues Log")
        st.caption("All flagged issues with severity classification and recommended remediation actions.")
        
        def color_severity(val):
            if val == "High":
                return "background-color: #ffcccc; color: #cc0000; font-weight: bold"
            elif val == "Medium":
                return "background-color: #fff3cd; color: #856404"
            elif val == "Low":
                return "background-color: #d4edda; color: #155724"
            return ""
        
        dq_display = dq_issues.style.applymap(color_severity, subset=["Severity"])
        st.dataframe(dq_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Data Completeness by Project
        st.subheader("Data Completeness by Project")
        st.caption("Percentage of required fields populated for each project. Required fields include: ID, name, country, sector, status, costs, loan terms, dates, and risk ratings.")
        
        completeness_sorted = completeness_df.sort_values("Completeness Score (%)", ascending=True)
        
        completeness_fig = go.Figure()
        completeness_fig.add_trace(go.Bar(
            y=completeness_sorted["Project Name"],
            x=completeness_sorted["Completeness Score (%)"],
            orientation="h",
            marker_color=completeness_sorted["Completeness Score (%)"].apply(
                lambda x: "#228B22" if x >= 95 else "#FFA500" if x >= 85 else "#FF4500"
            ),
            hovertemplate="<b>%{y}</b><br>Completeness: %{x:.1f}%<extra></extra>"
        ))
        
        completeness_fig.add_vline(
            x=95, line_dash="dash", line_color="green", line_width=2,
            annotation_text="95% Target", annotation_position="top"
        )
        
        completeness_fig.update_layout(
            title="Data Completeness Score by Project (%)",
            xaxis_title="Completeness Score (%)",
            yaxis_title="Project",
            showlegend=False,
            height=500
        )
        
        st.plotly_chart(completeness_fig, use_container_width=True)
        st.caption("✅ **Green bars (≥95%)** meet data quality standards. **Orange (85-95%)** need improvement. **Red (<85%)** require immediate data cleanup.")
        
        st.markdown("---")
        
        # Reconciliation Summary
        st.subheader("Reconciliation Summary")
        
        recon_col1, recon_col2 = st.columns(2)
        
        with recon_col1:
            st.markdown("#### Issue Categories")
            issue_categories = dq_issues["Issue Description"].apply(
                lambda x: "Cost Reconciliation" if "cost" in x.lower() else
                          "Commitment Validation" if "commitment" in x.lower() else
                          "Missing Data" if "missing" in x.lower() else
                          "Duplicate Detection" if "duplicate" in x.lower() else
                          "Balance Verification" if "balance" in x.lower() else
                          "Date Validation"
            ).value_counts()
            
            cat_fig = px.pie(
                values=issue_categories.values,
                names=issue_categories.index,
                title="Issues by Category",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            cat_fig.update_traces(hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>")
            st.plotly_chart(cat_fig, use_container_width=True)
        
        with recon_col2:
            st.markdown("#### Resolution Status")
            
            # Simulated resolution status
            resolution_status = pd.DataFrame({
                "Status": ["Resolved", "In Progress", "Pending Review", "Unresolved"],
                "Count": [2, 2, 1, 1]
            })
            
            status_fig = px.bar(
                resolution_status,
                x="Status",
                y="Count",
                title="Issues by Resolution Status",
                color="Status",
                color_discrete_map={
                    "Resolved": "#228B22",
                    "In Progress": "#FFA500",
                    "Pending Review": "#4169E1",
                    "Unresolved": "#FF4500"
                }
            )
            status_fig.update_traces(hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>")
            status_fig.update_layout(showlegend=False)
            
            st.plotly_chart(status_fig, use_container_width=True)
        
        # Detailed Reconciliation Log
        st.markdown("---")
        st.subheader("Reconciliation Log")
        
        log_data = {
            "Date": ["2024-01-15", "2024-01-18", "2024-01-20", "2024-01-22", "2024-01-25"],
            "Issue ID": ["DQ-006", "DQ-001", "DQ-002", "DQ-004", "DQ-003"],
            "Action": ["Corrected", "Under Review", "Escalated", "Merged", "Data Request Sent"],
            "Owner": ["Data Team", "Finance", "Legal", "Operations", "Risk"],
            "Status": ["Resolved", "In Progress", "In Progress", "Resolved", "Pending"]
        }
        
        log_df = pd.DataFrame(log_data)
        
        st.dataframe(
            log_df,
            use_container_width=True,
            hide_index=True
        )
    
    # ==================== TAB 6: LOAN TERMINOLOGY REFERENCE ====================
    with tab6:
        render_terminology_reference()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**MDB Project & Loan Portfolio Monitor** | AIIB Demonstration Dashboard | "
        "Built with Streamlit & Plotly"
    )
    st.caption(
        "This dashboard is for demonstration purposes only. All data is synthetically generated "
        "and does not represent actual AIIB portfolio information."
    )


if __name__ == "__main__":
    main()
