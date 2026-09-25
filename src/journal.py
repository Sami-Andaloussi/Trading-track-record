"""
journal.py — shared helpers for the trading journal notebooks.

Each notebook embeds its own `entries` list directly (no external data file is
read at runtime). This module only provides generic, reusable helpers on top
of that list: computing simple stats and drawing consistent, clean charts. It
has no dependency on anything outside this repo.

Entry schema (see README for the full write-up):
    {
        "pair": str,
        "direction": "long" | "short" | None,
        "status": "closed" | "open" | "skipped",
        "r": float | None,          # realized R, only meaningful when status == "closed"
        "floating_r": float | None, # unrealized R, only meaningful when status == "open"
        "date": str | None,         # ISO date, or a coarser "YYYY-MM" string, or None
        "title": str,
        "body": str,                # markdown
    }
"""
from __future__ import annotations

import os
import re
from datetime import datetime

import matplotlib.pyplot as plt

# --------------------------------------------------------------------------- #
# Look & feel
# --------------------------------------------------------------------------- #

COLOR_WIN = "#1f9d55"
COLOR_LOSS = "#d64545"
COLOR_NEUTRAL = "#4a5568"
COLOR_LINE = "#2c3e50"
COLOR_GRID = "#d9d9d9"

plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": COLOR_GRID,
    "grid.linewidth": 0.6,
    "grid.alpha": 0.6,
    "font.size": 10.5,
})


def _style_axes(ax):
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


# --------------------------------------------------------------------------- #
# Stats
# --------------------------------------------------------------------------- #

def sort_key(entry: dict):
    d = entry.get("date")
    if not d:
        return "9999-99-99"
    return d


def closed_entries(entries: list[dict]) -> list[dict]:
    """Entries that are closed AND have a realized R value logged."""
    return sorted(
        [e for e in entries if e.get("status") == "closed" and e.get("r") is not None],
        key=sort_key,
    )


def open_entries(entries: list[dict]) -> list[dict]:
    return [e for e in entries if e.get("status") == "open"]


def skipped_entries(entries: list[dict]) -> list[dict]:
    return [e for e in entries if e.get("status") == "skipped"]


def total_r(entries: list[dict]) -> float:
    return round(sum(e["r"] for e in closed_entries(entries)), 4)


def win_loss_counts(entries: list[dict]) -> tuple[int, int]:
    ce = closed_entries(entries)
    wins = sum(1 for e in ce if e["r"] > 0)
    losses = sum(1 for e in ce if e["r"] < 0)
    return wins, losses


def r_series(entries: list[dict]) -> list[float]:
    return [e["r"] for e in closed_entries(entries)]


def equity_curve(r_values: list[float]) -> list[float]:
    out, total = [], 0.0
    for r in r_values:
        total += r
        out.append(total)
    return out


def summary_line(entries: list[dict]) -> str:
    wins, losses = win_loss_counts(entries)
    n_open = len(open_entries(entries))
    n_skipped = len(skipped_entries(entries))
    parts = [f"{total_r(entries):+.2f}R logged", f"{wins}W/{losses}L"]
    if n_open:
        parts.append(f"{n_open} open")
    if n_skipped:
        parts.append(f"{n_skipped} passed on")
    return " · ".join(parts)


# --------------------------------------------------------------------------- #
# Charts
# --------------------------------------------------------------------------- #

def plot_r_bars(entries: list[dict], title: str):
    ce = closed_entries(entries)
    if not ce:
        print("No closed, R-logged trades to chart for this period.")
        return
    labels = [e["pair"] for e in ce]
    values = [e["r"] for e in ce]
    colors = [COLOR_WIN if v >= 0 else COLOR_LOSS for v in values]

    fig, ax = plt.subplots(figsize=(max(6, 0.9 * len(values) + 2), 3.4))
    bars = ax.bar(range(len(values)), values, color=colors, width=0.6, edgecolor="white", linewidth=0.5)
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("R")
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    for b, v in zip(bars, values):
        ax.annotate(f"{v:+.2f}", (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4 if v >= 0 else -12),
                    ha="center", fontsize=8.5, color="#333333")
    _style_axes(ax)
    plt.tight_layout()
    plt.show()


def plot_equity_curve(entries: list[dict], title: str):
    ce = closed_entries(entries)
    if not ce:
        return
    curve = equity_curve([e["r"] for e in ce])
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(range(1, len(curve) + 1), curve, marker="o", markersize=4.5,
            color=COLOR_LINE, linewidth=1.6)
    ax.fill_between(range(1, len(curve) + 1), curve, 0, alpha=0.06, color=COLOR_LINE)
    ax.axhline(0, color=COLOR_GRID, linewidth=1, linestyle="--")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("Cumulative R")
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    _style_axes(ax)
    plt.tight_layout()
    plt.show()


def plot_monthly_bars(labels: list[str], values: list[float], title: str):
    fig, ax = plt.subplots(figsize=(max(7, 0.6 * len(values) + 2), 3.6))
    colors = [COLOR_WIN if v >= 0 else COLOR_LOSS for v in values]
    ax.bar(range(len(values)), values, color=colors, width=0.62)
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("R")
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    _style_axes(ax)
    plt.tight_layout()
    plt.show()


def plot_monthly_equity(labels: list[str], values: list[float], title: str):
    curve = equity_curve(values)
    fig, ax = plt.subplots(figsize=(max(7, 0.6 * len(values) + 2), 3.6))
    ax.plot(range(len(curve)), curve, marker="o", markersize=5, color=COLOR_LINE, linewidth=1.8)
    ax.fill_between(range(len(curve)), curve, 0, alpha=0.06, color=COLOR_LINE)
    ax.axhline(0, color=COLOR_GRID, linewidth=1, linestyle="--")
    ax.set_xticks(range(len(curve)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Cumulative R")
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    _style_axes(ax)
    plt.tight_layout()
    plt.show()


# --------------------------------------------------------------------------- #
# Optional price context (Yahoo Finance, best-effort)
# --------------------------------------------------------------------------- #

YF_TICKER_OVERRIDES = {
    "XAUUSD": "GC=F",
    "SPX500": "^GSPC",
    "US500": "^GSPC",
    "NAS100": "^NDX",
    "US30": "^DJI",
    "GER40": "^GDAXI",
    "UK100": "^FTSE",
}


def asset_to_yf_ticker(pair: str) -> str | None:
    if not pair:
        return None
    a = re.sub(r"\s*\(.*?\)\s*", "", pair).replace("/", "").strip().upper()
    if a in YF_TICKER_OVERRIDES:
        return YF_TICKER_OVERRIDES[a]
    if re.fullmatch(r"[A-Z]{6}", a):
        return f"{a}=X"
    return None


def fetch_price_history(ticker: str, start: str, end: str):
    """Best-effort price fetch. Never raises — returns None if unavailable
    (no network, invalid ticker, etc.) so notebooks stay executable anywhere."""
    if os.environ.get("JOURNAL_SKIP_PRICE_CHARTS"):
        print(f"  [price charts skipped — no internet access in this environment]")
        return None
    try:
        import yfinance as yf
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:  # noqa: BLE001 - intentionally broad, see docstring
        print(f"  [price data unavailable for {ticker}: {type(e).__name__}]")
        return None


def plot_price_context(entry: dict):
    ticker = asset_to_yf_ticker(entry.get("pair", ""))
    date_str = entry.get("date")
    if not ticker or not date_str or len(date_str) != 10:
        return
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return
    import pandas as pd
    start = (d - pd.Timedelta(days=15)).strftime("%Y-%m-%d")
    end = (d + pd.Timedelta(days=15)).strftime("%Y-%m-%d")
    hist = fetch_price_history(ticker, start, end)
    if hist is None:
        return
    close_col = "Close" if "Close" in hist.columns else hist.columns[0]
    fig, ax = plt.subplots(figsize=(7, 2.6))
    ax.plot(hist.index, hist[close_col], color=COLOR_LINE, linewidth=1.4)
    ax.axvline(d, color=COLOR_LOSS if entry.get("r", 0) and entry["r"] < 0 else COLOR_WIN,
               linestyle="--", linewidth=1.2, label="Entry")
    ax.set_title(f"{entry.get('pair')} around {date_str}", fontsize=10.5, fontweight="bold", loc="left")
    ax.legend(frameon=False, fontsize=8.5)
    _style_axes(ax)
    plt.tight_layout()
    plt.show()
