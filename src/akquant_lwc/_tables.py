"""HTML table rendering helpers (port of akquant.plot.report table formatters).

Produces self-contained HTML tables used by the analysis/attribution/risk
sections of the report. All cell text is HTML-escaped; numeric formatting
follows the original report: floats ``{:,.6f}`` by default, percentage
columns ``{:.2%}``, and amounts optionally compacted to K/M/B suffixes.
"""

from __future__ import annotations

import html as _html
from typing import Any, Dict, Iterable, Optional

import pandas as pd


def format_currency(value: Any, compact: bool = True) -> str:
    """Format an amount, optionally with compact K/M/B suffixes.

    :param value: Numeric value.
    :param compact: When true, ``>=1e9`` renders as ``x.xxB``, ``>=1e6`` as
        ``x.xxM``, ``>=1e3`` as ``x.xxK``; otherwise ``{:,.2f}``.
    :return: Formatted string ("N/A" for non-numeric input).
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if v != v:  # NaN
        return "N/A"
    if not compact:
        return f"{v:,.2f}"
    sign = "-" if v < 0 else ""
    a = abs(v)
    if a >= 1e9:
        return f"{sign}{a / 1e9:.2f}B"
    if a >= 1e6:
        return f"{sign}{a / 1e6:.2f}M"
    if a >= 1e3:
        return f"{sign}{a / 1e3:.2f}K"
    return f"{v:,.2f}"


def rename_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """Rename the subset of columns present in ``mapping`` (order preserved).

    :param df: Source frame.
    :param mapping: ``{source_name: display_name}``; only existing source
        columns are kept, in the mapping's iteration order, followed by any
        unmapped columns.
    :return: Renamed frame (copy).
    """
    existing = [c for c in mapping if c in df.columns]
    rest = [c for c in df.columns if c not in mapping]
    out = df[existing + rest].copy()
    out.columns = [mapping.get(c, c) for c in existing + rest]
    return out


def _format_cell(
    value: Any,
    pct_columns: Iterable[str],
    currency_columns: Iterable[str],
    column: str,
    compact: bool,
) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "-"
    if column in pct_columns:
        try:
            return f"{float(value) * 100:.2f}%"
        except (TypeError, ValueError):
            return _html.escape(str(value))
    if column in currency_columns:
        return format_currency(value, compact=compact)
    if isinstance(value, float):
        return f"{value:,.6f}"
    return _html.escape(str(value))


def format_table(
    df: pd.DataFrame,
    max_rows: int = 20,
    pct_columns: Optional[Iterable[str]] = None,
    currency_columns: Optional[Iterable[str]] = None,
    compact: bool = True,
) -> str:
    """Render a DataFrame as an HTML table.

    :param df: Frame to render (columns are used as headers verbatim).
    :param max_rows: Maximum body rows; an overflow note row is appended.
    :param pct_columns: Columns whose values are decimal fractions rendered
        as percentages.
    :param currency_columns: Columns rendered with K/M/B compact amounts.
    :param compact: Amount compaction switch.
    :return: HTML table string; a hint div when the frame is empty.
    """
    if df is None or df.empty:
        return '<div class="hint">暂无数据</div>'
    pct = set(pct_columns or ())
    cur = set(currency_columns or ())
    head = "".join(f"<th>{_html.escape(str(c))}</th>" for c in df.columns)
    rows = []
    view = df.head(max_rows)
    for _, row in view.iterrows():
        cells = "".join(
            f"<td>{_format_cell(row[c], pct, cur, str(c), compact)}</td>"
            for c in df.columns
        )
        rows.append(f"<tr>{cells}</tr>")
    if len(df) > max_rows:
        span = len(df.columns)
        note = f"仅展示前 {max_rows} 行，共 {len(df)} 行"
        rows.append(f'<tr><td colspan="{span}" class="hint">{note}</td></tr>')
    return (
        '<table class="data-table"><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )
