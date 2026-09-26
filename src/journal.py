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


def load_cached_ohlc_by_ticker(cache_dir: Path, ticker: str):
    """Load a cache filename stem's daily OHLC as a pandas DataFrame indexed
    by date, or None if no cache file exists for it."""
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


def load_cached_ohlc(cache_dir: Path, pair: str):
    """Load a pair's cached daily OHLC as a pandas DataFrame indexed by date,
    or None if no cache file exists for it."""
    return load_cached_ohlc_by_ticker(cache_dir, pair_to_cache_ticker(pair))


# Secondary/macro assets a trade's reasoning can point to (oil driving CAD,
# DXY driving a USD pair, broad risk sentiment via the S&P or VIX, a specific
# yield). Keyed by the short tag used in an entry's "context" list; each maps
# to the price_cache/{cache}.json file to read and a display label for the
# chart title. SPX reuses the same cache file as the SPX500-pair trades.
CONTEXT_ASSETS = {
    "WTI": ("WTI", "WTI Crude Oil"),
    "DXY": ("DXY", "US Dollar Index (DXY)"),
    "US10Y": ("US10Y", "US 10-Year Treasury Yield"),
    "SPX": ("SPX500", "S&P 500"),
    "VIX": ("VIX", "CBOE Volatility Index (VIX)"),
}


def _render_range_close_chart(df, center: "any", window_days: int, title: str,
                               out_path: Path, vline_color: str | None) -> bool:
    """Shared renderer: a window_days-wide window of df around `center`,
    each day's high/low range as a colour-coded bar (green/red by whether
    that day's close rose or fell from the previous close — this stays
    meaningful even on tickers where Yahoo's daily open/close degenerate,
    see render_trade_chart), the close plotted as a line on top, and
    optionally a dashed vertical line at the nearest trading day to
    `center`. Returns False (no file written) if the window has no rows."""
    import pandas as pd
    center = pd.Timestamp(center)
    lo, hi = center - pd.Timedelta(days=window_days), center + pd.Timedelta(days=window_days)
    pre = df.loc[df.index < lo]
    window = df.loc[(df.index >= lo) & (df.index <= hi)]
    if window.empty:
        return False
    prev_close = pre["Close"].iloc[-1] if not pre.empty else None

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

    if vline_color:
        nearest_idx = window.index[(window.index - center).map(lambda td: abs(td.days)).argmin()]
        ax.axvline(nearest_idx, color=vline_color, linestyle="--", linewidth=1.4, zorder=4)

    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
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

    r = entry.get("r")
    if r is not None and r > 0:
        entry_color = COLOR_WIN
    elif r is not None and r < 0:
        entry_color = COLOR_LOSS
    else:
        entry_color = COLOR_NEUTRAL

    direction = entry.get("direction")
    arrow = {"long": "▲", "short": "▼"}.get(direction, "")
    title = f"{pair} — {d.strftime('%b %d, %Y')} {arrow}".strip()

    return _render_range_close_chart(df, d, window_days, title, out_path, entry_color)


def render_context_chart(cache_dir: Path, context_key: str, date_str: str, out_path: Path,
                          window_days: int = 15) -> bool:
    """Render the same style of chart as render_trade_chart, but for a
    secondary/macro asset (oil, DXY, S&P, VIX, a yield) that a trade's
    reasoning explicitly points to, rather than the traded pair itself.
    `context_key` is a key into CONTEXT_ASSETS. No entry outcome to colour
    the marker by, so the date line (if any date is given) is neutral grey.
    Returns False if the key is unknown, the date is missing/coarse, there's
    no cache for it, or the window has no rows.
    """
    if context_key not in CONTEXT_ASSETS:
        return False
    ticker, label = CONTEXT_ASSETS[context_key]
    if not date_str or len(date_str) != 10:
        return False
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False

    df = load_cached_ohlc_by_ticker(cache_dir, ticker)
    if df is None or df.empty:
        return False

    title = f"{label} — {d.strftime('%b %d, %Y')}"
    return _render_range_close_chart(df, d, window_days, title, out_path, COLOR_NEUTRAL)


# --------------------------------------------------------------------------- #
# Economic calendar (from cached Forex Factory scrapes)
# --------------------------------------------------------------------------- #
#
# Raw calendar rows for a given day are scraped ahead of time from
# forexfactory.com/calendar and cached as data/ff_calendar/{day}.json — a
# JSON array of {time, currency, impact, event, actual, forecast, previous}
# objects, `impact` being the site's own CSS class ("...impact-red/ora/yel").
# This module only reads that local cache; it never calls the network.

FF_CURRENCY_OVERRIDES = {
    "XAUUSD": ["USD"],
    "SPX500": ["USD"],
    "US500": ["USD"],
    "NAS100": ["USD"],
    "US30": ["USD"],
    "GER40": ["EUR"],
    "UK100": ["GBP"],
}

FF_IMPACT_COLORS = {
    "red": "#d64545",
    "ora": "#e08a2c",
    "yel": "#d4b106",
}


def pair_to_ff_currencies(pair: str) -> list[str]:
    """Which Forex Factory currency codes matter for this pair, e.g.
    'AUD/CAD' -> ['AUD', 'CAD'], 'XAUUSD' -> ['USD']."""
    if not pair:
        return []
    p = re.sub(r"\s*\(.*?\)\s*", "", pair).replace("/", "").strip().upper()
    if p in FF_CURRENCY_OVERRIDES:
        return FF_CURRENCY_OVERRIDES[p]
    if len(p) == 6:
        return [p[:3], p[3:]]
    return []


def _impact_color(impact_class: str) -> str:
    for key, color in FF_IMPACT_COLORS.items():
        if key in (impact_class or ""):
            return color
    return "#9aa0a6"  # grey: holiday / non-economic entries


def load_cached_calendar(cache_dir: Path, date_str: str) -> list[dict]:
    """Load the raw scraped FF calendar rows for one day, or [] if there's no
    cache file for it."""
    path = Path(cache_dir) / f"{date_str}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def render_calendar_table(events: list[dict], date_str: str, out_path: Path) -> bool:
    """Render a compact table of economic-calendar events (already filtered
    to the currencies relevant to a trade) as a PNG in the journal's visual
    style: a coloured dot for each event's impact (red/orange/yellow, grey
    for non-economic), then time, currency, event, actual, forecast and
    previous. Returns False when there are no events to show."""
    if not events:
        return False
    d = datetime.strptime(date_str, "%Y-%m-%d")
    n = len(events)

    row_h_in = 0.32
    header_in = 0.5
    fig_h = header_in + row_h_in * n + 0.15
    fig, ax = plt.subplots(figsize=(7.2, fig_h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0, 1.0, f"Economic calendar — {d.strftime('%b %d, %Y')}",
            fontsize=11, fontweight="bold", ha="left", va="top", transform=ax.transAxes)

    cols = [("time", 0.045, "left"), ("currency", 0.145, "left"), ("event", 0.215, "left"),
            ("actual", 0.72, "right"), ("forecast", 0.855, "right"), ("previous", 1.0, "right")]
    headers = {"time": "Time", "currency": "Cur", "event": "Event",
               "actual": "Actual", "forecast": "Forecast", "previous": "Previous"}

    header_frac = header_in / fig_h
    top = 1 - header_frac
    row_step = top / n

    hy = top + row_step * 0.25
    for key, x, ha in cols:
        ax.text(x, hy, headers[key], fontsize=8.3, fontweight="bold", color="#666666",
                ha=ha, va="bottom", transform=ax.transAxes)
    ax.axhline(top + row_step * 0.05, xmin=0, xmax=1, color=COLOR_GRID, linewidth=0.8)

    def _clip(text: str, n_chars: int) -> str:
        text = text or "—"
        return text if len(text) <= n_chars else text[: n_chars - 1] + "…"

    for i, ev in enumerate(events):
        y = top - row_step * (i + 0.9)
        color = _impact_color(ev.get("impact", ""))
        ax.scatter([0.012], [y + row_step * 0.12], s=20, color=color,
                   transform=ax.transAxes, clip_on=False, zorder=3)
        ax.text(cols[0][1], y, ev.get("time") or "—", fontsize=8.3, ha="left", va="center",
                transform=ax.transAxes)
        ax.text(cols[1][1], y, ev.get("currency", ""), fontsize=8.3, fontweight="bold",
                ha="left", va="center", transform=ax.transAxes)
        ax.text(cols[2][1], y, _clip(ev.get("event", ""), 46), fontsize=8.3,
                ha="left", va="center", transform=ax.transAxes)
        ax.text(cols[3][1], y, ev.get("actual") or "—", fontsize=8.3, ha="right", va="center",
                transform=ax.transAxes)
        ax.text(cols[4][1], y, ev.get("forecast") or "—", fontsize=8.3, ha="right", va="center",
                transform=ax.transAxes)
        ax.text(cols[5][1], y, ev.get("previous") or "—", fontsize=8.3, ha="right", va="center",
                transform=ax.transAxes)
        if i < n - 1:
            ax.axhline(y - row_step * 0.5, xmin=0, xmax=1, color=COLOR_GRID,
                       linewidth=0.5, alpha=0.6)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return True


def render_trade_calendar(ff_cache_dir: Path, entry: dict, out_path: Path) -> bool:
    """Convenience wrapper: load the cached FF calendar for entry['date'],
    filter to the currencies relevant to entry['pair'], and render it.
    Returns False if there's no exact date, no cache for that day, or
    nothing left after filtering to the relevant currencies."""
    date_str = entry.get("date")
    pair = entry.get("pair")
    if not date_str or len(date_str) != 10 or not pair:
        return False
    currencies = set(pair_to_ff_currencies(pair))
    if not currencies:
        return False
    all_events = load_cached_calendar(ff_cache_dir, date_str)
    events = [e for e in all_events if e.get("currency") in currencies]
    return render_calendar_table(events, date_str, out_path)
