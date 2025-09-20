"""
app.py
======

This Streamlit application provides a user interface for the simplified
multi‑agent trading simulation implemented in `trading_agents.py`. It allows
engineers to experiment with different tickers and dates, observe how each
agent contributes to the final trading decision and persist the results in a
local SQLite database. The UI intentionally mirrors the workflow described in
the TradingAgents paper: analysts produce reports, researchers debate, the
trader makes a decision and the risk manager adjusts it.

Usage
-----

Run the app from a terminal with::

    streamlit run app.py

Ensure the required packages (`streamlit`, `pandas`, `numpy`) are installed in
your environment. Because this file is part of a demonstration package, the
code checks for missing dependencies and fails gracefully with a clear error
message.
"""

import datetime
from typing import List

try:
    import streamlit as st
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "streamlit must be installed to run this application. "
        "Install it with `pip install streamlit` and try again."
    )

from trading_agents import TradingAgentsGraph, AnalysisReport
import database


def format_report(report: AnalysisReport) -> str:
    """Format an AnalysisReport into a string for display."""
    lines = [f"**{report.title}**"]
    lines.append(report.summary)
    lines.append(f"Score: {report.score:.2f}")
    # Optionally show details in expandable section
    return "\n\n".join(lines)


def main() -> None:
    st.set_page_config(page_title="Multi‑Agent Trading Demo", layout="wide")
    st.title("TradingAgents Demo (Simplified)")
    st.markdown(
        "This application demonstrates a simplified multi‑agent trading system. "
        "Enter a stock ticker and a date, then click **Run Simulation** to see how "
        "fundamental, sentiment, news and technical analysts produce reports, how bull and "
        "bear researchers debate those reports and how a trader and risk manager arrive at a final decision."
    )

    # Initialise database table
    database.initialise_database()

    # Sidebar for simulation parameters
    st.sidebar.header("Simulation Parameters")
    ticker = st.sidebar.text_input("Ticker", value="AAPL")
    date = st.sidebar.date_input("Date", value=datetime.date.today())
    debate_rounds = st.sidebar.slider(
        "Number of Debate Rounds", min_value=1, max_value=5, value=1, step=1
    )
    show_logs = st.sidebar.checkbox("Show Detailed Logs", value=True)
    run_button = st.sidebar.button("Run Simulation")

    # Persistent TradingAgentsGraph instance for efficiency
    if "agent" not in st.session_state:
        st.session_state.agent = TradingAgentsGraph(debug=False)

    # Main column layout
    col1, col2 = st.columns(2)

    if run_button:
        with st.spinner("Running multi‑agent simulation..."):
            state, decision = st.session_state.agent.propagate(ticker=ticker, date=str(date))
        # Persist to DB
        database.insert_trade(decision)

        # Display final decision
        col1.subheader("Final Decision")
        col1.metric(
            label=f"{decision['action'].upper()} {decision['ticker']}",
            value=f"{decision['amount']:.0f} shares",
            delta="",
        )
        col1.write(decision["reason"])

        # Display agent reports and debate logs
        if show_logs:
            col2.subheader("Agent Reports")
            for report in state["reports"]:
                with col2.expander(report.title, expanded=False):
                    st.markdown(format_report(report))
            col2.subheader("Researcher Debate")
            bull_report = state["bull_report"]
            bear_report = state["bear_report"]
            with col2.expander("Bull Research", expanded=False):
                st.markdown(format_report(bull_report))
            with col2.expander("Bear Research", expanded=False):
                st.markdown(format_report(bear_report))
            col2.subheader("Trader & Risk Manager Logs")
            st.markdown(f"**Trader Reason:** {state['trader_reason']}")
            st.markdown(f"**Risk Reason:** {state['risk_reason']}")

    # Past trades table
    st.subheader("Trade History")
    trades = database.list_trades(limit=20)
    if trades:
        st.table(trades)
    else:
        st.info("No trades have been executed yet. Run a simulation to see results here.")


if __name__ == "__main__":  # pragma: no cover
    main()
