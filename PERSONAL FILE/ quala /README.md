# QUALA — AI Financial Intelligence Engine
**Made by Yaskin's** | v1.0.0

## What QUALA Does
QUALA is a full AI-powered personal finance system with 3 core engines:

### 1. Stock Intelligence Engine (`core/signal_engine.py`)
- Reads 15 NSE/NASDAQ stocks
- NLP sentiment analysis on financial news (FinBERT-style rules)
- Detects events: earnings, policy, geopolitical, regulatory, innovation
- Fuses NLP score (55%) + Technical indicators (45%)
- Outputs: BUY/SELL/HOLD + confidence % + risk level

### 2. Tax Intelligence Engine (`core/tax_engine.py`)
- Old Regime vs New Regime comparison (FY 2025-26)
- Auto-computes: 80C, 80D, NPS, HRA, Home Loan deductions
- Section 87A rebate applied
- Calculates exact refund or payable amount
- Personalized tax saving tips

### 3. Budget Planner (`core/budget_engine.py`)
- Zero-based budget analysis
- Financial health score (0-100)
- Smart alerts for overspending
- SIP allocation recommendation
- Wealth projection (Geometric Brownian Motion + compound returns)

## How to Run

```bash
# Interactive CLI (full terminal experience)
python3 quala_cli.py

# Generate HTML report
python3 -c "
import sys; sys.path.insert(0,'.')
from web.report_generator import generate_report
generate_report('quala_report.html')
"
```

## Architecture
```
quala/
├── core/
│   ├── config.py          # Stocks, sectors, tax slabs, budgets
│   ├── market_data.py     # Price simulation + RSI/MACD/Bollinger
│   ├── nlp_engine.py      # Sentiment analysis + event detection
│   ├── signal_engine.py   # BUY/SELL/HOLD signal fusion
│   ├── tax_engine.py      # India tax calculator
│   ├── budget_engine.py   # Budget + SIP + wealth projector
│   └── database.py        # SQLite persistence
├── web/
│   └── report_generator.py # Full HTML report generator
├── quala_cli.py            # Interactive CLI
└── quala_report.html       # Pre-generated full report
```

## Production Upgrade Path
| Current (Local) | Production Upgrade |
|---|---|
| GBM price simulation | yfinance / NSE API |
| Rule-based NLP | FinBERT / HuggingFace |
| Sample news | NewsAPI / Bloomberg feed |
| SQLite | PostgreSQL |
| CLI | React/Next.js dashboard |
| Static HTML | Live streaming dashboard |

## Tech Stack
- **Language**: Python 3.12 (zero external dependencies)
- **NLP**: Custom rule-based + intensifier/negator-aware lexicon
- **Technicals**: RSI-14, MACD(12,26,9), Bollinger Bands(20), SMA20/50
- **Simulation**: Geometric Brownian Motion
- **Storage**: SQLite
- **Report**: Self-contained HTML

---
*QUALA is for educational/research use. Not SEBI registered. Not financial advice.*
