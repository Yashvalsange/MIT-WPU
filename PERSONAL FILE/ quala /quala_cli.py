"""
QUALA CLI — Main Entry Point
Made by Yaskin's
"""

import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(__file__))

from core.config       import APP_NAME, APP_VERSION, APP_CREDIT, STOCKS
from core.signal_engine import run_full_analysis
from core.tax_engine   import compute_tax, get_tax_saving_tips
from core.budget_engine import analyze_budget, suggest_sip_allocation, project_wealth
from core.database     import init_db, save_signals, save_tax, save_budget

# ── Terminal colors ───────────────────────────────────────────────────────────
G  = "\033[92m"   # green
R  = "\033[91m"   # red
Y  = "\033[93m"   # yellow
C  = "\033[96m"   # cyan
B  = "\033[94m"   # blue
W  = "\033[97m"   # white
DIM= "\033[2m"
BOLD="\033[1m"
RST= "\033[0m"

def clr(text, color): return f"{color}{text}{RST}"
def signal_color(s):
    return G if s == "BUY" else (R if s == "SELL" else Y)

def banner():
    print(f"""
{C}{BOLD}
 ██████╗ ██╗   ██╗ █████╗ ██╗      █████╗
██╔═══██╗██║   ██║██╔══██╗██║     ██╔══██╗
██║   ██║██║   ██║███████║██║     ███████║
██║▄▄ ██║██║   ██║██╔══██║██║     ██╔══██║
╚██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║
 ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{RST}
{DIM}   AI Financial Intelligence Engine v{APP_VERSION}{RST}
{DIM}   {APP_CREDIT}{RST}
""")

def separator(title="", char="─", width=68):
    if title:
        side = (width - len(title) - 2) // 2
        print(f"{DIM}{char*side} {W}{BOLD}{title}{RST} {DIM}{char*side}{RST}")
    else:
        print(f"{DIM}{char*width}{RST}")

def fmt_inr(n):
    if abs(n) >= 10_000_000: return f"₹{n/10_000_000:.2f}Cr"
    if abs(n) >= 100_000:    return f"₹{n/100_000:.2f}L"
    return f"₹{n:,.0f}"

def run_stock_analysis():
    separator("STOCK INTELLIGENCE ENGINE")
    print(f"\n{C}⟳  Running NLP + Technical analysis across {len(STOCKS)} stocks...{RST}\n")
    signals = run_full_analysis()
    save_signals(signals)

    # Header
    print(f"  {'TICKER':<12}{'NAME':<28}{'PRICE':<12}{'SIGNAL':<8}{'CONF':<8}{'RSI':<8}{'30D%':<9}{'RISK'}")
    separator(char="─")

    for s in signals:
        sym    = clr(f"{s['ticker']:<12}", C)
        name   = f"{s['name'][:26]:<28}"
        price  = f"{s['currency']} {s['price']:,.1f}"
        price  = f"{price:<12}"
        sig    = clr(f"{'●'} {s['signal']:<6}", signal_color(s["signal"]))
        conf   = clr(f"{s['confidence_pct']}%", W)
        conf   = f"{conf:<8}"
        rsi    = f"{s['rsi']:.1f}"
        rsi_c  = G if s['rsi'] < 40 else (R if s['rsi'] > 70 else Y)
        rsi_s  = clr(f"{rsi:<8}", rsi_c)
        chg    = f"{s['pct_change_30d']:+.1f}%"
        chg_c  = G if s['pct_change_30d'] > 0 else R
        chg_s  = clr(f"{chg:<9}", chg_c)
        risk_c = R if s['risk']=="HIGH" else (Y if s['risk']=="MEDIUM" else G)
        risk_s = clr(s['risk'], risk_c)
        print(f"  {sym}{name}{price}{sig}{conf}{rsi_s}{chg_s}{risk_s}")

    # Summary
    buys  = [s for s in signals if s["signal"]=="BUY"]
    sells = [s for s in signals if s["signal"]=="SELL"]
    holds = [s for s in signals if s["signal"]=="HOLD"]
    separator()
    print(f"\n  {clr('BUY', G)}: {len(buys)}   {clr('HOLD', Y)}: {len(holds)}   {clr('SELL', R)}: {len(sells)}")

    # Top picks
    print(f"\n{C}{BOLD}  ★  TOP PICKS TODAY  ★{RST}")
    top = [s for s in signals if s["signal"]=="BUY"][:3]
    for s in top:
        print(f"\n  {clr(s['ticker'], C)} — {s['name']} | {clr(s['signal'], G)} {s['confidence_pct']}% confidence")
        for r in s["reasons"][:2]:
            print(f"    {DIM}• {r[:80]}{RST}")

    return signals

def run_tax_calculator():
    separator("TAX CALCULATOR — FY 2025-26")
    print(f"\n  {DIM}Using demo profile (replace with your data in production){RST}\n")

    profile = {
        "gross_salary":       1200000,
        "hra_received":        180000,
        "rent_paid":           168000,
        "city_type":           "metro",
        "deductions_80c":      150000,
        "deductions_80d":       25000,
        "nps_80ccd":            50000,
        "home_loan_interest":  200000,
        "education_loan_int":       0,
        "other_deductions":         0,
        "tds_deducted":         95000,
    }

    result = compute_tax(profile)
    save_tax(profile, result)
    tips   = get_tax_saving_tips(profile, result)

    print(f"  {C}Gross Salary:{RST}          {fmt_inr(profile['gross_salary'])}")
    print(f"  {C}TDS Deducted:{RST}          {fmt_inr(profile['tds_deducted'])}")
    separator()
    nr = result["regime_new"]
    or_ = result["regime_old"]
    print(f"\n  {'Regime':<20} {'Taxable Income':<22} {'Total Tax':<18} {'Recommended?'}")
    separator(char="-")
    rec = result["recommended_regime"]
    star_new = clr("✓ RECOMMENDED", G) if rec=="new" else ""
    star_old = clr("✓ RECOMMENDED", G) if rec=="old" else ""
    print(f"  {'New Regime':<20} {fmt_inr(nr['taxable_income']):<22} {fmt_inr(nr['total_tax']):<18} {star_new}")
    print(f"  {'Old Regime':<20} {fmt_inr(or_['taxable_income']):<22} {fmt_inr(or_['total_tax']):<18} {star_old}")

    separator()
    print(f"\n  {G}{BOLD}Tax Saved by choosing right regime: {fmt_inr(result['tax_savings'])}{RST}")

    status = result["status"]
    val    = result["refund_or_payable"]
    status_color = G if status == "REFUND" else R
    label  = "Expected Refund" if status == "REFUND" else "Tax Payable"
    print(f"  {status_color}{BOLD}{label}: {fmt_inr(abs(val))}{RST}")

    print(f"\n{C}{BOLD}  DEDUCTION BREAKUP (Old Regime):{RST}")
    for k, v in or_["deduction_breakup"].items():
        if v > 0:
            print(f"    • {k.replace('_',' ').title():<28} {fmt_inr(v)}")

    print(f"\n{Y}{BOLD}  💡 TAX SAVING TIPS:{RST}")
    for t in tips[:4]:
        print(f"    {t}")

def run_budget_planner():
    separator("BUDGET PLANNER & WEALTH PROJECTOR")
    print(f"\n  {DIM}Demo profile — Monthly Income: ₹85,000{RST}\n")

    income   = 85000
    expenses = {
        "Housing":       18000,
        "Food":          14000,
        "Transport":      7000,
        "Utilities":      4000,
        "Healthcare":     2500,
        "Entertainment":  6500,
        "Investments":   18000,
        "Savings":        9000,
    }

    result = analyze_budget(income, expenses)
    save_budget(income, expenses, result)

    print(f"  {'Category':<18}{'Spent':>10}{'Ideal':>10}{'Actual%':>9}{'Ideal%':>9}  {'Status'}")
    separator(char="─")

    for cat, data in result["analysis"].items():
        icon   = data["icon"]
        name   = f"{icon} {cat}"
        spent  = f"₹{data['spent']:,}"
        ideal  = f"₹{data['ideal']:,.0f}"
        ap     = f"{data['actual_pct']}%"
        ip     = f"{data['ideal_pct']}%"
        st     = data["status"]
        st_c   = R if st=="overspending" else (G if st=="on_track" else Y)
        st_s   = clr(st.replace("_"," ").upper(), st_c)
        print(f"  {name:<18}{spent:>10}{ideal:>10}{ap:>9}{ip:>9}  {st_s}")

    separator()
    surplus_c = G if result["surplus"] >= 0 else R
    print(f"\n  Monthly Surplus:  {clr(fmt_inr(result['surplus']), surplus_c)}")
    print(f"  Financial Health: {clr(result['grade'], C)} (Score: {result['health_score']}/100)")

    if result["alerts"]:
        print(f"\n{Y}{BOLD}  ALERTS:{RST}")
        for a in result["alerts"]:
            print(f"    {a}")

    print(f"\n{G}{BOLD}  SMART TIPS:{RST}")
    for t in result["tips"]:
        print(f"    {t}")

    # SIP allocation
    monthly_inv = expenses["Investments"]
    sip = suggest_sip_allocation(monthly_inv)
    print(f"\n{C}{BOLD}  RECOMMENDED SIP ALLOCATION (₹{monthly_inv:,}/month):{RST}")
    for s in sip:
        print(f"    {s['pct']:2d}% → {s['fund']:<35} ₹{s['amount']:,.0f}/mo  [{s['type']}]")

    # Wealth projection
    print(f"\n{C}{BOLD}  WEALTH PROJECTION (at current SIP):{RST}")
    for yr in [5, 10, 20, 30]:
        p = project_wealth(monthly_inv, yr)
        print(f"    {yr:2d} years → Invested: {fmt_inr(p['total_invested']):<14} "
              f"Future Value: {clr(fmt_inr(p['future_value']), G)}")

def main():
    init_db()
    banner()

    print(f"  {C}SELECT MODULE:{RST}")
    print(f"    {W}[1]{RST} Stock Intelligence & Signals")
    print(f"    {W}[2]{RST} Tax Calculator (FY 2025-26)")
    print(f"    {W}[3]{RST} Budget Planner & Wealth Projector")
    print(f"    {W}[4]{RST} Run ALL modules\n")

    choice = input(f"  {C}Enter choice (1-4): {RST}").strip()

    if choice == "1":
        run_stock_analysis()
    elif choice == "2":
        run_tax_calculator()
    elif choice == "3":
        run_budget_planner()
    elif choice == "4":
        run_stock_analysis()
        print()
        run_tax_calculator()
        print()
        run_budget_planner()
    else:
        print(f"  {R}Invalid choice.{RST}")
        return

    print(f"\n{DIM}  {APP_CREDIT} | QUALA v{APP_VERSION}{RST}\n")

if __name__ == "__main__":
    main()
