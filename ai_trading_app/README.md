# TradingAgents Streamlit Demo

This repository contains a hands‑on Streamlit application that demonstrates
the core ideas behind **TradingAgents**, a multi‑agent large language model
(LLM) trading framework introduced by researchers at UCLA and MIT. The
original paper proposes a system where specialised LLM agents—fundamental
analysts, sentiment analysts, news analysts, technical analysts, researchers,
traders and risk managers—collaborate to make trading decisions. The
framework uses structured communication and debate to mimic the workflows of
real hedge funds and reports superior performance compared with buy–and–hold
and rule‑based strategies【639543415264422†L114-L124】【639543415264422†L189-L198】.  

While the original implementation relies on advanced libraries such as
LangGraph and integrates with external data providers, this demo keeps the
dependencies minimal. It generates synthetic market data, runs simple agent
logic and stores results in a local SQLite database. The goal is to help AI
engineers explore the architecture and experiment with extensions without
needing API keys or proprietary services.

## Features

* **Agent Specialisation:** Four analyst roles (fundamental, sentiment, news and
  technical) process different aspects of the synthetic data and produce
  structured reports. This mirrors the paper’s recommendation to break down
  complex tasks into specialised agents【639543415264422†L114-L124】.
* **Researcher Debate:** Bull and bear researchers summarise positive and
  negative aspects of the analyst reports, reflecting the dialectical process
  described in the paper【639543415264422†L189-L198】.
* **Trader and Risk Manager:** A trader agent aggregates the debate and decides
  whether to buy, sell or hold. A risk manager adjusts the position size based
  on volatility, emulating the risk‑control step emphasised in the research.
* **Streamlit Interface:** A simple web UI lets you enter a ticker and date,
  run the simulation, view agent logs and see past trades stored in a SQLite
  database. Toggle detailed logs to explore how each agent contributes to the
  final decision.

## Getting Started

1. **Install dependencies:** You need Python 3.11 and the following packages:
   `streamlit`, `pandas` and `numpy`. If you want to replicate the full
   TradingAgents workflow with real LLMs and market data you’ll also need
   `langchain` and `langgraph`, but they are not required for this demo.

   ```bash
   pip install streamlit pandas numpy
   ```

2. **Run the app:** From within the `ai_trading_app` directory execute:

   ```bash
   streamlit run app.py
   ```

3. **Interact:** In your browser you’ll see controls to select a ticker and
   date and to run the simulation. Each run generates synthetic data, so
   results will vary slightly. The trade history section shows previous
   decisions saved to `trades.db`.

## Extending the Demo

This project is intentionally simple to encourage experimentation. Here are
some ideas for extending it:

* **Real Data:** Replace the synthetic data generator in
  `trading_agents.generate_sample_market_data` with calls to a real
  data provider such as FinnHub or Alpha Vantage. You can then compute
  technical indicators on actual price series.
* **LLM Integration:** Swap the simple scoring logic for calls to real LLMs
  via the OpenAI API or other providers. LangChain and LangGraph can help
  orchestrate multi‑agent workflows and maintain state across steps.
* **Custom Agents:** Add your own agent classes to incorporate machine
  learning predictors or domain‑specific analysis. The modular design makes
  it straightforward to plug in new roles.
* **Backtesting:** Implement a loop over multiple dates and tickers to
  simulate a portfolio and compute metrics like cumulative return and Sharpe
  ratio, as done in the TradingAgents paper【639543415264422†L769-L884】.

## Disclaimer

This application is for educational and research purposes only. It does not
constitute financial advice. The synthetic data and simplified agent logic
should not be used for real trading decisions.
