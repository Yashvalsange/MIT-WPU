"""
QUALA Signal Engine
Fuses NLP sentiment scores with technical indicators to produce BUY/SELL/HOLD.
Made by Yaskin's
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.market_data import get_technicals
from core.nlp_engine  import analyze_news
from core.config       import STOCKS

# Simulated news dataset — in production: replaced by live API feed
SAMPLE_NEWS = [
    {"id":"n001","title":"India IT sector to hit $350B revenue by 2026 amid global AI boom","body":"Tata Consultancy Services and Infosys are leading the charge as AI-driven outsourcing demand surges. Strong deal wins and digital transformation orders are boosting growth prospects significantly.","source":"ET Markets","category":"IT"},
    {"id":"n002","title":"RBI maintains repo rate at 6.5%, signals cautious stance","body":"Reserve Bank of India kept interest rates unchanged citing inflation concerns. HDFC Bank and other NBFCs may face pressure on margins as lending growth slows in near term.","source":"Bloomberg","category":"Banking"},
    {"id":"n003","title":"NVIDIA announces Blackwell GPU expansion to Indian cloud partners","body":"NVIDIA is boosting GPU supply for Microsoft Azure and Google Cloud India. Strong AI chip demand continues to surge with no signs of slowdown. Record revenue expected next quarter.","source":"Reuters","category":"Semicon"},
    {"id":"n004","title":"RBI imposes fresh payment restrictions on Paytm Payment Bank","body":"Reserve Bank of India has revoked Paytm Payment Bank license raising regulatory concerns. Fine and investigation ongoing. Paytm stock expected to face significant bearish pressure.","source":"NDTV Profit","category":"Fintech"},
    {"id":"n005","title":"Reliance Industries Q3 profit in line, Jio growth impressive","body":"Reliance Industries posted strong quarterly results with Jio subscriber growth beating estimates. Oil-to-chemicals segment robust. Management optimistic about retail expansion.","source":"NSE Bulletin","category":"Energy"},
    {"id":"n006","title":"Tesla EV sales slump in Europe amid rising competition","body":"Tesla faces declining market share as BYD and European automakers gain ground. Cybertruck demand disappoints. Price cuts fail to boost volume. Analysts downgrade outlook.","source":"Reuters","category":"EV/Auto"},
    {"id":"n007","title":"Wipro wins $200M multi-year cloud transformation deal","body":"Wipro secured a major cloud outsourcing contract boosting revenue visibility. The deal win signals strong IT outsourcing momentum and improves earnings guidance.","source":"Moneycontrol","category":"IT"},
    {"id":"n008","title":"Crude oil prices surge on OPEC+ production cut extension","body":"OPEC extended production cuts sending Brent crude above $90. ONGC and Reliance stand to benefit significantly from higher oil prices in the coming quarters.","source":"Bloomberg","category":"Energy"},
    {"id":"n009","title":"Apple iPhone 16 demand strong in India, record ASP growth","body":"Apple reports record iPhone shipments in India with premium mix improving significantly. Services revenue grows 14% YoY. Analysts upgrade to outperform with higher price targets.","source":"WSJ","category":"Tech"},
    {"id":"n010","title":"Bajaj Finance faces NPA concerns amid unsecured loan growth","body":"Rising bad loans in personal loan segment raise concern for Bajaj Finance. RBI scrutiny on unsecured lending practices could pressure margins and growth trajectory.","source":"ET Markets","category":"NBFC"},
    {"id":"n011","title":"Infosys issues revenue growth guidance cut for FY26","body":"Infosys slashed its revenue growth guidance citing weak deal ramp-ups and client budget delays. Disappointing earnings miss estimates. Analysts downgrade to neutral.","source":"Reuters","category":"IT"},
    {"id":"n012","title":"Microsoft Azure AI cloud revenue beats estimates by 18%","body":"Microsoft reported strong Azure cloud growth driven by AI services adoption. Copilot enterprise rollout exceeding targets. Record quarterly profit boosts investor confidence.","source":"CNBC","category":"Tech"},
    {"id":"n013","title":"Sun Pharma US drug approvals surge, biosimilar pipeline strong","body":"Sun Pharmaceutical gets FDA approval for three new generic drugs. US business growing strongly. Biosimilar launches expected to drive significant revenue growth ahead.","source":"Pharma Journal","category":"Pharma"},
    {"id":"n014","title":"Tata Motors EV sales hit record high, JLR profit doubles","body":"Tata Motors reports record electric vehicle sales in India and UK. Jaguar Land Rover doubles profit on strong order book. Management raises FY guidance. Bullish outlook.","source":"Autocar","category":"Auto"},
    {"id":"n015","title":"Global recession fears rise as US manufacturing PMI contracts","body":"US PMI data signals contraction as factory orders fall sharply. Recession fears intensify. Tech stocks and emerging markets face selling pressure as risk-off sentiment dominates.","source":"Bloomberg","category":"Macro"},
]


def compute_signal(ticker: str, news_analyses: list) -> dict:
    tech = get_technicals(ticker)
    info = STOCKS[ticker]

    # Filter relevant news
    relevant = [a for a in news_analyses if ticker in a["tickers"]]

    # NLP composite score
    if relevant:
        nlp_score = sum(
            a["sentiment"]["score"] * a["impact_score"] for a in relevant
        ) / len(relevant)
        nlp_score = max(-1.0, min(1.0, nlp_score))
    else:
        nlp_score = 0.0

    tech_score = tech["tech_score"]

    # Normalize tech_score to -1..+1 (range is roughly -6 to +6)
    tech_norm = max(-1.0, min(1.0, tech_score / 6.0))

    # Weighted fusion: 55% NLP, 45% Technical
    final_score = 0.55 * nlp_score + 0.45 * tech_norm

    # Signal classification
    if final_score >= 0.25:
        signal = "BUY"
        color  = "green"
    elif final_score <= -0.20:
        signal = "SELL"
        color  = "red"
    else:
        signal = "HOLD"
        color  = "yellow"

    confidence = round(min(abs(final_score) * 1.6 + 0.35, 0.98), 2)

    # Risk
    volatility = abs(tech["pct_change_30d"])
    if volatility > 15:
        risk = "HIGH"
    elif volatility > 7:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Build reasoning
    reasons = []
    if relevant:
        top_news = sorted(relevant, key=lambda x: abs(x["impact_score"]), reverse=True)[:2]
        for n in top_news:
            reasons.append(f"[{n['source']}] {n['headline'][:70]}... → {n['sentiment']['label'].upper()}")
    reasons += tech["tech_reasons"][:2]

    return {
        "ticker":       ticker,
        "name":         info["name"],
        "sector":       info["sector"],
        "exchange":     info["exchange"],
        "currency":     info["currency"],
        "price":        tech["latest_close"],
        "signal":       signal,
        "color":        color,
        "confidence":   confidence,
        "confidence_pct": int(confidence * 100),
        "final_score":  round(final_score, 4),
        "nlp_score":    round(nlp_score, 4),
        "tech_score":   tech_score,
        "rsi":          tech["rsi"],
        "macd_hist":    tech["macd_hist"],
        "pct_change_30d": tech["pct_change_30d"],
        "risk":         risk,
        "reasons":      reasons,
        "news_count":   len(relevant),
        "candles":      tech["candles"],
    }


def run_full_analysis() -> list:
    news_analyses = [analyze_news(n) for n in SAMPLE_NEWS]
    results = []
    for ticker in STOCKS:
        try:
            sig = compute_signal(ticker, news_analyses)
            results.append(sig)
        except Exception as e:
            print(f"[WARN] {ticker}: {e}")
    results.sort(key=lambda x: (-x["confidence"], x["signal"]))
    return results
