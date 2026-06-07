import streamlit as st

st.set_page_config(
    page_title="FinSight-AI",
    page_icon="💹",
    layout="wide"
)

# ── Styles ────────────────────────────────────────────────────────────────────
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
        color: #546e7a;
        margin-bottom: 2rem;
    }
    .module-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.2s;
        cursor: pointer;
        height: 160px;
    }
    .footer {
        text-align: center;
        color: #9e9e9e;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">💹 FinSight AI</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">A financial intelligence platform for forecasting, risk assessment, credit scoring, and portfolio optimisation — powered by AI.</div>', unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
MODULES = {
    "🏠 Home": "home",
    "📈 Forecasting & Anomaly Detection": "forecasting",
    "📄 Annual Report Analyser": "report",
    "🏦 Credit Risk Scorer": "credit",
    "💼 Portfolio Optimiser": "portfolio",
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
            <h2>📈</h2>
            <h4>Forecasting & Anomaly Detection</h4>
            <p style="color:#666; font-size:0.9rem">Upload any financial time series — get forecasts and automatic anomaly alerts</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="module-card">
            <h2>🏦</h2>
            <h4>Credit Risk Scorer</h4>
            <p style="color:#666; font-size:0.9rem">Input company financials and get a credit risk score, rating, and lending recommendation</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="module-card">
            <h2>📄</h2>
            <h4>Annual Report Analyser</h4>
            <p style="color:#666; font-size:0.9rem">Upload any annual report PDF and get KPIs, investment signals, and analyst recommendations</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="module-card">
            <h2>💼</h2>
            <h4>Portfolio Optimiser</h4>
            <p style="color:#666; font-size:0.9rem">Enter your assets and get an AI-optimised allocation with efficient frontier analysis</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Who is this for?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🏦 Banks & Lenders**
        Credit risk assessment, loan scoring, and financial health monitoring
        """)
    with col2:
        st.markdown("""
        **📊 Investment Firms**
        Portfolio optimisation, annual report analysis, and market forecasting
        """)
    with col3:
        st.markdown("""
        **🏢 Finance Teams**
        Anomaly detection in financial data, forecasting, and risk monitoring
        """)

    st.markdown("""
    <div class="footer">
        Built by <strong>Sowmya Janmahanthi</strong> ·
        <a href="https://linkedin.com/in/sowmyajanmahanthi">LinkedIn</a> ·
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
