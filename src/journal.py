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

import json
import re
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
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
# Price context (daily candles, from the local price_cache/*.json files)
# --------------------------------------------------------------------------- #
#
# Historical daily OHLC is fetched ahead of time (via the Yahoo Finance chart
# API) and cached locally as data/price_cache/{TICKER}.json, one file per
# pair, each a JSON array of [date, open, high, low, close] rows. This module
# only ever reads those local files — it makes no network calls — so building
# the journal never depends on live internet access.

def pair_to_cache_ticker(pair: str) -> str | None:
    """Map a trade pair label (e.g. 'AUD/CAD', 'XAUUSD') to the price_cache
    filename stem (e.g. 'AUDCAD', 'XAUUSD') used when the data was fetched."""
    if not pair:
        return None
    return re.sub(r"\s*\(.*?\)\s*", "", pair).replace("/", "").strip().upper()


def load_cached_ohlc(cache_dir: Path, pair: str):
    """Load a pair's cached daily OHLC as a pandas DataFrame indexed by date,
    or None if no cache file exists for it."""
    ticker = pair_to_cache_ticker(pair)
    if not ticker:
        return None
    path = Path(cache_dir) / f"{ticker}.json"
    if not path.exists():
        return None
    import pandas as pd
    rows = json.loads(path.read_text())
    df = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date").sort_index()


def render_trade_chart(cache_dir: Path, entry: dict, out_path: Path, window_days: int = 15) -> bool:
    """Render a daily price-context chart spanning `window_days` on either
    side of entry['date'], mark the entry, and save it as a PNG at out_path.

    Yahoo's daily FX data frequently reports the same value for a day's open
    and close (a known quirk of its `=X` cross-rate feeds — futures and index
    tickers don't have it), which makes literal candlestick bodies degenerate
    into a thin dash for most days. Rather than draw misleading candles for
    some pairs and real ones for others, every chart uses one consistent
    style: each day's high/low range as a coloured bar (green/red by whether
    that day's close rose or fell from the previous close, which stays
    meaningful regardless of the open field) with the daily close plotted as
    a line on top, and the entry date marked with a dashed vertical line.

    Returns True on success, False when there's no exact date, no cached data
    for the pair, or no cached rows in range — callers should skip embedding
    an image in that case rather than treat it as an error.
    """
    date_str = entry.get("date")
    pair = entry.get("pair")
    if not date_str or len(date_str) != 10 or not pair:
        return False
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False

    df = load_cached_ohlc(cache_dir, pair)
    if df is None or df.empty:
        return False

    import pandas as pd
    d = pd.Timestamp(d)
    lo, hi = d - pd.Timedelta(days=window_days), d + pd.Timedelta(days=window_days)
    # Pull one extra prior row so the first bar in the window has a previous
    # close to compare against for its up/down colour.
    pre = df.loc[df.index < lo]
    window = df.loc[(df.index >= lo) & (df.index <= hi)]
    if window.empty:
        return False
    prev_close = pre["Close"].iloc[-1] if not pre.empty else None

    r = entry.get("r")
    if r is not None and r > 0:
        entry_color = COLOR_WIN
    elif r is not None and r < 0:
        entry_color = COLOR_LOSS
    else:
        entry_color = COLOR_NEUTRAL

    # Nearest trading day to the entry date (Yahoo has no weekend/holiday rows).
    nearest_idx = window.index[(window.index - d).map(lambda td: abs(td.days)).argmin()]

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    closes = window["Close"].tolist()
    for i, (idx, row) in enumerate(window.iterrows()):
        prior = closes[i - 1] if i > 0 else prev_close
        if prior is None:
            bar_color = COLOR_NEUTRAL
        else:
            bar_color = COLOR_WIN if row["Close"] >= prior else COLOR_LOSS
        ax.plot([idx, idx], [row["Low"], row["High"]], color=bar_color,
                linewidth=3.2, alpha=0.55, solid_capstyle="round")
    ax.plot(window.index, window["Close"], color=COLOR_LINE, linewidth=1.3,
            marker="o", markersize=2.6, zorder=3)
    ax.axvline(nearest_idx, color=entry_color, linestyle="--", linewidth=1.4, zorder=4)

    direction = entry.get("direction")
    arrow = {"long": "▲", "short": "▼"}.get(direction, "")
    ax.set_title(f"{pair} — {d.strftime('%b %d, %Y')} {arrow}".strip(),
                 fontsize=11, fontweight="bold", loc="left")
    ax.set_ylabel("Price")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8, minticks=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.tick_params(axis="x", rotation=0)
    _style_axes(ax)
    plt.tight_layout()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return True
