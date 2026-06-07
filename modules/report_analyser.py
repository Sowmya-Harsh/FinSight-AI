import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pypdf
import io
import json
import re
from utils.groq_client import get_client, ask_groq


def extract_pdf_text(uploaded_file, max_chars=15000) -> str:
    try:
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) >= max_chars:
                break
        return text[:max_chars]
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""


def analyse_report(client, company: str, text: str) -> dict:
    prompt = f"""You are a senior financial analyst. Analyse this annual report for {company} and return ONLY a JSON object:

REPORT:
{text}

Return ONLY this JSON, no other text:
{{
  "company": "{company}",
  "kpis": {{
    "revenue": "<value or N/A>",
    "revenue_growth": "<% or N/A>",
    "net_profit": "<value or N/A>",
    "profit_margin": "<% or N/A>",
    "ebitda": "<value or N/A>",
    "debt_to_equity": "<ratio or N/A>",
    "return_on_equity": "<% or N/A>",
    "current_ratio": "<ratio or N/A>"
  }},
  "financial_health_score": <0-100>,
  "growth_score": <0-100>,
  "risk_score": <0-100>,
  "investment_signal": "<one of: Strong Buy | Buy | Hold | Sell | Strong Sell>",
  "executive_summary": "<3-4 sentences overall assessment>",
  "key_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "key_risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
  "opportunities": ["<opportunity 1>", "<opportunity 2>", "<opportunity 3>"],
  "segment_performance": [
    {{"segment": "<name>", "performance": "<positive/neutral/negative>", "notes": "<brief note>"}}
  ],
  "analyst_recommendation": "<2-3 sentence recommendation with reasoning>"
}}"""

    raw = ask_groq(client, prompt, max_tokens=2048)
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            st.error("Could not parse report analysis.")
            return {}
    return {}


def signal_color(signal: str) -> str:
    colors = {
        "Strong Buy": "#1b5e20",
        "Buy": "#4caf50",
        "Hold": "#ff9800",
        "Sell": "#f44336",
        "Strong Sell": "#b71c1c"
    }
    return colors.get(signal, "#9e9e9e")


def render():
    st.markdown("## 📄 Annual Report Analyser")
    st.markdown("Upload any company annual report and get instant KPIs, investment signals, risk assessment, and analyst recommendations.")

    uploaded = st.file_uploader("Upload Annual Report (PDF)", type=["pdf"])
    company_name = st.text_input("Company name", placeholder="e.g. BNP Paribas")

    if st.button("Analyse Report", type="primary", use_container_width=True):
        if not uploaded or not company_name:
            st.warning("Please upload a PDF and enter the company name.")
            return

        with st.spinner("Reading and analysing report..."):
            text = extract_pdf_text(uploaded)
            if not text:
                st.error("Could not extract text from PDF.")
                return
            client = get_client()
            result = analyse_report(client, company_name, text)

        if not result:
            st.error("Analysis failed. Please try again.")
            return

        st.divider()

        # ── Investment signal ────────────────────────────────────────────────
        signal = result.get("investment_signal", "Hold")
        sig_color = signal_color(signal)
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:{sig_color}15;
             border: 2px solid {sig_color}; border-radius:12px; margin-bottom:20px">
            <h1 style="color:{sig_color}; margin:0">⚡ {signal}</h1>
            <p style="color:#666; margin:4px 0">Investment Signal for {company_name}</p>
        </div>""", unsafe_allow_html=True)

        # ── Score cards ──────────────────────────────────────────────────────
        st.markdown("### Scores")
        c1, c2, c3 = st.columns(3)
        scores = [
            (c1, "Financial Health", result.get("financial_health_score", 0), "#4caf50"),
            (c2, "Growth Potential", result.get("growth_score", 0), "#2196f3"),
            (c3, "Risk Level", result.get("risk_score", 0), "#f44336"),
        ]
        for col, label, score, color in scores:
            with col:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={"text": label, "font": {"size": 14}},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": color},
                        "steps": [
                            {"range": [0, 33], "color": "#ffebee"},
                            {"range": [33, 66], "color": "#fff8e1"},
                            {"range": [66, 100], "color": "#e8f5e9"},
                        ]
                    }
                ))
                fig.update_layout(height=220, margin=dict(t=40, b=0, l=20, r=20),
                                  paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)

        # ── KPIs ─────────────────────────────────────────────────────────────
        st.markdown("### 📊 Key Performance Indicators")
        kpis = result.get("kpis", {})
        kpi_cols = st.columns(4)
        kpi_items = list(kpis.items())
        for i, (key, val) in enumerate(kpi_items):
            with kpi_cols[i % 4]:
                label = key.replace("_", " ").title()
                st.metric(label, val if val != "N/A" else "—")

        st.divider()

        # ── Summary ──────────────────────────────────────────────────────────
        st.markdown("### 📝 Executive Summary")
        st.markdown(result.get("executive_summary", ""))

        # ── Strengths, Risks, Opportunities ─────────────────────────────────
        st.markdown("### Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**✅ Key Strengths**")
            for s in result.get("key_strengths", []):
                st.markdown(f"""<div style="background:#e8f5e9; border-left:4px solid #4caf50;
                    padding:8px 12px; border-radius:6px; margin:4px 0">{s}</div>""",
                    unsafe_allow_html=True)
        with col2:
            st.markdown("**⚠️ Key Risks**")
            for r in result.get("key_risks", []):
                st.markdown(f"""<div style="background:#fce4ec; border-left:4px solid #e91e63;
                    padding:8px 12px; border-radius:6px; margin:4px 0">{r}</div>""",
                    unsafe_allow_html=True)
        with col3:
            st.markdown("**🚀 Opportunities**")
            for o in result.get("opportunities", []):
                st.markdown(f"""<div style="background:#e3f2fd; border-left:4px solid #2196f3;
                    padding:8px 12px; border-radius:6px; margin:4px 0">{o}</div>""",
                    unsafe_allow_html=True)

        # ── Segment performance ──────────────────────────────────────────────
        segments = result.get("segment_performance", [])
        if segments:
            st.markdown("### 🏢 Segment Performance")
            perf_colors = {"positive": "#4caf50", "neutral": "#ff9800", "negative": "#f44336"}
            for seg in segments:
                color = perf_colors.get(seg.get("performance", "neutral"), "#9e9e9e")
                st.markdown(f"""<div style="border-left:4px solid {color}; padding:8px 12px;
                    background:{color}15; border-radius:6px; margin:4px 0">
                    <strong>{seg.get('segment', '')}</strong> — {seg.get('notes', '')}
                    </div>""", unsafe_allow_html=True)

        # ── Recommendation ───────────────────────────────────────────────────
        st.markdown("### 💡 Analyst Recommendation")
        st.info(result.get("analyst_recommendation", ""))

        st.caption("Disclaimer: This is AI-generated analysis for informational purposes only. Not financial advice.")
