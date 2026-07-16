"""
QUALA Tax Engine — India FY 2025-26
Supports Old & New Regime, auto-deduction optimizer, refund calculator.
Made by Yaskin's
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.config import (NEW_REGIME_SLABS, OLD_REGIME_SLABS,
                          STD_DEDUCTION_NEW, STD_DEDUCTION_OLD, HEALTH_EDU_CESS)


def _compute_tax_from_slabs(income: float, slabs: list) -> float:
    tax = 0.0
    prev = 0
    for limit, rate in slabs:
        if income <= prev:
            break
        taxable = min(income, limit) - prev
        tax += taxable * rate
        prev = limit
    return tax


def _apply_rebate_87a(tax: float, income: float, regime: str) -> float:
    """Section 87A rebate."""
    limit = 700000 if regime == "new" else 500000
    max_rebate = 25000 if regime == "new" else 12500
    if income <= limit:
        tax = max(0, tax - max_rebate)
    return tax


def compute_tax(profile: dict) -> dict:
    """
    profile = {
        "gross_salary": float,
        "hra_received": float,         # optional
        "rent_paid": float,            # optional
        "city_type": "metro"|"non-metro",
        "deductions_80c": float,       # max 150000
        "deductions_80d": float,       # health insurance, max 25000
        "nps_80ccd": float,            # NPS contribution, max 50000
        "home_loan_interest": float,   # max 200000
        "education_loan_int": float,
        "other_deductions": float,
        "tds_deducted": float,
    }
    """
    gross   = profile.get("gross_salary", 0)
    tds     = profile.get("tds_deducted", 0)

    # ── New Regime ────────────────────────────────────────────────────────────
    taxable_new    = max(0, gross - STD_DEDUCTION_NEW)
    tax_new_base   = _compute_tax_from_slabs(taxable_new, NEW_REGIME_SLABS)
    tax_new_rebate = _apply_rebate_87a(tax_new_base, taxable_new, "new")
    cess_new       = tax_new_rebate * HEALTH_EDU_CESS
    tax_new_total  = round(tax_new_rebate + cess_new, 2)

    # ── Old Regime ────────────────────────────────────────────────────────────
    hra_exempt = _calc_hra_exemption(
        gross, profile.get("hra_received", 0),
        profile.get("rent_paid", 0), profile.get("city_type", "metro"))

    d80c   = min(profile.get("deductions_80c", 0),   150000)
    d80d   = min(profile.get("deductions_80d", 0),   25000)
    d80ccd = min(profile.get("nps_80ccd", 0),        50000)
    home_l = min(profile.get("home_loan_interest", 0), 200000)
    edu_l  = profile.get("education_loan_int", 0)
    other  = profile.get("other_deductions", 0)

    total_deductions = STD_DEDUCTION_OLD + hra_exempt + d80c + d80d + d80ccd + home_l + edu_l + other
    taxable_old      = max(0, gross - total_deductions)
    tax_old_base     = _compute_tax_from_slabs(taxable_old, OLD_REGIME_SLABS)
    tax_old_rebate   = _apply_rebate_87a(tax_old_base, taxable_old, "old")
    cess_old         = tax_old_rebate * HEALTH_EDU_CESS
    tax_old_total    = round(tax_old_rebate + cess_old, 2)

    # ── Recommendation ────────────────────────────────────────────────────────
    if tax_new_total <= tax_old_total:
        recommended = "new"
        savings     = round(tax_old_total - tax_new_total, 2)
    else:
        recommended = "old"
        savings     = round(tax_new_total - tax_old_total, 2)

    # ── Refund / Payable ──────────────────────────────────────────────────────
    final_tax = tax_new_total if recommended == "new" else tax_old_total
    refund    = round(tds - final_tax, 2)

    return {
        "gross_salary":    gross,
        "regime_new": {
            "taxable_income": taxable_new,
            "tax_before_cess": tax_new_rebate,
            "cess": round(cess_new, 2),
            "total_tax": tax_new_total,
        },
        "regime_old": {
            "taxable_income": taxable_old,
            "total_deductions": round(total_deductions, 2),
            "deduction_breakup": {
                "standard_deduction": STD_DEDUCTION_OLD,
                "hra_exemption":      round(hra_exempt, 2),
                "80c":                d80c,
                "80d":                d80d,
                "80ccd_nps":          d80ccd,
                "home_loan_interest": home_l,
                "education_loan":     edu_l,
                "other":              other,
            },
            "tax_before_cess": tax_old_rebate,
            "cess": round(cess_old, 2),
            "total_tax": tax_old_total,
        },
        "recommended_regime": recommended,
        "tax_savings":   savings,
        "tds_deducted":  tds,
        "final_tax":     final_tax,
        "refund_or_payable": refund,
        "status": "REFUND" if refund > 0 else "PAYABLE",
    }


def _calc_hra_exemption(gross, hra_received, rent_paid, city_type):
    if not rent_paid:
        return 0
    basic   = gross * 0.40   # assume basic = 40% gross
    percent = 0.50 if city_type == "metro" else 0.40
    exempt  = min(hra_received, basic * percent, max(0, rent_paid - 0.10 * basic))
    return max(0, exempt)


def get_tax_saving_tips(profile: dict, result: dict) -> list:
    tips = []
    regime_old = result["regime_old"]
    d = regime_old["deduction_breakup"]

    unused_80c = 150000 - d["80c"]
    if unused_80c > 0:
        tips.append(f"Invest ₹{unused_80c:,.0f} more in ELSS/PPF/LIC to fully utilize 80C — saves ₹{unused_80c*0.30*1.04:,.0f} in tax.")

    if d["80d"] < 25000:
        gap = 25000 - d["80d"]
        tips.append(f"Buy health insurance worth ₹{gap:,.0f} more to max out 80D deduction.")

    if d["80ccd_nps"] < 50000:
        gap = 50000 - d["80ccd_nps"]
        tips.append(f"Contribute ₹{gap:,.0f} to NPS (Tier-1) to claim extra 80CCD(1B) deduction.")

    if profile.get("rent_paid", 0) > 0 and d["hra_exemption"] == 0:
        tips.append("Claim HRA exemption — you're paying rent but not claiming it. File Form 12BB.")

    if profile.get("home_loan_interest", 0) == 0:
        tips.append("If you have a home loan, interest up to ₹2,00,000 is deductible under Section 24.")

    tips.append("Donate to PM Relief Fund / approved NGOs for 80G deduction (50-100% of donation).")
    tips.append("Invest in LTCG-exempt equity for returns above ₹1L — use tax-loss harvesting to offset gains.")
    return tips
