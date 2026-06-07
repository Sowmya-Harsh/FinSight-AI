# 💹 FinSight AI - Financial Intelligence Platform

An AI-powered financial intelligence platform with four modules: forecasting & anomaly detection, annual report analysis, credit risk scoring, and portfolio optimisation.

## Live Demo
👉 [Try it on Streamlit Cloud](#) *https://finsight-ai-3.streamlit.app/*

## Modules

### 📈 Forecasting & Anomaly Detection
- Upload any financial time series CSV
- Automatic anomaly detection with configurable sensitivity
- Polynomial trend forecasting with confidence intervals
- AI-generated insights and business recommendations

### 📄 Annual Report Analyser
- Upload any company annual report PDF
- Extracts KPIs: revenue, profit margin, debt/equity, ROE, and more
- Investment signal: Strong Buy / Buy / Hold / Sell / Strong Sell
- Financial health, growth, and risk scores
- Strengths, risks, opportunities, and analyst recommendation

### 🏦 Credit Risk Scorer
- Input company financials via interactive form
- Credit score (300–850) with rating (AAA to D)
- Probability of default and recommended lending rate
- Approve / Decline recommendation with conditions
- Financial ratio assessment

### 💼 Portfolio Optimiser
- Enter any assets (stocks, ETFs, bonds, commodities)
- Monte Carlo simulation (5,000 portfolios)
- Efficient frontier visualisation
- Conservative / Balanced / Aggressive risk profiles
- Dollar allocation breakdown with AI commentary

## Tech Stack
- **Frontend:** Streamlit
- **LLM:** Groq (LLaMA 3.3 70B)
- **Optimisation:** NumPy Monte Carlo simulation
- **Charts:** Plotly
- **PDF parsing:** PyPDF

## How it works:

- Forecasting: Rolling window Z-score for anomaly detection + polynomial regression for trend forecasting with 95% confidence intervals
- Report Analyser: PyPDF extracts text from annual report PDFs → chunked and sent to LLaMA 3.3 via Groq API → structured JSON response with KPIs, scores, signals
- Credit Risk: Rule-based financial ratio computation (debt/equity, current ratio, DSCR) + LLM reasoning layer for qualitative assessment and rating
- Portfolio: Monte Carlo simulation (5,000 portfolios) with mean-variance optimisation → efficient frontier → optimal allocation based on Sharpe ratio

## Run Locally

```bash
git clone https://github.com/Sowmya-Harsh/finsight-ai.git
cd finsight-ai
pip install -r requirements.txt
mkdir .streamlit
echo 'GROQ_API_KEY = "your_key_here"' > .streamlit/secrets.toml
streamlit run app.py
```

Get a free Groq API key at https://console.groq.com

## Deploy on Streamlit Cloud
1. Push to GitHub (public repo)
2. Go to share.streamlit.io
3. Select repo, main file: `app.py`
4. Add `GROQ_API_KEY` in secrets
5. Deploy!

## Project Structure
```
finsight-ai/
├── app.py                    # Main entry + navigation
├── modules/
│   ├── forecasting.py        # Module 1: Forecasting & Anomaly Detection
│   ├── report_analyser.py    # Module 2: Annual Report Analyser
│   ├── credit_risk.py        # Module 3: Credit Risk Scorer
│   └── portfolio.py          # Module 4: Portfolio Optimiser
├── utils/
│   └── groq_client.py        # Shared Groq API client
├── requirements.txt
└── README.md
```

## Disclaimer
For informational and demonstration purposes only. Not financial advice.

## Author
**Sowmya Janmahanthi**
- GitHub: [Sowmya-Harsh](https://github.com/Sowmya-Harsh)
- LinkedIn: [sowmyajanmahanthi](https://linkedin.com/in/sowmyajanmahanthi)
- Hugging Face: [sowmya4547](https://huggingface.co/sowmya4547)
