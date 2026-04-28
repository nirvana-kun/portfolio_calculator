"""
Portfolio Returns & Risk Calculator
Tracks a simple investment portfolio, calculates
returns, volatility, Sharpe ratio, and max drawdown.
"""

import json
import csv
import datetime
import sys
import os
import math

SAMPLE_PORTFOLIO = {
    "name": "Sample Growth Portfolio",
    "currency": "EUR",
    "risk_free_rate_annual_pct": 3.5,
    "positions": [
        {"ticker": "ASML",  "name": "ASML Holding",       "shares": 10,  "avg_cost": 650.00,  "current_price": 820.00,  "weight_target_pct": 25},
        {"ticker": "NVDA",  "name": "NVIDIA",              "shares": 15,  "avg_cost": 480.00,  "current_price": 875.00,  "weight_target_pct": 20},
        {"ticker": "SAP",   "name": "SAP SE",              "shares": 20,  "avg_cost": 135.00,  "current_price": 178.00,  "weight_target_pct": 15},
        {"ticker": "BNP",   "name": "BNP Paribas",         "shares": 50,  "avg_cost": 58.00,   "current_price": 62.00,   "weight_target_pct": 10},
        {"ticker": "MC",    "name": "LVMH",                "shares": 5,   "avg_cost": 780.00,  "current_price": 695.00,  "weight_target_pct": 15},
        {"ticker": "CASH",  "name": "Cash (EUR)",          "shares": 1,   "avg_cost": 5000.00, "current_price": 5000.00, "weight_target_pct": 15},
    ],
    "monthly_returns_pct": [
        {"month": "2025-01", "portfolio": 3.2,  "benchmark": 2.8},
        {"month": "2025-02", "portfolio": -1.4, "benchmark": -0.9},
        {"month": "2025-03", "portfolio": 4.1,  "benchmark": 3.5},
        {"month": "2025-04", "portfolio": 2.7,  "benchmark": 1.9},
        {"month": "2025-05", "portfolio": -2.1, "benchmark": -1.5},
        {"month": "2025-06", "portfolio": 5.3,  "benchmark": 4.1},
        {"month": "2025-07", "portfolio": 1.8,  "benchmark": 2.2},
        {"month": "2025-08", "portfolio": -0.7, "benchmark": 0.3},
    ]
}


def mean(values):
    return sum(values) / len(values) if values else 0


def std_dev(values):
    if len(values) < 2:
        return 0
    avg = mean(values)
    variance = sum((v - avg) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def max_drawdown(returns_pct):
    cumulative = [1.0]
    for r in returns_pct:
        cumulative.append(cumulative[-1] * (1 + r / 100))

    peak = cumulative[0]
    max_dd = 0
    for val in cumulative:
        if val > peak:
            peak = val
        dd = (val - peak) / peak * 100
        if dd < max_dd:
            max_dd = dd
    return round(max_dd, 2)


def sharpe_ratio(returns_pct, risk_free_annual_pct):
    monthly_rf = risk_free_annual_pct / 12
    excess = [r - monthly_rf for r in returns_pct]
    if std_dev(excess) == 0:
        return 0
    monthly_sharpe = mean(excess) / std_dev(excess)
    return round(monthly_sharpe * math.sqrt(12), 2)


def cumulative_return(returns_pct):
    result = 1.0
    for r in returns_pct:
        result *= (1 + r / 100)
    return round((result - 1) * 100, 2)


def format_eur(n):
    if abs(n) >= 1_000_000:
        return f"€{n/1_000_000:.2f}M"
    elif abs(n) >= 1_000:
        return f"€{n/1_000:.1f}k"
    return f"€{n:,.2f}"


def format_pct(n, decimals=2):
    sign = "+" if n > 0 else ""
    return f"{sign}{n:.{decimals}f}%"


def print_report(data: dict):
    sep = "=" * 70
    thin = "-" * 70
    positions = data["positions"]
    returns_data = data["monthly_returns_pct"]
    rf_rate = data["risk_free_rate_annual_pct"]

    # Portfolio valuation
    total_cost = sum(p["shares"] * p["avg_cost"] for p in positions)
    total_value = sum(p["shares"] * p["current_price"] for p in positions)
    total_pnl = total_value - total_cost
    total_return_pct = (total_pnl / total_cost * 100) if total_cost else 0

    port_returns = [r["portfolio"] for r in returns_data]
    bench_returns = [r["benchmark"] for r in returns_data]

    port_cumulative = cumulative_return(port_returns)
    bench_cumulative = cumulative_return(bench_returns)
    port_vol = round(std_dev(port_returns) * math.sqrt(12), 2)
    port_sharpe = sharpe_ratio(port_returns, rf_rate)
    port_drawdown = max_drawdown(port_returns)
    alpha = round(port_cumulative - bench_cumulative, 2)

    print(f"\n{sep}")
    print(f"  PORTFOLIO RETURNS & RISK CALCULATOR")
    print(f"  {data['name']}")
    print(f"  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{sep}")

    print(f"\n  PORTFOLIO SUMMARY")
    print(f"  {thin}")
    print(f"  Total cost basis : {format_eur(total_cost)}")
    print(f"  Current value    : {format_eur(total_value)}")
    print(f"  Unrealised P&L   : {format_eur(total_pnl)}  ({format_pct(total_return_pct)})")

    print(f"\n  POSITIONS")
    print(f"  {thin}")
    print(f"  {'TICKER':<7} {'NAME':<22} {'SHARES':>6} {'COST':>9} {'PRICE':>9} "
          f"{'VALUE':>10} {'P&L':>10} {'RETURN':>8} {'WEIGHT':>7}")
    print(f"  {'-'*6} {'-'*21} {'-'*6} {'-'*9} {'-'*9} {'-'*10} {'-'*10} {'-'*8} {'-'*7}")

    for p in positions:
        cost = p["shares"] * p["avg_cost"]
        value = p["shares"] * p["current_price"]
        pnl = value - cost
        ret_pct = (pnl / cost * 100) if cost else 0
        weight = value / total_value * 100 if total_value else 0
        drift = weight - p["weight_target_pct"]
        drift_flag = " !" if abs(drift) > 5 else ""
        print(f"  {p['ticker']:<7} {p['name']:<22} {p['shares']:>6} "
              f"€{p['avg_cost']:>8,.2f} €{p['current_price']:>8,.2f} "
              f"{format_eur(value):>10} {format_eur(pnl):>10} "
              f"{format_pct(ret_pct, 1):>8} {weight:>6.1f}%{drift_flag}")

    print(f"\n  PERFORMANCE METRICS ({len(returns_data)} months)")
    print(f"  {thin}")
    print(f"  {'METRIC':<35} {'PORTFOLIO':>12} {'BENCHMARK':>12}")
    print(f"  {'-'*34} {'-'*12} {'-'*12}")
    print(f"  {'Cumulative return':<35} {format_pct(port_cumulative):>12} {format_pct(bench_cumulative):>12}")
    print(f"  {'Annualised volatility':<35} {port_vol:>11.2f}%           —")
    print(f"  {'Sharpe ratio (annualised)':<35} {port_sharpe:>12.2f}           —")
    print(f"  {'Max drawdown':<35} {format_pct(port_drawdown):>12}           —")
    print(f"  {'Alpha vs benchmark':<35} {format_pct(alpha):>12}           —")
    print(f"  {'Risk-free rate (annual)':<35} {rf_rate:>11.1f}%           —")

    print(f"\n  MONTH-BY-MONTH RETURNS")
    print(f"  {thin}")
    print(f"  {'MONTH':<10} {'PORTFOLIO':>10} {'BENCHMARK':>12} {'ALPHA':>8} SPARKLINE")
    print(f"  {'-'*9} {'-'*10} {'-'*12} {'-'*8} {'-'*15}")

    cum_p = 1.0
    for r in returns_data:
        cum_p *= (1 + r["portfolio"] / 100)
        alpha_m = round(r["portfolio"] - r["benchmark"], 2)
        bar_val = r["portfolio"]
        bar = ("▲" if bar_val > 0 else "▼") * min(5, int(abs(bar_val)))
        print(f"  {r['month']:<10} {format_pct(r['portfolio']):>10} "
              f"{format_pct(r['benchmark']):>12} {format_pct(alpha_m):>8} {bar}")

    print(f"\n  Cumulative portfolio value (normalised to 100):")
    cum = 100.0
    for r in returns_data:
        cum *= (1 + r["portfolio"] / 100)
        bar_len = max(0, min(50, int(cum / 4)))
        print(f"  {r['month']}  {'█' * bar_len}  {cum:.1f}")

    # Rebalancing flags
    print(f"\n  {thin}")
    drifted = []
    for p in positions:
        value = p["shares"] * p["current_price"]
        weight = value / total_value * 100 if total_value else 0
        drift = weight - p["weight_target_pct"]
        if abs(drift) > 5:
            direction = "overweight" if drift > 0 else "underweight"
            drifted.append(f"{p['ticker']}: {direction} by {abs(drift):.1f}% vs target")

    if drifted:
        print(f"  REBALANCING FLAGS")
        for d in drifted:
            print(f"  ! {d}")
    else:
        print(f"  REBALANCING: No positions outside ±5% of target weight.")

    print(f"\n{sep}\n")


def main():
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
    else:
        print("No JSON provided. Running with built-in sample portfolio.")
        print("Usage: python3 portfolio_calculator.py portfolio.json\n")
        data = SAMPLE_PORTFOLIO

    print_report(data)

    save = input("Save report as JSON? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"portfolio_report_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved to {filename}")


if __name__ == "__main__":
    main()
