"""
QUALA Budget Engine
Zero-based budgeting, smart allocation, savings optimizer.
Made by Yaskin's
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.config import BUDGET_CATEGORIES


def analyze_budget(income: float, expenses: dict) -> dict:
    """
    expenses = {"Housing": 20000, "Food": 12000, ...}
    """
    total_spent = sum(expenses.values())
    surplus     = income - total_spent

    analysis = {}
    alerts   = []
    tips     = []

    for cat, meta in BUDGET_CATEGORIES.items():
        spent    = expenses.get(cat, 0)
        ideal    = income * meta["ideal_pct"]
        actual_p = spent / income if income else 0
        ideal_p  = meta["ideal_pct"]
        diff     = spent - ideal
        pct_diff = (diff / ideal * 100) if ideal else 0

        status = "on_track"
        if pct_diff > 20:
            status = "overspending"
            alerts.append(f"⚠️  {meta['icon']} {cat}: overspending by ₹{diff:,.0f} ({pct_diff:.0f}% over ideal)")
        elif pct_diff < -30 and cat in ("Investments", "Savings"):
            status = "underspending"
            alerts.append(f"💡 {meta['icon']} {cat}: under-investing by ₹{abs(diff):,.0f} — opportunity to grow wealth!")

        analysis[cat] = {
            "spent":      spent,
            "ideal":      round(ideal, 2),
            "actual_pct": round(actual_p * 100, 1),
            "ideal_pct":  round(ideal_p * 100, 1),
            "diff":       round(diff, 2),
            "pct_diff":   round(pct_diff, 1),
            "status":     status,
            "icon":       meta["icon"],
        }

    # Smart tips
    if surplus > 0:
        inv_alloc = round(surplus * 0.60, 2)
        liq_alloc = round(surplus * 0.25, 2)
        fun_alloc = round(surplus * 0.15, 2)
        tips.append(f"💰 You have a surplus of ₹{surplus:,.0f}! Allocate: ₹{inv_alloc:,.0f} → SIP, ₹{liq_alloc:,.0f} → Liquid Fund, ₹{fun_alloc:,.0f} → discretionary.")
    else:
        tips.append(f"🚨 You're spending ₹{abs(surplus):,.0f} MORE than you earn. Cut top 2 overspend categories immediately.")

    food_pct = analysis.get("Food", {}).get("pct_diff", 0)
    if food_pct > 15:
        tips.append("🍱 Food spending is high — try meal prep on weekends; can save ₹2,000-4,000/month.")

    entertain = analysis.get("Entertainment", {}).get("spent", 0)
    if entertain > income * 0.08:
        tips.append("🎬 Entertainment over budget — audit subscriptions; average Indian has 4 unused ones.")

    inv = analysis.get("Investments", {}).get("spent", 0)
    ideal_inv = income * 0.20
    if inv < ideal_inv:
        tips.append(f"📈 Increase monthly SIP by ₹{round(ideal_inv - inv):,} to hit 20% investment target — compounding will reward you.")

    score = _financial_health_score(income, expenses, surplus)

    return {
        "income":       income,
        "total_spent":  total_spent,
        "surplus":      round(surplus, 2),
        "analysis":     analysis,
        "alerts":       alerts,
        "tips":         tips,
        "health_score": score,
        "grade":        _grade(score),
    }


def _financial_health_score(income, expenses, surplus) -> int:
    score = 50
    # Surplus ratio
    surplus_ratio = surplus / income if income else 0
    score += int(surplus_ratio * 30)
    # Investment ratio
    inv = expenses.get("Investments", 0) + expenses.get("Savings", 0)
    inv_ratio = inv / income if income else 0
    score += int(inv_ratio * 40)
    # Penalize overspend on non-essentials
    for cat in ("Entertainment", "Food"):
        s = expenses.get(cat, 0)
        ideal = income * BUDGET_CATEGORIES[cat]["ideal_pct"]
        if s > ideal * 1.3:
            score -= 5
    return max(0, min(100, score))


def _grade(score: int) -> str:
    if score >= 80: return "A+ — Excellent"
    if score >= 65: return "B — Good"
    if score >= 50: return "C — Average"
    if score >= 35: return "D — Needs Work"
    return "F — Critical"


def suggest_sip_allocation(monthly_investment: float) -> list:
    """Suggest SIP allocation for a given monthly amount."""
    return [
        {"fund": "Nifty 50 Index Fund",     "pct": 40, "amount": round(monthly_investment * 0.40, 2), "type": "Large Cap"},
        {"fund": "Nifty Next 50 Index",     "pct": 20, "amount": round(monthly_investment * 0.20, 2), "type": "Mid Cap"},
        {"fund": "Flexi Cap Fund",           "pct": 20, "amount": round(monthly_investment * 0.20, 2), "type": "Diversified"},
        {"fund": "Short Duration Debt Fund", "pct": 10, "amount": round(monthly_investment * 0.10, 2), "type": "Debt"},
        {"fund": "International Fund (US)",  "pct": 10, "amount": round(monthly_investment * 0.10, 2), "type": "Global"},
    ]


def project_wealth(monthly_sip: float, years: int, annual_return: float = 0.12) -> dict:
    monthly_rate = annual_return / 12
    months       = years * 12
    future_val   = monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    invested     = monthly_sip * months
    returns      = future_val - invested
    return {
        "monthly_sip":   monthly_sip,
        "years":         years,
        "total_invested": round(invested, 2),
        "future_value":  round(future_val, 2),
        "wealth_gained": round(returns, 2),
        "cagr":          f"{annual_return*100:.0f}%",
    }
