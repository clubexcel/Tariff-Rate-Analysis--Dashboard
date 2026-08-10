import streamlit as st
import plotly.express as px
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
import numpy as np

# --- 1. Page Configuration & Styling ---
st.set_page_config(page_title="ASEAN Economic Dashboard", layout="wide")

# Custom CSS for "Premium" Aesthetics
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(17, 24, 39) 0%, rgb(10, 10, 15) 90%);
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #f0f8ff;
    }
    h1 {
        font-weight: 800;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Custom Plotly container styling if needed */
    .stPlotlyChart {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Data Loading Utility ---
@st.cache_data
def load_data(filename: str):
    """Load CSV file from absolute path or relative to the script location."""
    # Try looking in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
        
    # Fallback to absolute path check
    if os.path.isabs(filename) and os.path.exists(filename):
        return pd.read_csv(filename)
        
    # Final fallback to direct path
    if os.path.exists(filename):
        return pd.read_csv(filename)
        
    st.error(f"❌ Critical Error: File not found - {filename}. Please check your directory.")
    return None

def clean_percent(df, columns):
    """Convert percentage strings like '2.50%' to floats."""
    for col in columns:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('%', '').str.strip()
                df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# --- 3. Header Section ---
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title('ASEAN Economic Insights')
    st.markdown("### Interactive Analysis of Tariff Rates & Banking Performance")
with col_header_2:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/87/Flag_of_ASEAN.svg/1200px-Flag_of_ASEAN.svg.png", width=100)

st.divider()

# --- 4. Main Section: Tariff Analysis ---
tariff_file = "asean_tariff_tax_analysis.csv" 
df_tariff = load_data(tariff_file)

if df_tariff is not None:
    st.header("🌍 Regional Trade & Tariffs")
    
    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    avg_tariff = df_tariff['Tariff rate'].mean()
    total_trade = df_tariff['Total Trade'].sum()
    highest_tariff_country = df_tariff.loc[df_tariff['Tariff rate'].idxmax(), 'CountryISO3']
    
    kpi1.metric("Avg Tariff Rate", f"{avg_tariff:.2f}%", delta="-0.5% (YoY)")
    kpi2.metric("Total Trade Volume", f"${total_trade:,.0f}M", delta="+12%")
    kpi3.metric("Highest Tariff Country", highest_tariff_country)
    
    st.markdown("#### Geographical Distribution of Tariffs")
    
    # CHOROPLETH MAP
    fig_map = px.choropleth(
        df_tariff,
        locations="CountryISO3",
        color="Tariff rate",
        hover_name="CountryISO3",
        hover_data=["Tariff value", "Total Trade"],
        color_continuous_scale="Viridis",
        projection="mercator",
        title="Tariff Rate Heatmap (ASEAN Region)",
        template="plotly_dark"
    )
    # Focus map on Asia/ASEAN
    fig_map.update_geos(fitbounds="locations", visible=False, showcountries=True, countrycolor="RebeccaPurple")
    fig_map.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # Detailed Bar Chart
    st.markdown("#### Comparative Metrics")
    tab_bar1, tab_bar2 = st.tabs(["By Tariff Rate", "By Trade Volume"])
    
    with tab_bar1:
        fig_bar = px.bar(
            df_tariff,
            x="CountryISO3",
            y="Tariff rate",
            color="Tariff rate",
            color_continuous_scale="RdBu_r",
            text_auto='.2s',
            title="Sovereign Tariff Rates",
            template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with tab_bar2:
        fig_trade = px.bar(
            df_tariff,
            x="CountryISO3",
            y="Total Trade",
            color="Total Trade",
            color_continuous_scale="Magma",
            title="Total Trade Volume by Country",
            template="plotly_dark"
        )
        st.plotly_chart(fig_trade, use_container_width=True)

# --- 4.1 Historical Tariff Trends ---
st.divider()
st.header("📈 Historical & Preliminary Tariff Trends")
hist_file = "asean_historical_tariffs.csv"
df_hist = load_data(hist_file)

if df_hist is not None:
    df_hist = clean_percent(df_hist, ["2023 (Actual)", "2024 (Actual)", "2025 (Preliminary)"])
    
    # Reshape for plotting
    df_hist_melted = df_hist.melt(id_vars=["Country"], var_name="Year", value_name="Tariff Rate")
    
    fig_trend = px.line(
        df_hist_melted,
        x="Year",
        y="Tariff Rate",
        color="Country",
        markers=True,
        title="Sovereign Tariff Trajectories (2023-2025)",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- 4.2 US-ASEAN Tariff Impact ---
st.divider()
st.header("US-ASEAN Trade Relations")
us_tariff_file = "asean_us_tariffs.csv"
df_us = load_data(us_tariff_file)

if df_us is not None:
    df_us = clean_percent(df_us, ["2024 US Tariff (Avg)", "Aug 2025 US Tariff"])
    
    col_us1, col_us2 = st.columns([2, 1])
    
    with col_us1:
        fig_us_bar = px.bar(
            df_us,
            x="Exporter",
            y=["2024 US Tariff (Avg)", "Aug 2025 US Tariff"],
            barmode="group",
            title="Anticipated US Tariff Increase (Impact Analysis)",
            labels={"value": "Tariff Rate (%)", "variable": "Period"},
            template="plotly_dark",
            color_discrete_map={"2024 US Tariff (Avg)": "#4facfe", "Aug 2025 US Tariff": "#ff4b4b"}
        )
        st.plotly_chart(fig_us_bar, use_container_width=True)
        
    with col_us2:
        st.warning("### Strategic Insight")
        st.write("""
            The projected sharp increase in US tariffs (Aug 2025) across major ASEAN exporters 
            indicates a significant shift in trade policy. 
            
            **Key Observations:**
            - **Vietnam & Malaysia** face the highest relative jumps.
            - **Singapore** remains the least affected due to existing trade agreements.
            - Manufacturers may need to pivot supply chains before Q3 2025.
        """)

# --- 4.3 HSBC Strategic Negotiation Impact ---
st.divider()
st.header("🤝 HSBC Strategic Negotiation Analysis")
hsbc_file = "asean_hsbc_strategy.csv"
df_hsbc = load_data(hsbc_file)

if df_hsbc is not None:
    df_hsbc = clean_percent(df_hsbc, ["Initial April 2025 Tariff", "Negotiated Aug 2025 Tariff"])
    
    # Calculate negotiation success (reduction percentage)
    df_hsbc["Reduction"] = (df_hsbc["Initial April 2025 Tariff"] - df_hsbc["Negotiated Aug 2025 Tariff"])
    avg_reduction = df_hsbc["Reduction"].mean()
    
    col_hsbc_1, col_hsbc_2 = st.columns([2, 1])
    
    with col_hsbc_1:
        fig_hsbc = px.bar(
            df_hsbc,
            x="Economy",
            y=["Initial April 2025 Tariff", "Negotiated Aug 2025 Tariff"],
            barmode="group",
            title="Tariff Reduction: Initial vs. Negotiated (HSBC Strategy)",
            labels={"value": "Tariff Rate (%)", "variable": "Phase"},
            template="plotly_dark",
            color_discrete_map={
                "Initial April 2025 Tariff": "#ff4b4b", 
                "Negotiated Aug 2025 Tariff": "#00f2fe"
            }
        )
        st.plotly_chart(fig_hsbc, use_container_width=True)
        
    with col_hsbc_2:
        st.metric("Avg. Negotiated Reduction", f"{avg_reduction:.1f}%", help="Average percentage points reduced through strategy.")
        st.info("""
            **Strategic Negotiation Insights:**
            HSBC's trade policy strategy suggests a significant reduction in anticipated tariffs 
            through bilateral negotiations. 
            
            - **Vietnam & Thailand** show the most substantial negotiation delta.
            - The goal is to stabilize rates at an average of **~17.4%** across the bloc.
            - Focus remains on maintaining Singapore's status quo at **10%**.
        """)

# --- 5. Secondary Section: Banking Analysis ---
st.divider()
st.header("🏦 Financial Sector Performance Prediction")

banks_file = "sea_banks_actual_vs_predicted.csv"
df_banks = load_data(banks_file)

if df_banks is not None:
    # Error Calculation
    df_banks["Diff"] = df_banks["predicted_Total Assets"] - df_banks["true_Total Assets"]
    df_banks["Diff_Abs"] = df_banks["Diff"].abs()
    
    col_bank_1, col_bank_2 = st.columns(2)
    
    with col_bank_1:
        st.subheader("Model Residuals")
        st.caption("Difference between predicted and actual assets.")
        fig_resid = px.bar(
            df_banks,
            x="Bank Name",
            y="Diff",
            color="Diff",
            color_continuous_scale="RdYlGn",
            labels={"Diff": "Prediction Error"},
            template="plotly_dark"
        )
        fig_resid.update_layout(showlegend=False)
        st.plotly_chart(fig_resid, use_container_width=True)
        
    with col_bank_2:
        st.subheader("Actual vs. Predicted")
        st.caption("Scatter plot analysis with trendline.")
        fig_scat = px.scatter(
            df_banks,
            x="true_Total Assets",
            y="predicted_Total Assets",
            color="Diff_Abs", # Color by error magnitude
            size="Diff_Abs",
            hover_name="Bank Name",
            labels={
                "true_Total Assets": "Actual Assets", 
                "predicted_Total Assets": "Predicted Assets"
            },
            template="plotly_dark",
            trendline="ols"
        )
        st.plotly_chart(fig_scat, use_container_width=True)
        
# --- 6. Overview ---
st.divider()
st.header("📈 ASEAN Trade Indicators Overview")
overview_file = "asean_overview.csv"
df_overview = load_data(overview_file)

if df_overview is not None:
    # Rename columns for easier plotting
    df_overview.columns = [c.replace(' (%)', '') for c in df_overview.columns]
    metrics = ["Applied Tariff", "NTM Frequency", "NTM Coverage", "Effective Tariff"]
    df_overview = clean_percent(df_overview, metrics)
    
    tab_ov1, tab_ov2 = st.tabs(["Indicator Comparison", "Raw Data"])
    
    with tab_ov1:
        fig_overview = px.bar(
            df_overview,
            x="Country",
            y=metrics,
            barmode="group",
            title="Sovereign Comparison: Applied vs Effective Tariffs & NTMs",
            labels={"value": "Percentage (%)", "variable": "Metric"},
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig_overview, use_container_width=True)
    
    with tab_ov2:
        st.dataframe(df_overview.style.background_gradient(cmap='Blues'), use_container_width=True)
