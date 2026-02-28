import streamlit as st
import pandas as pd
from insights_engine import generate_insights
import plotly.express as px
import plotly.graph_objects as go
import psycopg
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weitblick — Supply Chain Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CHART_COLORS = ["#6366F1", "#10B981", "#F59E0B", "#F43F5E", "#0EA5E9", "#8B5CF6"]

# ─── GLOBAL STYLES ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── MAIN BG ── */
html, body, .main,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: #0D0E1A !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
[data-testid="stMain"] { background: transparent !important; }
.block-container {
    background: transparent !important;
    padding: 1.5rem 2rem 4rem !important;
    max-width: 1440px !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Completely hide sidebar (we don't use it anymore) ── */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
}
[data-testid="stAppViewContainer"] > section:not([data-testid="stSidebar"]),
[data-testid="stMain"] {
    margin-left: 0 !important;
    padding-left: 0 !important;
    width: 100% !important;
}

/* ══════════════════════════════════════
   PAGE HEADER
══════════════════════════════════════ */
.page-header-wrap {
    background: linear-gradient(135deg, #4338CA 0%, #6D28D9 50%, #7C3AED 100%);
    border-radius: 18px;
    margin-bottom: 0;
    box-shadow: 0 10px 40px rgba(99,102,241,0.28), 0 0 0 1px rgba(255,255,255,0.08) inset;
    position: relative;
    overflow: hidden;
}
.page-header-wrap::before {
    content: ''; position: absolute;
    top: -70px; right: 120px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
/* Pure flexbox inner row — no Streamlit columns involved */
.ph-inner {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1.1rem 1.8rem;
    position: relative;
    z-index: 1;
}
.ph-logo-slot {
    flex-shrink: 0;
    display: flex;
    align-items: center;
}
/* Logo image — contained, small */
.header-logo {
    height: 42px;
    width: auto;
    max-width: 140px;
    object-fit: contain;
    border-radius: 8px;
    display: block;
}
/* Logo placeholder when no PNG provided */
.logo-placeholder {
    background: rgba(255,255,255,0.1);
    border: 2px dashed rgba(255,255,255,0.28);
    border-radius: 10px;
    width: 120px; height: 42px;
    display: flex; align-items: center; justify-content: center;
    color: rgba(255,255,255,0.38);
    font-size: 0.58rem; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
}
.ph-text-slot { flex: 1; text-align: right; }
/* Title + subtitle */
.ph-title {
    font-size: 1.35rem; font-weight: 700;
    color: #fff; letter-spacing: -0.03em; line-height: 1.2;
}
.ph-subtitle {
    font-size: 0.7rem; color: rgba(255,255,255,0.5); margin-top: 4px;
}

/* ── Override Streamlit widget styles inside the filter row ── */

/* All filter widget text */
[data-testid="stHorizontalBlock"] [data-baseweb="select"] > div,
[data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-size: 0.78rem !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="select"] > div:focus-within,
[data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="select"] span,
[data-testid="stHorizontalBlock"] [data-baseweb="select"] div[class*="singleValue"],
[data-testid="stHorizontalBlock"] [data-baseweb="select"] div[class*="placeholder"] {
    color: #CBD5E1 !important;
    font-size: 0.78rem !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="menu"] {
    background: #12132B !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 12px !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5) !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="menu"] li {
    color: #E2E8F0 !important;
    font-size: 0.78rem !important;
    background: transparent !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="menu"] li:hover {
    background: rgba(99,102,241,0.18) !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="tag"] {
    background: rgba(99,102,241,0.2) !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 6px !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="tag"] span {
    color: #A5B4FC !important;
    font-size: 0.72rem !important;
}
[data-testid="stHorizontalBlock"] [data-baseweb="tag"] svg {
    fill: #A5B4FC !important;
}

/* Filter widget labels */
[data-testid="stHorizontalBlock"] label,
[data-testid="stHorizontalBlock"] [data-testid="stWidgetLabel"] p {
    font-size: 0.58rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: rgba(99,102,241,0.7) !important;
    margin-bottom: 3px !important;
}

/* Date input text */
[data-testid="stHorizontalBlock"] input[type="text"],
[data-testid="stHorizontalBlock"] input[type="date"] {
    color: #CBD5E1 !important;
    background: transparent !important;
    border: none !important;
    font-size: 0.78rem !important;
}

/* Remove top padding from filter columns */
[data-testid="stHorizontalBlock"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Active filter chip count badge */
.filter-count {
    background: linear-gradient(135deg, #6366F1, #8B5CF6);
    color: #fff !important;
    font-size: 0.6rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
    margin-left: 6px;
}

/* ══════════════════════════════════════
   SECTION LABELS
══════════════════════════════════════ */
.section-label {
    font-size: 0.58rem; font-weight: 700;
    letter-spacing: 0.16em; text-transform: uppercase;
    color: #6366F1; margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 0.6rem; opacity: 0.9;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.3) 0%, transparent 100%);
}

/* ══════════════════════════════════════
   KPI CARDS
══════════════════════════════════════ */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.3rem !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2) !important;
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative; overflow: hidden;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 32px rgba(0,0,0,0.3) !important;
}
[data-testid="metric-container"]::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: 16px 16px 0 0;
}
[data-testid="column"]:nth-child(1) [data-testid="metric-container"]::before { background: linear-gradient(90deg,#6366F1,#818CF8); }
[data-testid="column"]:nth-child(2) [data-testid="metric-container"]::before { background: linear-gradient(90deg,#10B981,#34D399); }
[data-testid="column"]:nth-child(3) [data-testid="metric-container"]::before { background: linear-gradient(90deg,#F59E0B,#FCD34D); }
[data-testid="column"]:nth-child(4) [data-testid="metric-container"]::before { background: linear-gradient(90deg,#F43F5E,#FB7185); }
[data-testid="column"]:nth-child(5) [data-testid="metric-container"]::before { background: linear-gradient(90deg,#0EA5E9,#38BDF8); }
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.6rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #475569 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.7rem !important; font-weight: 700 !important;
    letter-spacing: -0.03em !important; color: #F1F5F9 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: #10B981 !important; font-size: 0.7rem !important;
}

/* ══════════════════════════════════════
   CHART CARDS
══════════════════════════════════════ */
.chart-card {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.2rem 0.3rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 6px 28px rgba(0,0,0,0.2), 0 1px 0 rgba(255,255,255,0.04) inset !important;
}
.chart-title {
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: #CBD5E1; margin-bottom: 0.7rem;
    display: flex; align-items: center; gap: 7px;
}
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }

/* ══════════════════════════════════════
   INSIGHT CARDS
══════════════════════════════════════ */
.insight-card {
    background: rgba(99,102,241,0.08);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(99,102,241,0.18);
    border-left: 3px solid #6366F1;
    border-radius: 12px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 0.55rem;
    font-size: 0.84rem; color: #C7D2FE; line-height: 1.65;
}

/* ══════════════════════════════════════
   DATAFRAME
══════════════════════════════════════ */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    overflow: hidden;
    box-shadow: 0 6px 28px rgba(0,0,0,0.18);
}
[data-testid="stDataFrame"] * { color: #E2E8F0 !important; }
[data-testid="stInfo"] {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
    color: #C7D2FE !important;
}
hr { border: none !important; border-top: 1px solid rgba(255,255,255,0.06) !important; margin: 1.25rem 0 !important; }

/* CTA two-column layout */
.cta-inner {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 3rem;
    position: relative;
    z-index: 1;
}
.cta-logo-col {
    flex: 0 0 420px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.cta-logo-col img {
    width: 400px !important;
    height: auto !important;
    max-height: 400px !important;
    object-fit: contain !important;
    border-radius: 12px;
    display: block;
}
.cta-logo-placeholder {
    width: 340px; height: 180px;
    background: rgba(255,255,255,0.06);
    border: 2px dashed rgba(255,255,255,0.2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    color: rgba(255,255,255,0.3);
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.cta-content-col {
    flex: 1;
    text-align: center;
    min-width: 0;
}
.cta-content-col .cta-heading { text-align: center; }
.cta-content-col .cta-subtext { text-align: center; margin: 0 auto 1.75rem; max-width: 520px; }
.cta-content-col .cta-buttons { justify-content: center; }
.cta-content-col .cta-divider { margin: 0 auto 1.25rem; max-width: 100%; }
.cta-content-col .cta-footer-row { justify-content: center; }
.cta-content-col .cta-eyebrow { justify-content: center; }


/* ══════════════════════════════════════
   CTA SECTION
══════════════════════════════════════ */
.cta-wrap {
    background: linear-gradient(135deg, #1E1B4B 0%, #2D1B69 40%, #1E1B4B 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 24px;
    padding: 3rem 3.5rem;
    position: relative;
    overflow: hidden;
    text-align: center;
    box-shadow: 0 20px 60px rgba(99,102,241,0.2), 0 0 0 1px rgba(255,255,255,0.05) inset;
}
.cta-wrap::before {
    content: ''; position: absolute;
    top: -80px; left: -80px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.cta-wrap::after {
    content: ''; position: absolute;
    bottom: -80px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.cta-eyebrow {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 20px; padding: 5px 14px;
    font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: #A5B4FC; margin-bottom: 1.25rem;
}
.cta-eyebrow-dot {
    width: 6px; height: 6px; background: #6366F1;
    border-radius: 50%; box-shadow: 0 0 8px #6366F1;
}
.cta-heading {
    font-size: 2rem; font-weight: 700; color: #F1F5F9;
    letter-spacing: -0.04em; line-height: 1.2;
    margin-bottom: 0.85rem; position: relative; z-index: 1;
}
.cta-heading span {
    background: linear-gradient(90deg, #818CF8, #C084FC);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.cta-subtext {
    font-size: 0.9rem; color: rgba(148,163,184,0.85);
    max-width: 540px; margin: 0 auto 2rem;
    line-height: 1.7; position: relative; z-index: 1;
}
.cta-buttons {
    display: flex; align-items: center; justify-content: center;
    gap: 1rem; flex-wrap: wrap;
    position: relative; z-index: 1; margin-bottom: 2rem;
}
.cta-btn-main {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.06); backdrop-filter: blur(12px);
    color: #E2E8F0 !important; font-size: 0.88rem; font-weight: 600;
    padding: 0.75rem 1.75rem; border-radius: 12px;
    text-decoration: none !important;
    border: 1px solid rgba(255,255,255,0.14);
    letter-spacing: -0.01em;
}
.cta-divider {
    height: 1px; background: rgba(255,255,255,0.07);
    margin: 0 auto 1.5rem; max-width: 480px;
    position: relative; z-index: 1;
}
.cta-footer-row {
    display: flex; align-items: center; justify-content: center;
    gap: 2rem; flex-wrap: wrap; position: relative; z-index: 1;
}
.cta-trust-item {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.72rem; color: rgba(148,163,184,0.65); font-weight: 500;
}
.cta-trust-icon { font-size: 0.85rem; opacity: 0.7; }

</style>
""", unsafe_allow_html=True)

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8", size=11),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=30, l=10, r=10),
    xaxis=dict(
        showgrid=False, zeroline=False,
        tickfont=dict(size=10, color="#64748B"),
        linecolor="rgba(255,255,255,0.07)", linewidth=1
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.05)", gridwidth=1,
        zeroline=False, tickfont=dict(size=10, color="#64748B"),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        font=dict(size=10, color="#94A3B8"), orientation="h",
        yanchor="bottom", y=1.02, xanchor="left", x=0
    ),
    colorway=CHART_COLORS,
    height=300
)

# ─── CONNECTION ───────────────────────────────────────────────────────────────
load_dotenv()
@st.cache_resource
def get_engine():
    return create_engine(
        os.getenv("DATABASE_URL"),
        pool_pre_ping=True
    )

# ─── DATA LOAD ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    query = "SELECT * FROM wb_int_prd.shipments ORDER BY shipment_date DESC;"
    try:
        engine = get_engine()
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data found. Run ETL first.")
    st.stop()

df['shipment_date'] = pd.to_datetime(df['shipment_date'])
df['delivery_date'] = pd.to_datetime(df['delivery_date'])

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
COMPANY_LOGO_PATH_SMALL = "assets/weitblick_transparent_logo.png"

import base64
def get_logo_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

logo_b64_small = get_logo_b64(COMPANY_LOGO_PATH_SMALL) if COMPANY_LOGO_PATH_SMALL else None

if logo_b64_small:
    logo_html = f'<img src="data:image/png;base64,{logo_b64_small}" class="header-logo" alt="Logo" />'
else:
    logo_html = '<div class="logo-placeholder">Your Logo</div>'

st.markdown(f'''
<div class="page-header-wrap">
    <div class="ph-inner">
        <div class="ph-logo-slot">{logo_html}</div>
        <div class="ph-text-slot">
            <div class="ph-title">🚚 Global Logistics Performance</div>
            <div class="ph-subtitle">Real-time shipment insights &amp; operational efficiency · Built by Weitblick</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# ─── INLINE FILTER BAR ────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-label">Filters</div>', unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns([2, 2, 2])

with fc1:
    date_range = st.date_input(
        "Date Range",
        [df['shipment_date'].min(), df['shipment_date'].max()],
        label_visibility="visible"
    )

with fc2:
    selected_mode = st.multiselect(
        "Transport Mode",
        options=sorted(df["transport_mode"].unique()),
        default=sorted(df["transport_mode"].unique()),
        placeholder="All modes"
    )

with fc3:
    selected_status = st.multiselect(
        "Status",
        options=sorted(df["status"].unique()),
        default=sorted(df["status"].unique()),
        placeholder="All statuses"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ─── FILTER ───────────────────────────────────────────────────────────────────
filtered_df = df.copy()
if selected_mode:
    filtered_df = filtered_df[filtered_df["transport_mode"].isin(selected_mode)]
if selected_status:
    filtered_df = filtered_df[filtered_df["status"].isin(selected_status)]
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['shipment_date'].dt.date >= date_range[0]) &
        (filtered_df['shipment_date'].dt.date <= date_range[1])
    ]
df = filtered_df

# ─── KPIs ─────────────────────────────────────────────────────────────────────
total_shipments = len(df)
total_revenue = df['revenue'].sum()
total_profit = df['profit'].sum()
on_time_rate = (df['on_time'].sum() / total_shipments) * 100 if total_shipments > 0 else 0
margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

st.markdown('<div class="section-label">Key Metrics</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📦 Shipments", f"{total_shipments:,}")
k2.metric("💰 Revenue", f"${total_revenue:,.0f}")
k3.metric("📈 Profit", f"${total_profit:,.0f}")
k4.metric("⏱️ On-Time Rate", f"{on_time_rate:.1f}%")
k5.metric("📊 Margin", f"{margin:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ─── ROW 1: TREND + DONUT ─────────────────────────────────────────────────────
st.markdown('<div class="section-label">Performance Overview</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#6366F1"></span>Revenue & Profit Trend</div>', unsafe_allow_html=True)
    trend = df.groupby(df['shipment_date'].dt.date)[['revenue', 'profit']].sum().reset_index()
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend['shipment_date'], y=trend['revenue'],
        name='Revenue', mode='lines',
        line=dict(color='#818CF8', width=2.5),
        fill='tozeroy', fillcolor='rgba(99,102,241,0.12)'
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend['shipment_date'], y=trend['profit'],
        name='Profit', mode='lines',
        line=dict(color='#34D399', width=2, dash='dot'),
        fill='tozeroy', fillcolor='rgba(16,185,129,0.07)'
    ))
    fig_trend.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig_trend, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#10B981"></span>On-Time vs Delayed</div>', unsafe_allow_html=True)
    if df['on_time'].dtype != bool:
        df['on_time_clean'] = df['on_time'].apply(lambda x: True if str(x).lower() in ["1","true","yes"] else False)
    else:
        df['on_time_clean'] = df['on_time']
    on_time_count = int(df['on_time_clean'].sum())
    delayed_count = len(df) - on_time_count
    if on_time_count + delayed_count > 0:
        fig_donut = go.Figure(data=[go.Pie(
            labels=['On-Time', 'Delayed'],
            values=[on_time_count, delayed_count],
            hole=0.7,
            marker=dict(colors=["#10B981", "#F43F5E"], line=dict(color='rgba(0,0,0,0.2)', width=2)),
            textfont=dict(family="Plus Jakarta Sans", size=11, color="#E2E8F0"),
        )])
        fig_donut.add_annotation(text=f"<b>{on_time_rate:.0f}%</b>", x=0.5, y=0.54, showarrow=False,
            font=dict(size=28, color="#F1F5F9", family="Plus Jakarta Sans"), xref="paper", yref="paper")
        fig_donut.add_annotation(text="on time", x=0.5, y=0.39, showarrow=False,
            font=dict(size=11, color="#64748B", family="Plus Jakarta Sans"), xref="paper", yref="paper")
        fig_donut.update_layout(**{**PLOTLY_LAYOUT, "height": 280, "showlegend": True})
        st.plotly_chart(fig_donut, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── MAP ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Route Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#F59E0B"></span>Shipment Origins</div>', unsafe_allow_html=True)
if {"origin_lat", "origin_lon"}.issubset(df.columns):
    map_df = df.rename(columns={"origin_lat": "lat", "origin_lon": "lon"})
    st.map(map_df[['lat', 'lon']], color='#818CF8', size=12)
else:
    city_counts = df['origin_city'].value_counts().reset_index()
    city_counts.columns = ['Origin City', 'Shipments']
    st.dataframe(city_counts, width="stretch", hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── 3-COL ANALYTICS ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Operational Analytics</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#F59E0B"></span>Avg Delay by Mode</div>', unsafe_allow_html=True)
    delay_mode = df.groupby('transport_mode')['delay_hours'].mean().reset_index().sort_values('delay_hours')
    fig_delay = go.Figure(go.Bar(
        x=delay_mode['transport_mode'], y=delay_mode['delay_hours'],
        marker=dict(color=CHART_COLORS[:len(delay_mode)], line=dict(width=0), cornerradius=6),
    ))
    fig_delay.update_layout(**{**PLOTLY_LAYOUT, "height": 250})
    st.plotly_chart(fig_delay, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#F43F5E"></span>Top Delayed Routes</div>', unsafe_allow_html=True)
    route_delay = (
        df.groupby(["origin_city", "destination_city"])["delay_hours"]
        .mean().reset_index().sort_values("delay_hours", ascending=False).head(5)
    )
    route_delay.columns = ['Origin', 'Destination', 'Avg Delay (h)']
    route_delay['Avg Delay (h)'] = route_delay['Avg Delay (h)'].round(1)
    st.dataframe(route_delay, width="stretch", hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#8B5CF6"></span>Status Breakdown</div>', unsafe_allow_html=True)
    status_counts = df['status'].value_counts()
    fig_status = go.Figure(data=[go.Pie(
        labels=status_counts.index, values=status_counts.values,
        hole=0.5,
        marker=dict(colors=CHART_COLORS, line=dict(color='rgba(0,0,0,0.15)', width=2)),
        textfont=dict(family="Plus Jakarta Sans", size=10, color="#E2E8F0"),
    )])
    fig_status.update_layout(**{**PLOTLY_LAYOUT, "height": 250})
    st.plotly_chart(fig_status, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── PROFITABILITY ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Profitability Analysis</div>', unsafe_allow_html=True)
p1, p2 = st.columns(2)

with p1:
    st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#10B981"></span>Profit by Transport Mode</div>', unsafe_allow_html=True)
    profit_mode = df.groupby('transport_mode')['profit'].sum().reset_index().sort_values('profit')
    fig_profit = go.Figure(go.Bar(
        x=profit_mode['profit'], y=profit_mode['transport_mode'],
        orientation='h',
        marker=dict(color=CHART_COLORS[:len(profit_mode)], line=dict(width=0), cornerradius=6),
    ))
    fig_profit.update_layout(**{**PLOTLY_LAYOUT, "height": 270,
        "xaxis": {**PLOTLY_LAYOUT["xaxis"], "tickprefix": "$", "tickformat": ",.0f"},
        "yaxis": {**PLOTLY_LAYOUT["yaxis"], "showgrid": False}
    })
    st.plotly_chart(fig_profit, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

with p2:
    st.markdown('<div class="chart-card"><div class="chart-title"><span class="dot" style="background:#0EA5E9"></span>Cost vs Revenue</div>', unsafe_allow_html=True)
    fig_scatter = px.scatter(
        df, x="shipment_cost", y="revenue",
        color="transport_mode", size="profit",
        hover_data=["origin_city", "destination_city"],
        color_discrete_sequence=CHART_COLORS
    )
    fig_scatter.update_layout(**{**PLOTLY_LAYOUT, "height": 270})
    fig_scatter.update_traces(marker=dict(line=dict(width=1, color='rgba(0,0,0,0.2)'), opacity=0.9))
    st.plotly_chart(fig_scatter, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── INSIGHTS ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Automated Insights</div>', unsafe_allow_html=True)
insights = generate_insights(df)
for insight in insights:
    st.markdown(f'<div class="insight-card">💡 {insight}</div>', unsafe_allow_html=True)

# ─── DATA TABLE ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Data Explorer</div>', unsafe_allow_html=True)
st.dataframe(df, width="stretch", hide_index=True)

# ─── CALL TO ACTION ───────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)

COMPANY_LOGO_PATH_BIG = "assets/weitblick_big.png"
logo_b64_big = get_logo_b64(COMPANY_LOGO_PATH_BIG) if COMPANY_LOGO_PATH_BIG else None

cta_logo_html = f'<img src="data:image/png;base64,{logo_b64_big}" alt="Weitblick Logo" />' if logo_b64_big else '<div class="cta-logo-placeholder">Your Logo</div>'

st.markdown(f'''<div class="cta-wrap">
<div class="cta-inner">
<div class="cta-logo-col">{cta_logo_html}</div>
<div class="cta-content-col">
<div class="cta-eyebrow"><span class="cta-eyebrow-dot"></span> Built by Weitblick &middot; Supply Chain Intelligence</div>
<div class="cta-heading">Ready to optimize your<br><span>supply chain operations?</span></div>
<div class="cta-subtext">This dashboard is a live demo of what Weitblick builds for logistics and supply chain teams. We design and deliver custom intelligence platforms tailored to your data, your KPIs, and your workflows.</div>
<div class="cta-buttons">
<a href="mailto:weitblick.contact@gmail.com" class="cta-btn-main">&#9993;&#65039;&nbsp; Get in Touch</a>
<a href="https://calendly.com/weitblick-contact/30min" target="_blank" class="cta-btn-main">&#128197;&nbsp; Book a Free Discovery Call</a>
</div>
<div class="cta-divider"></div>
<div class="cta-footer-row">
<div class="cta-trust-item"><span class="cta-trust-icon">&#9889;</span> Fast turnaround</div>
<div class="cta-trust-item"><span class="cta-trust-icon">&#128274;</span> Your data stays yours</div>
<div class="cta-trust-item"><span class="cta-trust-icon">&#127919;</span> Built to your exact specs</div>
<div class="cta-trust-item"><span class="cta-trust-icon">&#127758;</span> Remote-first, global clients</div>
</div>
</div>
</div>
</div>''', unsafe_allow_html=True)
