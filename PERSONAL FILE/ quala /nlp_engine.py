"""
QUALA NLP Sentiment & Event Engine
Rule-based finance NLP — production upgrade: swap with FinBERT/HuggingFace.
Made by Yaskin's
"""

import re
import math
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.config import (STOCKS, SECTOR_KEYWORDS, POSITIVE_WORDS,
                          NEGATIVE_WORDS, INTENSIFIERS, NEGATORS)

# ── Ticker direct-mention map ─────────────────────────────────────────────────
TICKER_ALIASES = {}
for sym, info in STOCKS.items():
    TICKER_ALIASES[sym.lower()] = sym
    for word in info["name"].lower().split():
        if len(word) > 3:
            TICKER_ALIASES[word] = sym

EVENT_PATTERNS = {
    "earnings":    [r"q[1-4]\s+result", r"quarterly\s+profit", r"net\s+profit", r"revenue\s+beat", r"earnings\s+report", r"eps\b"],
    "policy":      [r"rbi\s+policy", r"repo\s+rate", r"fed\s+rate", r"interest\s+rate", r"monetary\s+policy", r"budget\s+20\d\d"],
    "geopolitical":[r"war\b", r"sanction", r"trade\s+war", r"conflict", r"opec", r"embargo", r"tariff"],
    "regulatory":  [r"sebi\b", r"rbi\s+ban", r"sec\s+", r"penalty", r"fine\b", r"probe\b", r"investigation"],
    "innovation":  [r"launch", r"breakthrough", r"patent", r"acquisition", r"merger", r"deal\s+worth", r"partnership"],
    "macro":       [r"inflation", r"gdp\s+growth", r"recession", r"unemployment", r"iip\b", r"pmi\b"],
}

def tokenize(text: str) -> list:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()

def _count_sentiments(tokens: list) -> tuple:
    pos = neg = 0
    for i, tok in enumerate(tokens):
        multiplier = 1.0
        # check preceding 2 words for negators/intensifiers
        prev = tokens[max(0, i-2):i]
        if any(n in prev for n in NEGATORS):
            multiplier = -1.0
        elif any(n in prev for n in INTENSIFIERS):
            multiplier = 1.5
        if tok in POSITIVE_WORDS:
            if multiplier > 0: pos += multiplier
            else: neg += abs(multiplier)
        elif tok in NEGATIVE_WORDS:
            if multiplier > 0: neg += multiplier
            else: pos += abs(multiplier)
    return pos, neg

def analyze_sentiment(text: str) -> dict:
    tokens   = tokenize(text)
    pos, neg = _count_sentiments(tokens)
    total    = pos + neg + 1e-9
    raw_score = (pos - neg) / math.sqrt(total)
    # Normalize to -1 … +1 via tanh
    score    = math.tanh(raw_score / 3)
    if score > 0.15:
        label = "positive"
    elif score < -0.15:
        label = "negative"
    else:
        label = "neutral"
    confidence = min(abs(score) * 1.4, 0.99)
    return {
        "score":      round(score, 4),
        "label":      label,
        "confidence": round(confidence, 3),
        "pos_words":  round(pos, 1),
        "neg_words":  round(neg, 1),
    }

def detect_events(text: str) -> list:
    found = []
    text_lower = text.lower()
    for event_type, patterns in EVENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                found.append(event_type)
                break
    return list(set(found))

def extract_tickers(text: str) -> list:
    tokens = tokenize(text)
    hits   = set()
    # direct symbol match
    for tok in tokens:
        if tok.upper() in STOCKS:
            hits.add(tok.upper())
        elif tok in TICKER_ALIASES:
            hits.add(TICKER_ALIASES[tok])
    # sector keyword match
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw in text.lower():
                for sym, info in STOCKS.items():
                    if info["sector"] == sector:
                        hits.add(sym)
                break
    return list(hits)

def analyze_news(article: dict) -> dict:
    """Full analysis of a single news article."""
    text     = article.get("title", "") + " " + article.get("body", "")
    sentiment = analyze_sentiment(text)
    events    = detect_events(text)
    tickers   = extract_tickers(text)
    impact    = _compute_impact(sentiment, events)
    return {
        "article_id": article.get("id", ""),
        "headline":   article.get("title", ""),
        "source":     article.get("source", ""),
        "sentiment":  sentiment,
        "events":     events,
        "tickers":    tickers,
        "impact_score": impact,
    }

def _compute_impact(sentiment: dict, events: list) -> float:
    base = abs(sentiment["score"])
    event_boost = {
        "earnings":     0.25,
        "policy":       0.20,
        "geopolitical": 0.30,
        "regulatory":   0.28,
        "innovation":   0.15,
        "macro":        0.18,
    }
    for e in events:
        base += event_boost.get(e, 0.10)
    return round(min(base, 1.0), 3)
