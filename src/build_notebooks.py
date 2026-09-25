"""
build_notebooks.py — generates the journal from the private local content in
data/*.py:

  - track_record/YYYY-MM.md              one plain-markdown entry per month
  - track_record/years/YYYY.ipynb        year-in-review rollup notebook
  - track_record/global_track_record.ipynb  full-history rollup notebook

Months are plain markdown on purpose: with only 2-4 trades a month, a
notebook and its charts don't add anything over well-formatted text. The
year and global rollups are notebooks because aggregating 9-20 months is
where a chart actually earns its place.

Rollup notebooks are self-contained: each one embeds its own month data
directly as a Python literal, so it never reads data/ (or any other file
outside itself) at run time. data/*.py is only ever read here, at build
time, and stays local (see .gitignore) — it never gets published.

Usage:
    python3 src/build_notebooks.py            # (re)generate everything
    python3 src/build_notebooks.py --execute   # + run the rollup notebooks
                                                #   (nbconvert) so charts render
                                                #   statically on GitHub
    python3 src/build_notebooks.py --only 2024-06   # only this month's markdown
"""
from __future__ import annotations

import argparse
import importlib.util
import pprint
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

MONTHS = [
    "2023-02", "2023-03", "2023-04", "2023-05", "2023-06", "2023-07", "2023-08", "2023-09",
    "2023-10", "2023-11", "2023-12", "2024-01", "2024-02", "2024-03", "2024-04", "2024-05",
    "2024-06", "2024-07", "2024-08", "2024-09",
]

YEARS = {
    "2023": [m for m in MONTHS if m.startswith("2023")],
    "2024": [m for m in MONTHS if m.startswith("2024")],
}

BOOTSTRAP = """\
# --- Bootstrap: locate the repo root and import the shared helper module ---
import sys
from pathlib import Path

def _find_root(start=None):
    p = Path(start or Path.cwd()).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "src" / "journal.py").exists() and (candidate / "track_record").is_dir():
            return candidate
    raise FileNotFoundError("Could not locate the repo root from " + str(p))

ROOT = _find_root()
sys.path.insert(0, str(ROOT / "src"))
import journal
import matplotlib.pyplot as plt
"""


def load_month_content(root: Path, ym: str) -> dict:
    path = root / "data" / f"{ym}.py"
    spec = importlib.util.spec_from_file_location(f"content_{ym.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.MONTH


def fmt_date(date_str: str | None) -> str:
    if not date_str:
        return ""
    if len(date_str) == 10:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d, %Y")
        except ValueError:
            return date_str
    return date_str


def meta_line(e: dict) -> str:
    pair = e.get("pair") or "—"
    direction = f"{e['direction']}" if e.get("direction") else None
    date = fmt_date(e.get("date"))
    bits = [f"**{pair}**"]
    if direction:
        bits.append(direction)
    status = e.get("status")
    if status == "closed":
        r = e.get("r")
        bits.append(f"closed · {r:+.2f}R" if r is not None else "closed")
    elif status == "open":
        fr = e.get("floating_r")
        bits.append(f"still open · {fr:+.2f}R floating" if fr is not None else "still open")
    elif status == "skipped":
        bits.append("passed on")
    if date:
        bits.append(date)
    return " · ".join(bits)


def entry_markdown(e: dict) -> str:
    return f"### {e['title']}\n\n*{meta_line(e)}*\n\n{e['body']}"


def _summary_from_entries(entries: list[dict]) -> str:
    closed = [e for e in entries if e.get("status") == "closed" and e.get("r") is not None]
    total = round(sum(e["r"] for e in closed), 2)
    wins = sum(1 for e in closed if e["r"] > 0)
    losses = sum(1 for e in closed if e["r"] < 0)
    return f"{total:+.2f}R logged · {wins}W/{losses}L"


# --------------------------------------------------------------------------- #
# Month markdown
# --------------------------------------------------------------------------- #

def build_month_markdown(root: Path, ym: str) -> Path:
    content = load_month_content(root, ym)
    entries = content["entries"]
    label = content["label"]
    lines = [f"# {label}", ""]
    for e in entries:
        lines.append(entry_markdown(e))
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*{_summary_from_entries(entries)}*")
    out_path = root / "track_record" / f"{ym}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [ok] {out_path.relative_to(root)}")
    return out_path


# --------------------------------------------------------------------------- #
# Year / global rollups
# --------------------------------------------------------------------------- #

def build_rollup_notebook(root: Path, months: list[str], title: str, out_path: Path,
                           month_link_prefix: str, extra_links_md: str = "") -> Path:
    month_rows = []
    for ym in months:
        content = load_month_content(root, ym)
        entries = content["entries"]
        closed = [e for e in entries if e.get("status") == "closed" and e.get("r") is not None]
        month_rows.append({
            "month": content["label"],
            "ym": ym,
            "total_r": round(sum(e["r"] for e in closed), 2),
            "trades": len(closed),
        })

    links_md = "\n".join(f"- [{r['month']}]({month_link_prefix}/{r['ym']}.md)" for r in month_rows)

    cells = [new_markdown_cell(f"# {title}")]
    cells.append(new_code_cell(BOOTSTRAP))
    cells.append(new_code_cell(
        f"month_rows = {pprint.pformat(month_rows, width=100, sort_dicts=False)}\n\n"
        "import pandas as pd\n"
        "df = pd.DataFrame(month_rows).set_index(\"month\")[[\"total_r\", \"trades\"]]\n"
        "df.columns = [\"R\", \"Trades\"]\n"
        "df\n"
    ))
    cells.append(new_code_cell(
        "print(f\"Total: {df['R'].sum():+.2f}R over {int(df['Trades'].sum())} logged trades \"\n"
        "      f\"across {len(df)} months.\")\n"
    ))
    cells.append(new_code_cell(
        f'journal.plot_monthly_bars(list(df.index), list(df["R"]), "R by month — {title}")\n'
    ))
    cells.append(new_code_cell(
        f'journal.plot_monthly_equity(list(df.index), list(df["R"]), "Cumulative R — {title}")\n'
    ))
    cells.append(new_markdown_cell("### Months\n\n" + links_md + ("\n\n" + extra_links_md if extra_links_md else "")))

    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, out_path)
    print(f"  [ok] {out_path.relative_to(root)}")
    return out_path


def build_year_notebook(root: Path, year: str, months: list[str]) -> Path:
    return build_rollup_notebook(
        root, months, f"{year} in review",
        root / "track_record" / "years" / f"{year}.ipynb",
        month_link_prefix="..",   # track_record/years/2024.ipynb -> ../2024-01.md
    )


def build_global_notebook(root: Path) -> Path:
    extra = "### Years\n\n" + "\n".join(f"- [{y}](years/{y}.ipynb)" for y in YEARS)
    return build_rollup_notebook(
        root, MONTHS, "Full journal — February 2023 to September 2024",
        root / "track_record" / "global_track_record.ipynb",
        month_link_prefix=".",   # track_record/global_track_record.ipynb -> ./2024-01.md
        extra_links_md=extra,
    )


# --------------------------------------------------------------------------- #

def execute_notebook(path: Path) -> bool:
    print(f"  [exec] {path.name} ...", end=" ", flush=True)
    r = subprocess.run(
        [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
         "--inplace", "--ExecutePreprocessor.timeout=180", str(path)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("FAILED")
        print(r.stdout[-3000:])
        print(r.stderr[-3000:])
    else:
        print("ok")
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    print("Repo root:", root)

    built: list[Path] = []
    months = args.only if args.only else MONTHS

    print("\n== Month markdown ==")
    for ym in months:
        if ym not in MONTHS:
            continue
        build_month_markdown(root, ym)

    if not args.only:
        print("\n== Year rollups ==")
        for y, ms in YEARS.items():
            built.append(build_year_notebook(root, y, ms))

        print("\n== Global rollup ==")
        built.append(build_global_notebook(root))

    if args.execute:
        print("\n== Executing notebooks ==")
        for p in built:
            execute_notebook(p)

    print(f"\nDone: {len(built)} notebook(s), {len(months)} month file(s).")


if __name__ == "__main__":
    main()
