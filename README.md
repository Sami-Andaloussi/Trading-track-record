# Trading journal — Feb 2023 to Sep 2024

A written trading journal covering 20 months, February 2023 through September
2024. Each month is a set of first-person entries logged around the time of
the trade: the macro and technical reasoning behind it, how it was sized and
managed, and the outcome or lesson. The point of this isn't the R number —
it's building a record I can actually go back and read to spot patterns in
my own decision-making.

Each month is also available as a self-contained **Jupyter notebook**
(`notebooks/YYYY-MM.ipynb`), rolled up into **year-in-review** notebooks
(`notebooks/years/`) and one **full-history** notebook
(`notebooks/global_track_record.ipynb`).

## Why the numbers won't tie out to a "real" track record

I only log a trade once I have enough of the actual reasoning behind it to
write something useful — the setup, the thesis, how I managed it. A line on
a monthly P&L chart with no story behind it doesn't get an entry, because
there's nothing to learn from a bare number. That means some months here
show fewer trades, or a smaller total, than what actually happened that
month — and that's fine. This journal isn't meant to reconcile to a
month-end statement; it's meant to be a complete, honest account of the
trades I can actually explain, so I never end up padding a gap with a guess.

Across all 20 months: **+40.46R** logged over **54 trades**.

## Repo layout

```
data/YYYY-MM.py       Source content for each month (kept locally, not published —
                       see .gitignore). This is what notebooks/ and trades/ are
                       generated from.
trades/YYYY-MM.md      Plain-markdown version of each month's entries, readable
                       without Jupyter.
src/journal.py         Shared helpers: stats, chart styling, optional price charts.
src/build_notebooks.py Generates trades/*.md and notebooks/ from data/*.py.
notebooks/YYYY-MM.ipynb           One notebook per month.
notebooks/years/YYYY.ipynb        Year-in-review rollup.
notebooks/global_track_record.ipynb  Full-history rollup.
```

Every notebook is **self-contained**: the trade entries for that month (or
year) are embedded directly in the notebook itself, so nothing outside the
notebook is needed to read it or re-run it. `data/` is only used to *build*
the notebooks and markdown files — it isn't part of what's published here.

## Charts

Each month notebook plots R per trade and a cumulative-R curve for that
month. Year and full-history notebooks plot the same thing aggregated by
month. There's also an optional per-trade price chart (via Yahoo Finance)
showing the instrument's price around the trade date — this needs a normal
internet connection to fetch data; it fails silently and just skips itself
if none is available.

## Using this repo

```bash
pip install -r requirements.txt
jupyter lab notebooks/global_track_record.ipynb   # full history
# or open a single month, e.g. notebooks/2024-07.ipynb
```

All notebooks are pre-executed, so charts render statically on GitHub
without needing to run anything. To regenerate after editing `data/`:

```bash
python3 src/build_notebooks.py --execute        # rebuild + run everything
python3 src/build_notebooks.py --only 2024-08   # just one month
```

## Monthly log

| Month | R | Trades logged |
|---|---|---|
| Feb 2023 | +6.58R | 3 |
| Mar 2023 | +0.26R | 3 |
| Apr 2023 | +1.75R | 3 |
| May 2023 | -0.10R | 2 |
| Jun 2023 | +3.55R | 3 |
| Jul 2023 | +5.13R | 3 |
| Aug 2023 | +1.13R | 3 |
| Sep 2023 | +0.35R | 3 |
| Oct 2023 | +0.80R | 2 |
| Nov 2023 | +3.65R | 3 |
| Dec 2023 | +1.43R | 3 |
| Jan 2024 | -1.05R | 3 |
| Feb 2024 | +3.27R | 3 |
| Mar 2024 | +1.77R | 3 |
| Apr 2024 | +5.60R | 3 |
| May 2024 | +2.52R | 2 |
| Jun 2024 | -0.29R | 3 |
| Jul 2024 | +5.30R | 3 |
| Aug 2024 | -0.44R | 2 |
| Sep 2024 | -0.75R | 1 |
| **Total** | **+40.46R** | **54** |
