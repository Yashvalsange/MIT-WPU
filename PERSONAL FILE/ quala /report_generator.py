"""
QUALA HTML Report Generator
Generates a full standalone HTML report with all three modules.
Made by Yaskin's
"""

import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.signal_engine  import run_full_analysis
from core.tax_engine     import compute_tax, get_tax_saving_tips
from core.budget_engine  import analyze_budget, suggest_sip_allocation, project_wealth
from core.database       import init_db, save_signals, save_tax, save_budget
from core.config         import APP_CREDIT, APP_VERSION


def generate_report(output_path: str = "/home/claude/quala/output/quala_report.html"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    init_db()

    # ── Run all engines ────────────────────────────────────────────────────────
    signals = run_full_analysis()
    save_signals(signals)

    tax_profile = {
        "gross_salary": 1200000, "hra_received": 180000, "rent_paid": 168000,
        "city_type": "metro", "deductions_80c": 150000, "deductions_80d": 25000,
        "nps_80ccd": 50000, "home_loan_interest": 200000,
        "education_loan_int": 0, "other_deductions": 0, "tds_deducted": 95000,
    }
    tax_result = compute_tax(tax_profile)
    tax_tips   = get_tax_saving_tips(tax_profile, tax_result)
    save_tax(tax_profile, tax_result)

    income   = 85000
    expenses = {
        "Housing": 18000, "Food": 14000, "Transport": 7000, "Utilities": 4000,
        "Healthcare": 2500, "Entertainment": 6500, "Investments": 18000, "Savings": 9000,
    }
    budget_result = analyze_budget(income, expenses)
    sip_alloc     = suggest_sip_allocation(expenses["Investments"])
    wealth_proj   = [project_wealth(expenses["Investments"], yr) for yr in [5, 10, 20, 30]]
    save_budget(income, expenses, budget_result)

    # ── Build HTML ─────────────────────────────────────────────────────────────
    generated_at = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    def sig_badge(s):
        c = "#10b981" if s=="BUY" else ("#ef4444" if s=="SELL" else "#f59e0b")
        return f'<span style="background:{c}22;color:{c};border:1px solid {c}44;padding:3px 10px;font-size:0.7rem;letter-spacing:1px;font-family:monospace">{s}</span>'

    def risk_badge(r):
        c = "#ef4444" if r=="HIGH" else ("#f59e0b" if r=="MEDIUM" else "#10b981")
        return f'<span style="color:{c};font-size:0.72rem">{r}</span>'

    def conf_bar(pct, color="#00e5ff"):
        return f'<div style="width:80px;height:4px;background:#1e2a3a;display:inline-block;vertical-align:middle"><div style="width:{pct}%;height:100%;background:{color}"></div></div> <span style="font-size:0.7rem;color:#6b7a8d">{pct}%</span>'

    def fmt(n):
        if abs(n) >= 1e7: return f"₹{n/1e7:.2f}Cr"
        if abs(n) >= 1e5: return f"₹{n/1e5:.2f}L"
        return f"₹{n:,.0f}"

    # Build signal rows
    signal_rows = ""
    for s in signals:
        sig_c = "#10b981" if s["signal"]=="BUY" else ("#ef4444" if s["signal"]=="SELL" else "#f59e0b")
        chg_c = "#10b981" if s["pct_change_30d"] > 0 else "#ef4444"
        chg_s = f'+{s["pct_change_30d"]:.1f}%' if s["pct_change_30d"] > 0 else f'{s["pct_change_30d"]:.1f}%'
        signal_rows += f"""
        <tr>
          <td style="color:#00e5ff;font-weight:700">{s['ticker']}</td>
          <td style="color:#c8d8e8">{s['name'][:22]}</td>
          <td style="color:#8892a0">{s['sector']}</td>
          <td>{s['currency']} {s['price']:,.1f}</td>
          <td>{sig_badge(s['signal'])}</td>
          <td>{conf_bar(s['confidence_pct'], sig_c)}</td>
          <td style="color:#c8d8e8">{s['rsi']:.1f}</td>
          <td style="color:{chg_c}">{chg_s}</td>
          <td>{risk_badge(s['risk'])}</td>
        </tr>"""

    # Build budget rows
    budget_rows = ""
    for cat, d in budget_result["analysis"].items():
        st_c = "#ef4444" if d["status"]=="overspending" else ("#10b981" if d["status"]=="on_track" else "#f59e0b")
        bar_w = min(100, int(d["actual_pct"] / d["ideal_pct"] * 100)) if d["ideal_pct"] else 0
        bar_c = "#ef4444" if d["status"]=="overspending" else "#10b981"
        budget_rows += f"""
        <tr>
          <td>{d['icon']} {cat}</td>
          <td>₹{d['spent']:,}</td>
          <td>₹{d['ideal']:,.0f}</td>
          <td>
            <div style="display:flex;align-items:center;gap:8px">
              <div style="width:80px;height:6px;background:#1e2a3a;flex-shrink:0">
                <div style="width:{bar_w}%;height:100%;background:{bar_c}"></div></div>
              <span style="color:{st_c};font-size:0.72rem">{d['actual_pct']}%</span>
            </div>
          </td>
          <td style="color:{st_c};font-size:0.72rem">{d['status'].replace('_',' ').upper()}</td>
        </tr>"""

    # Build SIP rows
    sip_rows = "".join(f"""<tr>
          <td style="color:#00e5ff">{s['pct']}%</td>
          <td>{s['fund']}</td>
          <td style="color:#8892a0">{s['type']}</td>
          <td style="color:#10b981">₹{s['amount']:,.0f}</td>
        </tr>""" for s in sip_alloc)

    # Build wealth rows
    wealth_rows = "".join(f"""<tr>
          <td style="color:#00e5ff">{p['years']} years</td>
          <td>₹{p['total_invested']:,.0f}</td>
          <td style="color:#10b981;font-weight:700">{fmt(p['future_value'])}</td>
          <td style="color:#f59e0b">{fmt(p['wealth_gained'])}</td>
        </tr>""" for p in wealth_proj)

    # Build tip items
    tip_items = "".join(f'<li style="padding:6px 0;border-bottom:1px solid rgba(99,210,255,0.06);font-size:0.83rem;color:#c8d8e8">{t}</li>' for t in tax_tips)
    budget_tip_items = "".join(f'<li style="padding:6px 0;border-bottom:1px solid rgba(99,210,255,0.06);font-size:0.83rem;color:#c8d8e8">{t}</li>' for t in budget_result["tips"])

    nr = tax_result["regime_new"]
    or_ = tax_result["regime_old"]
    rec = tax_result["recommended_regime"]
    refund_label = "Expected Refund" if tax_result["status"]=="REFUND" else "Tax Payable"
    refund_color = "#10b981" if tax_result["status"]=="REFUND" else "#ef4444"

    deduction_rows = "".join(
        f'<tr><td style="color:#8892a0">{k.replace("_"," ").title()}</td><td style="color:#10b981">₹{v:,.0f}</td></tr>'
        for k, v in or_["deduction_breakup"].items() if v > 0
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>QUALA — AI Financial Report</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700&display=swap" rel="stylesheet"/>
<style>
  :root{{--bg:#050810;--surface:#0c1120;--surface2:#111827;--border:rgba(99,210,255,0.1);--accent:#00e5ff;--text:#e8f4f8;--muted:#6b7a8d;}}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;line-height:1.6;}}
  body::before{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,229,255,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,0.02) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}}

  .wrap{{max-width:1200px;margin:0 auto;padding:40px 32px;position:relative;z-index:1;}}

  header{{text-align:center;padding:60px 0 40px;border-bottom:1px solid var(--border);margin-bottom:48px;}}
  .logo{{font-family:'Bebas Neue',sans-serif;font-size:5rem;letter-spacing:6px;background:linear-gradient(135deg,#00e5ff,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
  .tagline{{font-family:'DM Mono',monospace;font-size:0.7rem;letter-spacing:3px;color:var(--muted);text-transform:uppercase;margin-top:8px;}}
  .gen-time{{font-family:'DM Mono',monospace;font-size:0.65rem;color:var(--muted);margin-top:12px;}}

  .section{{margin-bottom:56px;}}
  .section-label{{font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:3px;color:var(--accent);text-transform:uppercase;margin-bottom:8px;}}
  .section-title{{font-family:'Bebas Neue',sans-serif;font-size:2.5rem;letter-spacing:2px;margin-bottom:24px;}}

  table{{width:100%;border-collapse:collapse;font-size:0.82rem;}}
  th{{font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:1px;text-transform:uppercase;color:var(--muted);padding:10px 12px;text-align:left;border-bottom:1px solid var(--border);background:var(--surface2);}}
  td{{padding:11px 12px;border-bottom:1px solid rgba(99,210,255,0.05);}}
  tr:hover td{{background:rgba(0,229,255,0.02);}}

  .card{{background:var(--surface);border:1px solid var(--border);padding:28px;}}
  .grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px;}}
  .grid-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:24px;}}
  .stat-card{{background:var(--surface);border:1px solid var(--border);padding:22px;}}
  .stat-label{{font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}}
  .stat-val{{font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:1px;}}

  .badge-buy{{background:#10b98122;color:#10b981;border:1px solid #10b98144;padding:3px 10px;font-size:0.65rem;letter-spacing:1px;font-family:monospace;}}
  .badge-sell{{background:#ef444422;color:#ef4444;border:1px solid #ef444444;padding:3px 10px;font-size:0.65rem;letter-spacing:1px;font-family:monospace;}}
  .badge-hold{{background:#f59e0b22;color:#f59e0b;border:1px solid #f59e0b44;padding:3px 10px;font-size:0.65rem;letter-spacing:1px;font-family:monospace;}}

  ul{{list-style:none;padding:0;margin:0;}}
  footer{{border-top:1px solid var(--border);padding:32px 0;text-align:center;margin-top:48px;}}
  .credit{{font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--muted);text-transform:uppercase;}}
  .credit span{{color:var(--accent);}}

  @media(max-width:768px){{.grid-2,.grid-4{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="logo">QUALA</div>
  <div class="tagline">AI Financial Intelligence Engine · Full Report</div>
  <div class="gen-time">Generated: {generated_at} &nbsp;|&nbsp; {APP_CREDIT}</div>
</header>

<!-- STOCK SIGNALS -->
<div class="section">
  <div class="section-label">// Module 01</div>
  <div class="section-title">STOCK INTELLIGENCE SIGNALS</div>

  <div class="grid-4">
    <div class="stat-card">
      <div class="stat-label">Total Stocks Analysed</div>
      <div class="stat-val" style="color:#00e5ff">{len(signals)}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Buy Signals</div>
      <div class="stat-val" style="color:#10b981">{len([s for s in signals if s['signal']=='BUY'])}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Sell Signals</div>
      <div class="stat-val" style="color:#ef4444">{len([s for s in signals if s['signal']=='SELL'])}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Hold Signals</div>
      <div class="stat-val" style="color:#f59e0b">{len([s for s in signals if s['signal']=='HOLD'])}</div>
    </div>
  </div>

  <div style="margin-top:24px;overflow-x:auto;">
  <table>
    <thead><tr>
      <th>Ticker</th><th>Name</th><th>Sector</th><th>Price</th>
      <th>Signal</th><th>Confidence</th><th>RSI</th><th>30D Chg</th><th>Risk</th>
    </tr></thead>
    <tbody>{signal_rows}</tbody>
  </table>
  </div>

  <div style="margin-top:24px;background:var(--surface);border:1px solid var(--border);padding:24px;">
    <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:16px;">⚡ Top Picks</div>
    {"".join(f'''<div style="margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid rgba(99,210,255,0.06)">
      <div style="color:#00e5ff;font-weight:700;font-size:0.9rem">{s["ticker"]} — {s["name"]} <span style="background:#10b98122;color:#10b981;border:1px solid #10b98144;padding:2px 10px;font-size:0.65rem;font-family:monospace;margin-left:8px">BUY {s["confidence_pct"]}%</span></div>
      {"".join(f'<div style="font-size:0.77rem;color:#6b7a8d;margin-top:4px">• {r[:90]}</div>' for r in s["reasons"][:2])}
    </div>''' for s in signals if s["signal"]=="BUY"[:3])}
  </div>
</div>

<!-- TAX -->
<div class="section">
  <div class="section-label">// Module 02</div>
  <div class="section-title">TAX INTELLIGENCE — FY 2025-26</div>

  <div class="grid-4">
    <div class="stat-card">
      <div class="stat-label">Gross Salary</div>
      <div class="stat-val" style="color:#00e5ff">{fmt(tax_profile['gross_salary'])}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Recommended Regime</div>
      <div class="stat-val" style="color:#10b981">{rec.upper()}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Tax Saved</div>
      <div class="stat-val" style="color:#10b981">{fmt(tax_result['tax_savings'])}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">{refund_label}</div>
      <div class="stat-val" style="color:{refund_color}">{fmt(abs(tax_result['refund_or_payable']))}</div>
    </div>
  </div>

  <div class="grid-2">
    <div class="card" style="margin-top:24px">
      <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:16px">Regime Comparison</div>
      <table>
        <thead><tr><th>Regime</th><th>Taxable Income</th><th>Total Tax</th><th></th></tr></thead>
        <tbody>
          <tr><td>New</td><td>{fmt(nr['taxable_income'])}</td><td>{fmt(nr['total_tax'])}</td>
            <td>{'<span class="badge-buy">PICK</span>' if rec=="new" else ""}</td></tr>
          <tr><td>Old</td><td>{fmt(or_['taxable_income'])}</td><td>{fmt(or_['total_tax'])}</td>
            <td>{'<span class="badge-buy">PICK</span>' if rec=="old" else ""}</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card" style="margin-top:24px">
      <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:16px">Deduction Breakup (Old)</div>
      <table><tbody>{deduction_rows}</tbody></table>
    </div>
  </div>

  <div class="card" style="margin-top:20px">
    <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:#f59e0b;text-transform:uppercase;margin-bottom:16px">💡 Tax Saving Tips</div>
    <ul>{tip_items}</ul>
  </div>
</div>

<!-- BUDGET -->
<div class="section">
  <div class="section-label">// Module 03</div>
  <div class="section-title">BUDGET PLANNER & WEALTH PROJECTOR</div>

  <div class="grid-4">
    <div class="stat-card">
      <div class="stat-label">Monthly Income</div>
      <div class="stat-val" style="color:#00e5ff">₹{income:,}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Spent</div>
      <div class="stat-val" style="color:#f59e0b">₹{budget_result['total_spent']:,}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Surplus</div>
      <div class="stat-val" style="color:#10b981">₹{budget_result['surplus']:,}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Health Score</div>
      <div class="stat-val" style="color:#10b981">{budget_result['health_score']}/100</div>
    </div>
  </div>

  <div class="grid-2">
    <div style="margin-top:24px;overflow-x:auto">
    <table>
      <thead><tr><th>Category</th><th>Spent</th><th>Ideal</th><th>Progress</th><th>Status</th></tr></thead>
      <tbody>{budget_rows}</tbody>
    </table>
    </div>
    <div>
      <div class="card" style="margin-top:24px">
        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:12px">Smart Tips</div>
        <ul>{budget_tip_items}</ul>
      </div>
    </div>
  </div>

  <div class="grid-2" style="margin-top:20px">
    <div class="card">
      <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:16px">SIP Allocation</div>
      <table><thead><tr><th>%</th><th>Fund</th><th>Type</th><th>Amount</th></tr></thead>
      <tbody>{sip_rows}</tbody></table>
    </div>
    <div class="card">
      <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--muted);text-transform:uppercase;margin-bottom:16px">Wealth Projection (12% CAGR)</div>
      <table><thead><tr><th>Horizon</th><th>Invested</th><th>Future Value</th><th>Gains</th></tr></thead>
      <tbody>{wealth_rows}</tbody></table>
    </div>
  </div>
</div>

<footer>
  <div class="credit">QUALA v{APP_VERSION} &nbsp;·&nbsp; <span>{APP_CREDIT}</span> &nbsp;·&nbsp; Not SEBI Registered · For Educational Use</div>
</footer>

</div>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    return output_path
