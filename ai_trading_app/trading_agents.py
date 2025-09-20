"""
trading_agents.py
==================

This module implements a simplified version of the multi‑agent stock trading
framework described in the TradingAgents research paper. The goal of this
implementation is to demonstrate, in a hands‑on way, how one might architect a
multi‑agent system for financial trading using Python. Rather than relying on
external services or proprietary APIs, the agents defined here operate on
randomly generated data to illustrate the flow of information and the
collaborative decision making described in the paper.

Key ideas from the paper reflected in this module include:

* **Agent specialization** – distinct classes are defined for fundamental, sentiment,
  news and technical analysis. Each agent processes its own slice of the data
  and produces a structured report summarising its findings. The paper notes
  that assigning specific roles to LLM agents, such as fundamentals, sentiment
  and technical analysts, allows complex trading objectives to be broken down
  into manageable tasks【639543415264422†L114-L124】. Our implementation follows
  the same philosophy.
* **Researcher debate** – bullish and bearish researcher roles interpret the
  analysts' reports and formulate opposing viewpoints. The paper points out
  that a dialectical process between bull and bear researchers ensures balanced
  analysis, highlighting opportunities and risks【639543415264422†L189-L198】. In
  this module the debate is simplified to numerical scoring, but it captures
  the idea of weighing positive and negative evidence.
* **Decision and risk management** – a Trader agent synthesises the research
  arguments and proposes a buy/sell/hold decision. A RiskManager then adjusts
  the trade based on volatility, aligning with the paper's emphasis on
  controlling risk through a dedicated risk management team【639543415264422†L189-L198】.

Because this code is designed to run in constrained environments, it does not
depend on external libraries such as LangChain or LangGraph. Instead, it
implements a lightweight orchestration pattern directly in Python. Users who
have access to those libraries can replace the simple orchestration with
LangGraph workflows; however, the logic will remain the same.
"""

from __future__ import annotations

import datetime
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Data generation utilities
# ---------------------------------------------------------------------------

def generate_sample_market_data(days: int = 60, start_price: float = 100.0) -> pd.DataFrame:
    """Generate a synthetic price series for demonstration.

    This function produces a DataFrame resembling historical OHLCV data for a
    single equity. Prices are simulated using a geometric Brownian motion model.
    Additional columns for moving averages and simple technical indicators are
    computed for use by the technical analyst.

    Parameters
    ----------
    days: int
        Number of trading days to simulate.
    start_price: float
        Starting price for the simulation.

    Returns
    -------
    pandas.DataFrame
        A DataFrame indexed by date with columns: open, high, low, close,
        volume, sma_5, sma_10, ema_12, ema_26, macd, signal, rsi.
    """
    np.random.seed(42)  # deterministic output for reproducibility
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="B")
    # Simulate log returns
    returns = np.random.normal(loc=0.0005, scale=0.01, size=days)
    prices = start_price * np.exp(np.cumsum(returns))
    df = pd.DataFrame(index=dates)
    df["close"] = prices
    # Generate OHLC ranges around close price
    df["open"] = df["close"].shift(1).fillna(df["close"])
    df["high"] = df[["open", "close"]].max(axis=1) * (1 + np.random.uniform(0, 0.01, size=days))
    df["low"] = df[["open", "close"]].min(axis=1) * (1 - np.random.uniform(0, 0.01, size=days))
    df["volume"] = np.random.randint(1000000, 5000000, size=days)
    # Simple moving averages
    df["sma_5"] = df["close"].rolling(window=5).mean()
    df["sma_10"] = df["close"].rolling(window=10).mean()
    # Exponential moving averages for MACD
    df["ema_12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_26"] = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema_12"] - df["ema_26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    # Relative Strength Index (RSI)
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    df["rsi"] = 100 - (100 / (1 + rs))
    # Fill any remaining NaNs. Rolling calculations produce NaNs at the beginning
    # of the series. Forward/backward filling ensures there is at least one
    # complete row for the technical analyst. Without this, the table may end up
    # empty if too many features are missing. In a real system you would
    # typically ignore the first few days or compute indicators only when
    # sufficient history exists.
    df = df.fillna(method="bfill").fillna(method="ffill")
    return df


# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------

@dataclass
class AnalysisReport:
    """Structured report returned by analysts and researchers."""
    title: str
    summary: str
    score: float
    details: Dict[str, float] = field(default_factory=dict)


class FundamentalAnalyst:
    """Analyses fundamental company data to estimate intrinsic value."""

    def analyze(self, ticker: str) -> AnalysisReport:
        # In a real implementation, fetch company financials (e.g. P/E, EPS)
        pe_ratio = random.uniform(5, 30)
        eps_growth = random.uniform(-0.05, 0.15)
        score = (1 / pe_ratio) + eps_growth
        summary = (
            f"PE ratio is {pe_ratio:.2f}; EPS growth estimated at {eps_growth:.2%}. "
            f"Lower PE and higher growth imply better fundamentals."
        )
        return AnalysisReport(
            title="Fundamental Analysis",
            summary=summary,
            score=score,
            details={"pe_ratio": pe_ratio, "eps_growth": eps_growth},
        )


class SentimentAnalyst:
    """Gauges market sentiment using synthetic sentiment scores."""

    def analyze(self, ticker: str) -> AnalysisReport:
        sentiment_score = random.uniform(-1, 1)
        summary = (
            f"Aggregated social and news sentiment score is {sentiment_score:.2f}. "
            f"Positive values indicate optimism, negative values indicate pessimism."
        )
        return AnalysisReport(
            title="Sentiment Analysis",
            summary=summary,
            score=sentiment_score,
            details={"sentiment_score": sentiment_score},
        )


class NewsAnalyst:
    """Evaluates macroeconomic events affecting the ticker."""

    def analyze(self, ticker: str) -> AnalysisReport:
        # Simulate a news impact score based on macro events
        macro_score = random.uniform(-0.5, 0.5)
        summary = (
            f"News impact factor is {macro_score:.2f}. Positive values suggest favourable macro events;"
            f" negative values suggest headwinds."
        )
        return AnalysisReport(
            title="News Analysis",
            summary=summary,
            score=macro_score,
            details={"macro_score": macro_score},
        )


class TechnicalAnalyst:
    """Computes technical indicators from price data."""

    def analyze(self, price_data: pd.DataFrame) -> AnalysisReport:
        # Evaluate MACD crossover
        latest = price_data.iloc[-1]
        prev = price_data.iloc[-2]
        macd_cross = int((prev["macd"] < prev["signal"]) and (latest["macd"] > latest["signal"]))
        rsi = latest["rsi"]
        summary_parts = []
        if macd_cross:
            summary_parts.append("MACD bullish crossover detected")
        elif latest["macd"] < latest["signal"]:
            summary_parts.append("MACD bearish crossover detected")
        # Interpret RSI: <30 oversold; >70 overbought
        if rsi < 30:
            summary_parts.append("RSI indicates oversold conditions")
        elif rsi > 70:
            summary_parts.append("RSI indicates overbought conditions")
        else:
            summary_parts.append("RSI in neutral range")
        score = 0
        # assign scores: +0.5 for bullish MACD, -0.5 for bearish; +0.3 for oversold, -0.3 for overbought
        score += 0.5 if macd_cross else -0.5 if latest["macd"] < latest["signal"] else 0
        score += 0.3 if rsi < 30 else -0.3 if rsi > 70 else 0
        summary = "; ".join(summary_parts)
        return AnalysisReport(
            title="Technical Analysis",
            summary=summary,
            score=score,
            details={"macd": latest["macd"], "signal": latest["signal"], "rsi": rsi},
        )


class BullResearcher:
    """Synthesises analyst reports to emphasise bullish factors."""

    def analyze(self, reports: List[AnalysisReport]) -> AnalysisReport:
        positive_score = sum(max(r.score, 0) for r in reports)
        summary = (
            "Bullish researcher highlights strengths across fundamentals, sentiment, news and technicals. "
            f"Aggregate positive score: {positive_score:.2f}."
        )
        return AnalysisReport(
            title="Bull Research",
            summary=summary,
            score=positive_score,
            details={r.title: r.score for r in reports},
        )


class BearResearcher:
    """Synthesises analyst reports to emphasise bearish factors."""

    def analyze(self, reports: List[AnalysisReport]) -> AnalysisReport:
        negative_score = sum(min(r.score, 0) for r in reports)
        summary = (
            "Bearish researcher notes risks across fundamentals, sentiment, news and technicals. "
            f"Aggregate negative score: {negative_score:.2f}."
        )
        return AnalysisReport(
            title="Bear Research",
            summary=summary,
            score=negative_score,
            details={r.title: r.score for r in reports},
        )


class Trader:
    """Decides whether to buy, sell or hold based on research."""

    def decide(self, bull_report: AnalysisReport, bear_report: AnalysisReport) -> Tuple[str, float, str]:
        # The trader compares bull vs bear scores
        total_score = bull_report.score + bear_report.score
        # Determine action: buy if score > threshold; sell if score < -threshold; else hold
        threshold = 0.3  # adjustable hyperparameter
        if total_score > threshold:
            action = "buy"
        elif total_score < -threshold:
            action = "sell"
        else:
            action = "hold"
        # Determine amount as a function of confidence
        confidence = min(abs(total_score) / 2, 1.0)  # scale into [0,1]
        amount = 100 * confidence  # trade 0–100 shares proportionally
        reason = (
            f"Trader combines bull score {bull_report.score:.2f} and bear score {bear_report.score:.2f}. "
            f"Net score {total_score:.2f} suggests a '{action}' decision with confidence {confidence:.2f}."
        )
        return action, amount, reason


class RiskManager:
    """Adjusts trader decisions based on volatility and risk tolerance."""

    def adjust(self, action: str, amount: float, price_data: pd.DataFrame) -> Tuple[str, float, str]:
        # Compute simple volatility as standard deviation of returns
        returns = price_data["close"].pct_change().dropna()
        volatility = returns.std()
        # If high volatility, reduce position size by 50%
        adjusted_amount = amount * 0.5 if volatility > 0.02 else amount
        reason = (
            f"Volatility over lookback period is {volatility:.2%}. "
            f"Adjusted amount from {amount:.2f} to {adjusted_amount:.2f} based on risk tolerance."
        )
        return action, adjusted_amount, reason


class TradingAgentsGraph:
    """Orchestrates the multi‑agent simulation.

    This class loosely follows the structure of the TradingAgents framework but
    omits the heavy dependencies on LLMs and external data. It generates
    synthetic market data, runs each agent in sequence, and returns a final
    decision along with detailed logs.
    """

    def __init__(self, debug: bool = False, config: Optional[Dict] = None) -> None:
        self.debug = debug
        self.config = config or {}
        # Instantiate agents
        self.fundamental = FundamentalAnalyst()
        self.sentiment = SentimentAnalyst()
        self.news = NewsAnalyst()
        self.technical = TechnicalAnalyst()
        self.bull = BullResearcher()
        self.bear = BearResearcher()
        self.trader = Trader()
        self.risk_manager = RiskManager()

    def propagate(self, ticker: str, date: str) -> Tuple[Dict, Dict]:
        """Run a full simulation for a single ticker and date.

        Parameters
        ----------
        ticker: str
            The stock symbol to analyse. Used only in reporting; synthetic data
            generation is independent of the ticker.
        date: str
            A date string (YYYY‑MM‑DD) representing the trading date. This
            implementation ignores the date when generating synthetic data but
            records it in the output.

        Returns
        -------
        state: Dict
            The internal state, including individual agent reports.
        decision: Dict
            The final trading decision with action, amount and narrative.
        """
        # Step 1: Generate synthetic price history
        data = generate_sample_market_data()
        if self.debug:
            print(f"Generated market data with {len(data)} rows for {ticker}")

        # Step 2: Analysts generate reports
        reports: List[AnalysisReport] = []
        reports.append(self.fundamental.analyze(ticker))
        reports.append(self.sentiment.analyze(ticker))
        reports.append(self.news.analyze(ticker))
        reports.append(self.technical.analyze(data))
        if self.debug:
            for r in reports:
                print(f"{r.title}: score={r.score:.2f}")

        # Step 3: Researchers debate
        bull_report = self.bull.analyze(reports)
        bear_report = self.bear.analyze(reports)
        if self.debug:
            print(f"Bull score: {bull_report.score:.2f}, Bear score: {bear_report.score:.2f}")

        # Step 4: Trader decision
        action, amount, trader_reason = self.trader.decide(bull_report, bear_report)

        # Step 5: Risk management
        final_action, final_amount, risk_reason = self.risk_manager.adjust(action, amount, data)

        # Compose final outputs
        state = {
            "reports": reports,
            "bull_report": bull_report,
            "bear_report": bear_report,
            "trader_reason": trader_reason,
            "risk_reason": risk_reason,
        }
        decision = {
            "action": final_action,
            "amount": round(final_amount, 2),
            "ticker": ticker,
            "date": date,
            "reason": f"{trader_reason}\n{risk_reason}",
        }
        return state, decision
