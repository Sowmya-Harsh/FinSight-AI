import streamlit as st
import plotly.graph_objects as go
import json
import re
from utils.groq_client import get_client, ask_groq


def score_credit_risk(client, inputs: dict) -> dict:
    prompt = f"""You are a senior credit risk analyst at a major bank. Based on the following company financials, provide a credit risk assessment.

COMPANY FINANCIALS:
{json.dumps(inputs, indent=2)}

Return ONLY this JSON, no other text:
{{
  "credit_score": <300-850>,
  "rating": "<one of: AAA | AA | A | BBB | BB | B | CCC | D>",
  "risk_level": "<one of: Very Low | Low | Moderate | High | Very High>",
  "probability_of_default": "<% e.g. 2.3%>",
  "recommended_loan_rate": "<% e.g. 4.5%>",
  "max_recommended_credit": "<e.g. $5M>",
  "overall_assessment": "<3-4 sentence summary>",
  "positive_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
  "risk_factors": ["<risk 1>", "<risk 2>", "<risk 3>"],
  "financial_ratios": {{
    "debt_to_equity_assessment": "<healthy/moderate/concerning>",
    "liquidity_assessment": "<strong/adequate/weak>",
    "profitability_assessment": "<strong/moderate/weak>",
    "coverage_assessment": "<strong/adequate/weak>"
  }},
  "recommendation": "<one of: Approve | Approve with Conditions | Further Review Required | Decline>",
  "conditions": ["<condition if any>"]
}}"""

    raw = ask_groq(client, prompt, max_tokens=1500)
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            return {}
    return {}


def render():
    st.markdown("## 🏦 Credit Risk Scorer")
    st.markdown("Input company financials to get an AI-powered credit risk assessment, rating, and lending recommendation.")

    st.markdown("### Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. Acme Corp")
        industry = st.selectbox("Industry", [
            "Technology", "Finance & Banking", "Manufacturing",
            "Retail & Consumer", "Healthcare", "Energy",
            "Real Estate", "Construction", "Agriculture", "Other"
        ])
        years_operating = st.number_input("Years in Operation", min_value=0, max_value=200, value=5)
        employees = st.number_input("Number of Employees", min_value=1, value=100)

    with col2:
        country = st.text_input("Country", placeholder="e.g. Luxembourg")
        company_type = st.selectbox("Company Type", [
            "Public Listed", "Private Limited", "SME", "Startup", "Subsidiary"
        ])
        credit_history = st.selectbox("Credit History", [
            "Excellent — no defaults", "Good — minor delays",
            "Fair — some defaults", "Poor — multiple defaults", "No history"
        ])

    st.markdown("### Financial Data (Annual)")
    col1, col2, col3 = st.columns(3)
    with col1:
        revenue = st.number_input("Annual Revenue ($)", min_value=0, value=1000000, step=10000,
                                   format="%d")
        net_profit = st.number_input("Net Profit ($)", value=100000, step=1000, format="%d")
        total_assets = st.number_input("Total Assets ($)", min_value=0, value=2000000, step=10000,
                                        format="%d")

    with col2:
        total_debt = st.number_input("Total Debt ($)", min_value=0, value=500000, step=10000,
                                      format="%d")
        total_equity = st.number_input("Total Equity ($)", min_value=1, value=1500000, step=10000,
                                        format="%d")
        current_assets = st.number_input("Current Assets ($)", min_value=0, value=800000,
                                          step=10000, format="%d")

    with col3:
        current_liabilities = st.number_input("Current Liabilities ($)", min_value=0,
                                               value=300000, step=10000, format="%d")
        ebitda = st.number_input("EBITDA ($)", value=200000, step=1000, format="%d")
        loan_requested = st.number_input("Loan Amount Requested ($)", min_value=0,
                                          value=500000, step=10000, format="%d")

    st.markdown("### Additional Context")
    additional_info = st.text_area(
        "Any additional context (optional)",
        placeholder="e.g. Company recently secured a major contract, expanding to new markets...",
        height=80
    )

    if st.button("Assess Credit Risk", type="primary", use_container_width=True):
        if not company_name:
            st.warning("Please enter the company name.")
            return

        inputs = {
            "company": company_name,
            "industry": industry,
            "country": country,
            "years_operating": years_operating,
            "employees": employees,
            "company_type": company_type,
            "credit_history": credit_history,
            "annual_revenue": revenue,
            "net_profit": net_profit,
            "profit_margin_pct": round(net_profit / revenue * 100, 2) if revenue > 0 else 0,
            "total_assets": total_assets,
            "total_debt": total_debt,
            "total_equity": total_equity,
            "debt_to_equity_ratio": round(total_debt / total_equity, 2) if total_equity > 0 else 0,
            "current_assets": current_assets,
            "current_liabilities": current_liabilities,
            "current_ratio": round(current_assets / current_liabilities, 2) if current_liabilities > 0 else 0,
            "ebitda": ebitda,
            "debt_service_coverage": round(ebitda / total_debt, 2) if total_debt > 0 else 0,
            "loan_requested": loan_requested,
            "additional_context": additional_info
        }

        with st.spinner("Running credit risk assessment..."):
            client = get_client()
            result = score_credit_risk(client, inputs)

        if not result:
            st.error("Assessment failed. Please try again.")
            return

        st.divider()

        # ── Credit score gauge ───────────────────────────────────────────────
        score = result.get("credit_score", 500)
        risk_level = result.get("risk_level", "Moderate")
        rating = result.get("rating", "BBB")
        recommendation = result.get("recommendation", "Further Review Required")

        rec_colors = {
            "Approve": "#4caf50",
            "Approve with Conditions": "#8bc34a",
            "Further Review Required": "#ff9800",
            "Decline": "#f44336"
        }
        rec_color = rec_colors.get(recommendation, "#9e9e9e")

        # recommendation banner
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:{rec_color}15;
             border: 2px solid {rec_color}; border-radius:12px; margin-bottom:20px">
            <h1 style="color:{rec_color}; margin:0">📋 {recommendation}</h1>
            <p style="color:#666; margin:4px 0">Credit Decision for {company_name}</p>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Credit Score", "font": {"size": 16}},
                gauge={
                    "axis": {"range": [300, 850]},
                    "bar": {"color": "#1f77b4"},
                    "steps": [
                        {"range": [300, 500], "color": "#ffebee"},
                        {"range": [500, 650], "color": "#fff8e1"},
                        {"range": [650, 750], "color": "#e8f5e9"},
                        {"range": [750, 850], "color": "#1b5e20"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": score
                    }
                }
            ))
            fig.update_layout(height=280, margin=dict(t=40, b=0), paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Key Metrics")
            m1, m2 = st.columns(2)
            m1.metric("Rating", rating)
            m2.metric("Risk Level", risk_level)
            m1.metric("Default Probability", result.get("probability_of_default", "N/A"))
            m2.metric("Recommended Rate", result.get("recommended_loan_rate", "N/A"))
            st.metric("Max Recommended Credit", result.get("max_recommended_credit", "N/A"))

        st.divider()

        # ── Assessment ───────────────────────────────────────────────────────
        st.markdown("### 📝 Overall Assessment")
        st.markdown(result.get("overall_assessment", ""))

        # ── Factors ─────────────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Positive Factors**")
            for f in result.get("positive_factors", []):
                st.markdown(f"""<div style="background:#e8f5e9; border-left:4px solid #4caf50;
                    padding:8px 12px; border-radius:6px; margin:4px 0">{f}</div>""",
                    unsafe_allow_html=True)
        with col2:
            st.markdown("**⚠️ Risk Factors**")
            for f in result.get("risk_factors", []):
                st.markdown(f"""<div style="background:#fce4ec; border-left:4px solid #e91e63;
                    padding:8px 12px; border-radius:6px; margin:4px 0">{f}</div>""",
                    unsafe_allow_html=True)

        # ── Financial ratio assessment ───────────────────────────────────────
        st.markdown("### 📊 Financial Ratio Assessment")
        ratios = result.get("financial_ratios", {})
        ratio_cols = st.columns(4)
        ratio_items = [
            ("Debt/Equity", ratios.get("debt_to_equity_assessment", "N/A")),
            ("Liquidity", ratios.get("liquidity_assessment", "N/A")),
            ("Profitability", ratios.get("profitability_assessment", "N/A")),
            ("Coverage", ratios.get("coverage_assessment", "N/A")),
        ]
        assessment_colors = {
            "healthy": "#4caf50", "strong": "#4caf50",
            "moderate": "#ff9800", "adequate": "#ff9800",
            "concerning": "#f44336", "weak": "#f44336"
        }
        for col, (label, val) in zip(ratio_cols, ratio_items):
            with col:
                color = assessment_colors.get(val.lower(), "#9e9e9e")
                st.markdown(f"""<div style="text-align:center; padding:12px;
                    border:1px solid {color}; border-radius:8px; border-top: 4px solid {color}">
                    <p style="color:#666; margin:0; font-size:0.85rem">{label}</p>
                    <h4 style="color:{color}; margin:4px 0; text-transform:capitalize">{val}</h4>
                    </div>""", unsafe_allow_html=True)

        # ── Conditions ───────────────────────────────────────────────────────
        conditions = result.get("conditions", [])
        if conditions and conditions[0]:
            st.markdown("### 📋 Conditions / Requirements")
            for c in conditions:
                st.markdown(f"- {c}")

        st.caption("Disclaimer: AI-generated assessment for informational purposes only. Not a substitute for professional credit analysis.")
