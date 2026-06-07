import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import re
from utils.groq_client import get_client, ask_groq


def generate_mock_returns(assets: list, days: int = 252) -> pd.DataFrame:
    """Generate synthetic return data for demonstration when no real data available."""
    np.random.seed(42)
    data = {}
    for asset in assets:
        daily_return = np.random.normal(0.0005, 0.02, days)
        data[asset] = daily_return
    return pd.DataFrame(data)


def optimise_portfolio(returns_df: pd.DataFrame, risk_tolerance: str) -> dict:
    """Mean-variance optimisation using Monte Carlo simulation."""
    n_assets = len(returns_df.columns)
    n_portfolios = 5000

    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()

    results = np.zeros((3, n_portfolios))
    weights_record = []

    for i in range(n_portfolios):
        weights = np.random.random(n_assets)
        weights /= np.sum(weights)
        weights_record.append(weights)

        portfolio_return = np.sum(mean_returns * weights) * 252
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
        sharpe = portfolio_return / portfolio_std if portfolio_std > 0 else 0

        results[0, i] = portfolio_std
        results[1, i] = portfolio_return
        results[2, i] = sharpe

    # select based on risk tolerance
    if risk_tolerance == "Conservative":
        idx = np.argmin(results[0])  # min volatility
    elif risk_tolerance == "Aggressive":
        idx = np.argmax(results[1])  # max return
    else:
        idx = np.argmax(results[2])  # max sharpe

    optimal_weights = weights_record[idx]
    return {
        "weights": dict(zip(returns_df.columns, [round(w * 100, 2) for w in optimal_weights])),
        "expected_return": round(results[1, idx] * 100, 2),
        "volatility": round(results[0, idx] * 100, 2),
        "sharpe_ratio": round(results[2, idx], 3),
        "all_returns": results[1].tolist(),
        "all_vols": results[0].tolist(),
        "all_sharpes": results[2].tolist(),
        "optimal_idx": int(idx)
    }


def get_ai_commentary(client, assets: list, weights: dict, metrics: dict, risk_tolerance: str) -> str:
    prompt = f"""As a portfolio manager, provide a concise analysis of this optimised portfolio:

Assets: {assets}
Optimal Allocation: {json.dumps(weights)}
Expected Annual Return: {metrics['expected_return']}%
Annual Volatility: {metrics['volatility']}%
Sharpe Ratio: {metrics['sharpe_ratio']}
Risk Tolerance: {risk_tolerance}

Provide 4-5 bullet points covering: allocation rationale, risk-return profile, diversification assessment, and recommendations."""

    return ask_groq(client, prompt,
                    system="You are a senior portfolio manager. Be specific and actionable.",
                    max_tokens=600)


def render():
    st.markdown("##  Portfolio Optimiser")
    st.markdown("Enter your assets and investment amount to get an AI-optimised portfolio allocation with risk-return analysis.")

    # inputs
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Assets")
        assets_input = st.text_area(
            "Enter asset names (one per line)",
            value="Apple (AAPL)\nMicrosoft (MSFT)\nGoogle (GOOGL)\nTesla (TSLA)\nGold ETF\nUS Treasury Bonds",
            height=150,
            help="Enter stocks, ETFs, bonds, or any asset class"
        )
    with col2:
        st.markdown("### Parameters")
        investment = st.number_input("Total Investment ($)", min_value=1000,
                                      value=100000, step=1000, format="%d")
        risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Balanced", "Aggressive"])
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CHF"])

    st.info("Note: Portfolio optimisation uses Monte Carlo simulation with synthetic return data for demonstration. For real portfolios, connect to a market data API.")

    if st.button("Optimise Portfolio", type="primary", use_container_width=True):
        assets = [a.strip() for a in assets_input.strip().split("\n") if a.strip()]

        if len(assets) < 2:
            st.warning("Please enter at least 2 assets.")
            return
        if len(assets) > 15:
            st.warning("Maximum 15 assets supported.")
            return

        with st.spinner("Running Monte Carlo optimisation..."):
            returns_df = generate_mock_returns(assets)
            result = optimise_portfolio(returns_df, risk_tolerance)

        with st.spinner("Generating AI commentary..."):
            client = get_client()
            commentary = get_ai_commentary(
                client, assets, result["weights"],
                {"expected_return": result["expected_return"],
                 "volatility": result["volatility"],
                 "sharpe_ratio": result["sharpe_ratio"]},
                risk_tolerance
            )

        st.divider()

        #  Key metrics 
        st.markdown("###  Optimised Portfolio Metrics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Expected Annual Return", f"{result['expected_return']}%")
        c2.metric("Annual Volatility", f"{result['volatility']}%")
        c3.metric("Sharpe Ratio", f"{result['sharpe_ratio']}")
        c4.metric("Risk Profile", risk_tolerance)

        st.divider()

        #  Allocation charts 
        st.markdown("###  Optimal Allocation")
        weights = result["weights"]
        col1, col2 = st.columns(2)

        with col1:
            # pie chart
            fig_pie = go.Figure(go.Pie(
                labels=list(weights.keys()),
                values=list(weights.values()),
                hole=0.4,
                textinfo="label+percent",
            ))
            fig_pie.update_layout(
                title="Portfolio Allocation",
                height=400, paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # bar chart with dollar amounts
            dollar_amounts = {k: round(v / 100 * investment, 2) for k, v in weights.items()}
            fig_bar = go.Figure(go.Bar(
                x=list(weights.keys()),
                y=list(dollar_amounts.values()),
                marker_color=px.colors.qualitative.Set2,
                text=[f"{currency} {v:,.0f}" for v in dollar_amounts.values()],
                textposition="outside"
            ))
            fig_bar.update_layout(
                title=f"Dollar Allocation ({currency})",
                height=400, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis_title=f"Amount ({currency})",
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        #  Allocation table 
        st.markdown("###  Allocation Details")
        alloc_df = pd.DataFrame({
            "Asset": list(weights.keys()),
            "Weight (%)": list(weights.values()),
            f"Amount ({currency})": [f"{v / 100 * investment:,.2f}" for v in weights.values()]
        }).sort_values("Weight (%)", ascending=False)
        st.dataframe(alloc_df, use_container_width=True, hide_index=True)

        #  Efficient frontier 
        st.markdown("###  Efficient Frontier")
        vols = result["all_vols"]
        rets = result["all_returns"]
        sharpes = result["all_sharpes"]
        opt_idx = result["optimal_idx"]

        fig_ef = go.Figure()
        fig_ef.add_trace(go.Scatter(
            x=[v * 100 for v in vols],
            y=[r * 100 for r in rets],
            mode="markers",
            marker=dict(
                color=sharpes, colorscale="Viridis",
                size=3, opacity=0.5,
                colorbar=dict(title="Sharpe Ratio")
            ),
            name="Portfolios"
        ))
        fig_ef.add_trace(go.Scatter(
            x=[vols[opt_idx] * 100],
            y=[rets[opt_idx] * 100],
            mode="markers",
            marker=dict(color="red", size=15, symbol="star"),
            name="Optimal Portfolio"
        ))
        fig_ef.update_layout(
            title="Efficient Frontier — 5,000 Simulated Portfolios",
            xaxis_title="Volatility (%)",
            yaxis_title="Expected Return (%)",
            height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_ef, use_container_width=True)

        #  AI commentary 
        st.markdown("###  Portfolio Manager Commentary")
        st.markdown(commentary)

        st.caption("Disclaimer: For informational purposes only. Not financial advice. Past performance does not guarantee future results.")
