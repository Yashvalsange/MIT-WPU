"""
QUALA Market Data Engine
Generates realistic OHLCV price data using geometric Brownian motion.
In production: replace generate_prices() with yfinance / NSE API calls.
Made by Yaskin's
"""

import random
import math
import datetime
import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.config import STOCKS, DB_PATH


def _gbm_prices(base: float, days: int, mu: float = 0.0003, sigma: float = 0.018, seed: int = 42) -> list:
    """Geometric Brownian Motion price simulation."""
    rng = random.Random(seed)
    prices = [base]
    for _ in range(days - 1):
        dt = 1
        drift = (mu - 0.5 * sigma ** 2) * dt
        shock = sigma * math.sqrt(dt) * rng.gauss(0, 1)
        prices.append(round(prices[-1] * math.exp(drift + shock), 2))
    return prices


def generate_ohlcv(ticker: str, days: int = 90) -> list:
    """Generate OHLCV candles for a ticker."""
    info  = STOCKS[ticker]
    base  = info["base"]
    seed  = hash(ticker) % 10000
    closes = _gbm_prices(base, days, seed=seed)
    rng   = random.Random(seed + 1)

    candles = []
    today   = datetime.date.today()
    for i, close in enumerate(closes):
        date   = today - datetime.timedelta(days=days - i - 1)
        spread = close * rng.uniform(0.005, 0.025)
        high   = round(close + spread * rng.uniform(0.3, 1.0), 2)
        low    = round(close - spread * rng.uniform(0.3, 1.0), 2)
        open_  = round(low + (high - low) * rng.random(), 2)
        vol    = int(rng.uniform(500_000, 5_000_000))
        candles.append({
            "date":   str(date),
            "open":   open_,
            "high":   high,
            "low":    low,
            "close":  close,
            "volume": vol,
        })
    return candles


# ── Technical Indicators ──────────────────────────────────────────────────────

def _sma(prices: list, period: int) -> list:
    result = [None] * (period - 1)
    for i in range(period - 1, len(prices)):
        result.append(round(sum(prices[i - period + 1:i + 1]) / period, 2))
    return result


def _ema(prices: list, period: int) -> list:
    k = 2 / (period + 1)
    result = [None] * (period - 1)
    ema = sum(prices[:period]) / period
    result.append(round(ema, 2))
    for p in prices[period:]:
        ema = p * k + ema * (1 - k)
        result.append(round(ema, 2))
    return result


def compute_rsi(prices: list, period: int = 14) -> list:
    result = [None] * period
    for i in range(period, len(prices)):
        window = prices[i - period:i]
        gains  = [max(window[j] - window[j-1], 0) for j in range(1, len(window))]
        losses = [max(window[j-1] - window[j], 0) for j in range(1, len(window))]
        avg_g  = sum(gains)  / (period - 1) or 1e-9
        avg_l  = sum(losses) / (period - 1) or 1e-9
        rs     = avg_g / avg_l
        result.append(round(100 - 100 / (1 + rs), 2))
    return result


def compute_macd(prices: list) -> dict:
    ema12 = _ema(prices, 12)
    ema26 = _ema(prices, 26)
    macd_line   = [round(a - b, 4) if a and b else None for a, b in zip(ema12, ema26)]
    valid_macd  = [v for v in macd_line if v is not None]
    signal_part = _ema(valid_macd, 9)
    signal_full = [None] * (len(macd_line) - len(signal_part)) + signal_part
    histogram   = [round(m - s, 4) if m and s else None for m, s in zip(macd_line, signal_full)]
    return {"macd": macd_line, "signal": signal_full, "histogram": histogram}


def compute_bollinger(prices: list, period: int = 20, num_std: float = 2.0) -> dict:
    mid  = _sma(prices, period)
    upper, lower = [], []
    for i in range(len(prices)):
        if mid[i] is None:
            upper.append(None); lower.append(None)
        else:
            window = prices[i - period + 1:i + 1]
            mean   = sum(window) / period
            std    = math.sqrt(sum((x - mean) ** 2 for x in window) / period)
            upper.append(round(mid[i] + num_std * std, 2))
            lower.append(round(mid[i] - num_std * std, 2))
    return {"upper": upper, "mid": mid, "lower": lower}


def get_technicals(ticker: str) -> dict:
    candles = generate_ohlcv(ticker, days=90)
    closes  = [c["close"] for c in candles]
    rsi     = compute_rsi(closes)
    macd    = compute_macd(closes)
    bb      = compute_bollinger(closes)
    sma20   = _sma(closes, 20)
    sma50   = _sma(closes, 50)

    latest_close = closes[-1]
    latest_rsi   = next((v for v in reversed(rsi) if v is not None), 50)
    latest_macd  = next((v for v in reversed(macd["histogram"]) if v is not None), 0)
    latest_bb_u  = next((v for v in reversed(bb["upper"]) if v is not None), latest_close * 1.05)
    latest_bb_l  = next((v for v in reversed(bb["lower"]) if v is not None), latest_close * 0.95)
    latest_sma20 = next((v for v in reversed(sma20) if v is not None), latest_close)
    latest_sma50 = next((v for v in reversed(sma50) if v is not None), latest_close)

    # Scoring
    score = 0
    reasons = []

    if latest_rsi < 35:
        score += 2; reasons.append(f"RSI oversold ({latest_rsi:.1f}) — potential reversal")
    elif latest_rsi > 70:
        score -= 2; reasons.append(f"RSI overbought ({latest_rsi:.1f}) — overheated")
    else:
        score += 1; reasons.append(f"RSI neutral ({latest_rsi:.1f}) — healthy momentum")

    if latest_macd > 0:
        score += 1; reasons.append("MACD histogram positive — bullish crossover")
    else:
        score -= 1; reasons.append("MACD histogram negative — bearish pressure")

    if latest_close > latest_sma20 > latest_sma50:
        score += 2; reasons.append("Price above SMA20 > SMA50 — strong uptrend")
    elif latest_close < latest_sma20 < latest_sma50:
        score -= 2; reasons.append("Price below SMA20 < SMA50 — downtrend confirmed")

    bb_pos = (latest_close - latest_bb_l) / (latest_bb_u - latest_bb_l + 1e-9)
    if bb_pos < 0.2:
        score += 1; reasons.append("Price near Bollinger lower band — buy zone")
    elif bb_pos > 0.8:
        score -= 1; reasons.append("Price near Bollinger upper band — overbought zone")

    pct_change_30d = round((closes[-1] / closes[-30] - 1) * 100, 2) if len(closes) >= 30 else 0

    return {
        "ticker":       ticker,
        "latest_close": latest_close,
        "rsi":          latest_rsi,
        "macd_hist":    latest_macd,
        "bb_position":  round(bb_pos, 3),
        "sma20":        latest_sma20,
        "sma50":        latest_sma50,
        "tech_score":   score,
        "tech_reasons": reasons,
        "pct_change_30d": pct_change_30d,
        "candles":      candles[-30:],
    }
