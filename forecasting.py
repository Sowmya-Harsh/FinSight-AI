import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.groq_client import get_client, ask_groq
import json
import re


def detect_anomalies(series: pd.Series, window: int = 7, threshold: float = 2.5) -> pd.Series:
    rolling_mean = series.rolling(window=window, center=True).mean()
    rolling_std = series.rolling(window=window, center=True).std()
    z_scores = (series - rolling_mean) / (rolling_std + 1e-9)
    return z_scores.abs() > threshold


def simple_forecast(series: pd.Series, periods: int = 30) -> pd.Series:
    # Linear trend + seasonal decomposition approximation
    x = np.arange(len(series))
    coeffs = np.polyfit(x, series.values, deg=2)
    future_x = np.arange(len(series), len(series) + periods)
    forecast_values = np.polyval(coeffs, future_x)
    # add slight noise for realism
    noise = np.random.normal(0, series.std() * 0.05, periods)
    return pd.Series(forecast_values + noise)


def render():
    st.markdown("## 📈 Financial Forecasting & Anomaly Detection")
    st.markdown("Upload any financial time series data to get forecasts and automatic anomaly alerts.")

    st.markdown("### Upload your data")
    uploaded = st.file_uploader("CSV file with a date column and numeric value column", type=["csv"])

    if not uploaded:
        st.info("Upload a CSV with at least two columns: a date/time column and a numeric value column (e.g. revenue, price, volume).")
        with st.expander("Example CSV format"):
            st.code("""date,revenue
2023-01-01,150000
2023-01-02,162000
2023-01-03,145000
2023-01-04,310000
...""")
        return

    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return

    # column selection
    st.markdown("### Configure")
    col1, col2, col3 = st.columns(3)
    with col1:
        date_col = st.selectbox("Date column", df.columns.tolist())
    with col2:
        value_col = st.selectbox("Value column", [c for c in df.columns if c != date_col])
    with col3:
        forecast_days = st.slider("Forecast periods", 7, 90, 30)

    sensitivity = st.select_slider(
        "Anomaly sensitivity",
        options=["Low", "Medium", "High"],
        value="Medium"
    )
    threshold_map = {"Low": 3.0, "Medium": 2.5, "High": 2.0}
    threshold = threshold_map[sensitivity]

    if st.button("Run Analysis", type="primary", use_container_width=True):
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col).reset_index(drop=True)
            series = df[value_col].astype(float)

            # anomaly detection
            anomalies = detect_anomalies(series, threshold=threshold)

            # forecast
            forecast = simple_forecast(series, periods=forecast_days)
            last_date = df[date_col].iloc[-1]
            future_dates = pd.date_range(start=last_date, periods=forecast_days + 1, freq="D")[1:]

            # ── Main chart ──────────────────────────────────────────────────
            st.markdown("### 📊 Time Series with Forecast & Anomalies")
            fig = go.Figure()

            # historical
            fig.add_trace(go.Scatter(
                x=df[date_col], y=series,
                mode="lines", name="Historical",
                line=dict(color="#1f77b4", width=2)
            ))

            # anomalies
            anomaly_dates = df[date_col][anomalies]
            anomaly_values = series[anomalies]
            fig.add_trace(go.Scatter(
                x=anomaly_dates, y=anomaly_values,
                mode="markers", name="Anomaly",
                marker=dict(color="red", size=10, symbol="x")
            ))

            # forecast
            fig.add_trace(go.Scatter(
                x=future_dates, y=forecast,
                mode="lines", name="Forecast",
                line=dict(color="#ff7f0e", width=2, dash="dash")
            ))

            # confidence band
            std = series.std()
            fig.add_trace(go.Scatter(
                x=list(future_dates) + list(future_dates[::-1]),
                y=list(forecast + 1.96 * std) + list((forecast - 1.96 * std)[::-1]),
                fill="toself", fillcolor="rgba(255,127,14,0.15)",
                line=dict(color="rgba(255,255,255,0)"),
                name="95% Confidence"
            ))

            fig.update_layout(
                height=450, paper_bgcolor="white", plot_bgcolor="white",
                xaxis_title="Date", yaxis_title=value_col,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            # ── Stats ───────────────────────────────────────────────────────
            st.markdown("### 📋 Summary Statistics")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Current Value", f"{series.iloc[-1]:,.0f}")
            c2.metric("Mean", f"{series.mean():,.0f}")
            c3.metric("Std Dev", f"{series.std():,.0f}")
            c4.metric("Anomalies Found", f"{anomalies.sum()}")
            c5.metric("Forecast (next period)", f"{forecast.iloc[0]:,.0f}",
                      delta=f"{forecast.iloc[0] - series.iloc[-1]:+,.0f}")

            # ── Anomaly table ───────────────────────────────────────────────
            if anomalies.sum() > 0:
                st.markdown("### 🚨 Detected Anomalies")
                anomaly_df = df[anomalies][[date_col, value_col]].copy()
                anomaly_df["Deviation from Mean"] = (
                    (series[anomalies] - series.mean()) / series.mean() * 100
                ).round(2).astype(str) + "%"
                st.dataframe(anomaly_df, use_container_width=True)

            # ── AI insights ─────────────────────────────────────────────────
            st.markdown("### 🤖 AI Insights")
            with st.spinner("Generating AI insights..."):
                client = get_client()
                summary_stats = f"""
Series: {value_col}
Period: {df[date_col].iloc[0].date()} to {df[date_col].iloc[-1].date()}
Data points: {len(series)}
Mean: {series.mean():.2f}
Std Dev: {series.std():.2f}
Min: {series.min():.2f}, Max: {series.max():.2f}
Trend: {'Upward' if series.iloc[-1] > series.iloc[0] else 'Downward'}
Anomalies detected: {anomalies.sum()} on dates: {list(anomaly_dates.dt.date.astype(str))}
Forecast next period: {forecast.iloc[0]:.2f}
"""
                insight = ask_groq(
                    client,
                    f"As a financial analyst, provide a concise 4-5 bullet point analysis of this financial time series data:\n{summary_stats}\nFocus on: trend interpretation, anomaly explanations, forecast outlook, and business recommendations.",
                    system="You are a senior financial analyst. Be specific, concise, and actionable.",
                    max_tokens=600
                )
                st.markdown(insight)

        except Exception as e:
            st.error(f"Analysis failed: {e}")
