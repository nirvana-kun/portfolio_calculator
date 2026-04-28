# Portfolio Returns & Risk Calculator

Tracks an investment portfolio, calculates returns, volatility, Sharpe ratio, maximum drawdown, and alpha vs a benchmark. Flags positions that have drifted from target weights.

---

## What It Does

- Calculates unrealised P&L and total return per position and portfolio-wide
- Computes annualised volatility, Sharpe ratio, and maximum drawdown from monthly returns
- Benchmarks portfolio performance against an index and calculates alpha
- Renders a month-by-month returns table with sparklines
- Flags positions that have drifted more than 5% from their target weight (rebalancing signal)
- Normalised cumulative value chart in the terminal

## How to Run

```bash
# Run with built-in sample portfolio (European equities)
python3 portfolio_calculator.py

# Run with your own portfolio JSON
python3 portfolio_calculator.py my_portfolio.json
```

No installs required. Pure Python 3 standard library.

## Key Metrics Explained

**Sharpe Ratio** — excess return per unit of risk (annualised). Above 1.0 is generally considered good; above 2.0 is strong.

**Max Drawdown** — the largest peak-to-trough decline over the period. Measures downside risk.

**Alpha** — portfolio return minus benchmark return over the same period. Positive alpha means the portfolio outperformed.

**Annualised Volatility** — standard deviation of monthly returns scaled to annual (× √12).

## Sample Output

```
======================================================================
  PORTFOLIO RETURNS & RISK CALCULATOR
  Sample Growth Portfolio
======================================================================

  POSITIONS
----------------------------------------------------------------------
  TICKER  NAME                   SHARES   COST      PRICE     VALUE      P&L       RETURN  WEIGHT
  ASML    ASML Holding               10  €650.00   €820.00   €8,200    €1,700    +26.2%   22.1%
  NVDA    NVIDIA                     15  €480.00   €875.00  €13,125    €5,925    +82.3%   35.4% !
  ...

  PERFORMANCE METRICS (8 months)
----------------------------------------------------------------------
  METRIC                               PORTFOLIO    BENCHMARK
  Cumulative return                       +13.9%        +12.4%
  Annualised volatility                     9.2%            —
  Sharpe ratio (annualised)                 1.84            —
  Max drawdown                             -2.8%           —
  Alpha vs benchmark                       +1.5%           —
```

## Input JSON Format

```json
{
  "name": "My Portfolio",
  "risk_free_rate_annual_pct": 3.5,
  "positions": [
    {
      "ticker": "ASML",
      "name": "ASML Holding",
      "shares": 10,
      "avg_cost": 650.00,
      "current_price": 820.00,
      "weight_target_pct": 25
    }
  ],
  "monthly_returns_pct": [
    {"month": "2025-01", "portfolio": 3.2, "benchmark": 2.8}
  ]
}
```

## Stack

- Python 3.11+
- Standard library only (`json`, `csv`, `datetime`, `math`, `sys`, `os`)
