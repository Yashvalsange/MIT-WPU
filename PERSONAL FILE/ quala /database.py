"""
QUALA Database Layer — SQLite
Stores signals, analyses, budgets, tax profiles.
Made by Yaskin's
"""

import sqlite3
import json
import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.config import DB_PATH


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS signals (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker      TEXT NOT NULL,
        signal      TEXT NOT NULL,
        confidence  REAL,
        final_score REAL,
        rsi         REAL,
        price       REAL,
        risk        TEXT,
        reasons     TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS news_analysis (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id  TEXT,
        headline    TEXT,
        source      TEXT,
        sentiment   TEXT,
        tickers     TEXT,
        events      TEXT,
        impact_score REAL,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS tax_profiles (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        profile     TEXT,
        result      TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS budget_analyses (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        income      REAL,
        expenses    TEXT,
        result      TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    """)
    conn.commit()
    conn.close()


def save_signals(signals: list):
    conn = get_conn()
    c    = conn.cursor()
    for s in signals:
        c.execute("""INSERT INTO signals
            (ticker, signal, confidence, final_score, rsi, price, risk, reasons)
            VALUES (?,?,?,?,?,?,?,?)""",
            (s["ticker"], s["signal"], s["confidence"], s["final_score"],
             s["rsi"], s["price"], s["risk"], json.dumps(s["reasons"])))
    conn.commit()
    conn.close()


def save_tax(profile, result):
    conn = get_conn()
    conn.execute("INSERT INTO tax_profiles (profile,result) VALUES (?,?)",
                 (json.dumps(profile), json.dumps(result)))
    conn.commit()
    conn.close()


def save_budget(income, expenses, result):
    conn = get_conn()
    conn.execute("INSERT INTO budget_analyses (income,expenses,result) VALUES (?,?,?)",
                 (income, json.dumps(expenses), json.dumps(result)))
    conn.commit()
    conn.close()


def get_latest_signals(limit=15):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM signals ORDER BY created_at DESC, confidence DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
