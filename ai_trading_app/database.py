"""
database.py
===========

This module manages persistence of trades using SQLite. A simple table called
`trades` stores each trade with metadata including ticker, date, action,
amount, reason and a timestamp. SQLite is used because it ships with the
standard Python library and requires no external server. The database file is
created automatically in the working directory if it does not already exist.

The functions here are intentionally straightforward: they open a connection,
ensure the table exists, insert records, query past trades and close the
connection. For a production system you might use connection pooling or an ORM
like SQLAlchemy, but for demonstration purposes this design keeps things
simple and easy to follow.
"""

from __future__ import annotations

import sqlite3
import datetime
from typing import List, Dict


DB_PATH = "trades.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def initialise_database() -> None:
    """Create the trades table if it does not exist."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            action TEXT NOT NULL,
            amount REAL NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def insert_trade(trade: Dict) -> None:
    """Insert a new trade into the database.

    Parameters
    ----------
    trade: Dict
        Dictionary with keys 'ticker', 'date', 'action', 'amount', 'reason'.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO trades (ticker, date, action, amount, reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            trade["ticker"],
            trade["date"],
            trade["action"],
            trade["amount"],
            trade["reason"],
            datetime.datetime.now(),
        ),
    )
    conn.commit()
    conn.close()


def list_trades(limit: int = 100) -> List[Dict]:
    """Return the most recent trades up to `limit` rows."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, ticker, date, action, amount, reason, created_at FROM trades ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
