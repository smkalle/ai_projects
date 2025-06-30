# Nancy Pelosi Portfolio Optimisation – README

This repository contains:

| File | Description |
|------|-------------|
| `nancy_pelosi_portfolio_optimization.ipynb` | Jupyter notebook with end‑to‑end analysis & optimisation |
| `nancy_pelosi_portfolio_optimization_tutorial.md` | This step‑by‑step guide (you are reading it!) |

---

## 📖 Overview
A viral X (Twitter) thread claimed that an *“optimised Pelosi portfolio”* could yield **1400 %** total return.  
This project recreates a **simplified** workflow to:

1. 🎯 **Fetch** historical price data for a Pelosi‑style basket of stocks  
2. 📊 **Compute** returns & risk metrics  
3. 🧮 **Optimise** portfolio weights via Monte‑Carlo to maximise Sharpe Ratio  
4. 📈 **Visualise** the efficient frontier & growth path  
5. ⚖️ **Discuss** ethics & limitations of analysing political trades  

## 🛠️ Prerequisites
```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy pandas yfinance matplotlib notebook
```

## 🚀 Quick‑Start
```bash
git clone <YOUR_FORK_URL> pelosi-portfolio
cd pelosi-portfolio
jupyter notebook nancy_pelosi_portfolio_optimization.ipynb
```

Follow the numbered sections in the notebook:

| Section | Purpose |
|---------|---------|
| 1️⃣ Parameters | Customise stock list, dates & assumptions |
| 2️⃣ Data Fetch | Download daily prices via Yahoo Finance |
| 3️⃣ Returns | Calculate log‑returns & annualise |
| 4️⃣ Helpers | Support functions |
| 5️⃣ Optimisation | Monte‑Carlo search for maximum Sharpe |
| 6️⃣ Frontier | Plot risk/return trade‑off |
| 7️⃣ Growth | Simulate $100 k investment |

## 📂 File Structure
```
.
├── nancy_pelosi_portfolio_optimization.ipynb
├── nancy_pelosi_portfolio_optimization_tutorial.md
└── README.md  (→ duplicate of this file)
```

## 🧑‍⚖️ Ethics & Legal
- The **STOCK Act (2012)** mandates disclosure but insider trading rules apply; enforcement is debated.  
- This repository is for **educational research** only – *no investment recommendations*.

## 📜 Licence
MIT
