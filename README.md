# Portfolio Optimization & Backtesting Web App (S&P 500 + Bonds) 📊🇺🇸

An interactive **Streamlit Web App** designed to teach investment and portfolio theory through real-world simulations and historical data. Users can explore how different models allocate portfolios using **S&P 500 stocks**, **US government bonds**, and **US corporate bonds**, and analyze how those portfolios would have performed over time.

---

## 🎯 Educational Goals
- Understand different portfolio optimization strategies.
- Simulate investment decisions in past years.
- Compare models and explore real data interactively.
- Visualize allocation, risk, and return across time.

---

## 📌 Core Features

### ✅ Asset Universe
- **S&P 500 Stocks** (via `yfinance` or static CSV).
- **US Government Bonds** (e.g., SHY, IEF, TLT).
- **US Corporate Bonds** (e.g., LQD, HYG).

### ✅ Optimization Models
- **Modern Portfolio Theory (Efficient Frontier)**.
- **Minimum Variance Portfolio (MVP)**.
- **Maximum Sharpe Ratio Portfolio (MSR)**.
- **Equal-weighted Portfolio**.
- **Risk Parity**.
- **Hierarchical Risk Parity (HRP)**.

### ✅ Backtesting & Time Controls
- Select **Investment Year** (e.g., 2010, 2015, 2020…).
- Choose **Training Window** (e.g., 10, 20, 30 years).
- Simulate portfolio performance up to today.

### ✅ Interactive UI (Streamlit Widgets)
- **Dropdown**: Select Optimization Model.
- **Slider**: Set Investment Start Year.
- **Slider**: Define Training Window (years).
- **Toggle**: Include Risk-Free Asset.
- **Dropdown**: Rebalancing Frequency (Monthly, Quarterly, Yearly, None).

---

## 📊 Visualizations
- **Efficient Frontier Plot** (interactive hover via Plotly).
- **Portfolio Allocation Pie Chart**.
- **Portfolio Performance Over Time**.
- **Rolling Volatility and Rolling Sharpe Ratio**.
- **Risk vs Return Scatter by Model**.
- **Side-by-Side Model Allocation Comparisons**.

---

## 💡 Advanced Educational Add-Ons
### 🧪 Custom Constraints
- Max allocation per asset (slider).
- Min allocation to bonds or equities.
- No short-selling toggle.
- ESG filter (stretch goal).

### 📚 Model Explanation Panels
- Expandable sections or tooltips explaining:
  - What the selected model does.
  - Why allocations change with time or data.
  - Historical context (e.g., Fed rates in 2010).

### 📈 Rolling Window Analysis
- Track changes in:
  - Sharpe Ratio.
  - Volatility.
  - Portfolio allocation.

### 🔁 Rebalancing Strategy Options
- Buy & Hold.
- Rebalance Monthly, Quarterly, or Annually.

### 🌍 Economic Context Panel (Optional)
- Show Fed Funds Rate, Inflation, and GDP at the time of investment using static data or `fredapi`.

### 📥 Export Options
- Download portfolio allocations as `.csv`.
- Export summary report (PDF or Markdown) with allocations, charts, and backtest results.

---

## 🗂️ Suggested Folder Structure
```
portfolio-optimization/
├── data/               # Cached or downloaded asset data
├── app/                # Streamlit app files
│   └── main.py
├── optimization/       # Python modules for each model (MPT, HRP, etc.)
├── backtesting/        # Portfolio simulation, rebalancing logic
├── utils/              # Data loaders, S&P 500 list, helper functions
├── requirements.txt
└── README.md
```

---

## 📦 Suggested Dependencies
```bash
streamlit
yfinance
pandas
numpy
matplotlib
seaborn
scipy
PyPortfolioOpt
cvxpy
riskfolio-lib
plotly
```

---

## 🚀 Getting Started Instructions
```bash
# Clone the repository
git clone https://github.com/PietroWei/portfolio-optimization.git

# Navigate to the project directory
cd portfolio-optimization

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app/main.py