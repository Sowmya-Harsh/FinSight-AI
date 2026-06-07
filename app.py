import streamlit as st

st.set_page_config(
    page_title="FinSight AI",
    page_icon="chart_with_upwards_trend",
    layout="wide"
)

# ── Styles — works in both light and dark mode ────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1a237e, #0d47a1, #1565c0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .main-subtitle {
        font-size: 1.05rem;
        color: var(--text-color);
        opacity: 0.7;
        margin-bottom: 2rem;
    }
    .module-card {
        background: transparent;
        border: 1px solid rgba(128,128,128,0.3);
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        transition: all 0.2s;
        height: 160px;
    }
    .module-card:hover {
        border-color: #1565c0;
        box-shadow: 0 4px 16px rgba(21,101,192,0.15);
    }
    .module-card h4 {
        color: var(--text-color);
        margin: 8px 0 6px 0;
        font-size: 1rem;
    }
    .module-card p {
        color: var(--text-color);
        opacity: 0.6;
        font-size: 0.88rem;
        margin: 0;
    }
    .module-icon {
        font-size: 1.6rem;
        margin-bottom: 4px;
    }
    .who-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 10px;
        padding: 16px;
        height: 100%;
    }
    .footer {
        text-align: center;
        opacity: 0.5;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(128,128,128,0.2);
    }
    .footer a { color: #1565c0; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">FinSight AI</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">A financial intelligence platform for forecasting, risk assessment, credit scoring, and portfolio optimisation — powered by AI.</div>', unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
MODULES = {
    "Home": "home",
    "Forecasting & Anomaly Detection": "forecasting",
    "Annual Report Analyser": "report",
    "Credit Risk Scorer": "credit",
    "Portfolio Optimiser": "portfolio",
}

selected = st.sidebar.radio(
    "Select Module",
    list(MODULES.keys()),
    index=0
)

module = MODULES[selected]

# ── Home page ─────────────────────────────────────────────────────────────────
if module == "home":
    st.markdown("### What can FinSight AI do?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="module-card">
            <div class="module-icon">&#x1F4C8;</div>
            <h4>Forecasting & Anomaly Detection</h4>
            <p>Upload any financial time series — get forecasts and automatic anomaly alerts</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="module-card">
            <div class="module-icon">&#x1F3E6;</div>
            <h4>Credit Risk Scorer</h4>
            <p>Input company financials and get a credit risk score, rating, and lending recommendation</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="module-card">
            <div class="module-icon">&#x1F4C4;</div>
            <h4>Annual Report Analyser</h4>
            <p>Upload any annual report PDF and get KPIs, investment signals, and analyst recommendations</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="module-card">
            <div class="module-icon">&#x1F4BC;</div>
            <h4>Portfolio Optimiser</h4>
            <p>Enter your assets and get an AI-optimised allocation with efficient frontier analysis</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Who is this for?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="who-card">
            <strong>Banks & Lenders</strong><br><br>
            Credit risk assessment, loan scoring, and financial health monitoring
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="who-card">
            <strong>Investment Firms</strong><br><br>
            Portfolio optimisation, annual report analysis, and market forecasting
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="who-card">
            <strong>Finance Teams</strong><br><br>
            Anomaly detection in financial data, forecasting, and risk monitoring
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        Built by <strong>Sowmya Janmahanthi</strong> &nbsp;·&nbsp;
        <a href="https://linkedin.com/in/sowmyajanmahanthi">LinkedIn</a> &nbsp;·&nbsp;
        <a href="https://github.com/Sowmya-Harsh">GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# ── Module routing ────────────────────────────────────────────────────────────
elif module == "forecasting":
    from modules.forecasting import render
    render()

elif module == "report":
    from modules.report_analyser import render
    render()

elif module == "credit":
    from modules.credit_risk import render
    render()

elif module == "portfolio":
    from modules.portfolio import render
    render()
