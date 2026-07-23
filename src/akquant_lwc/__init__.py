"""akquant-lwc: TradingView Lightweight Charts reporting plugin for AKQuant.

A drop-in, plotly-free replacement of AKQuant's built-in HTML backtest
report, powered by TradingView Lightweight Charts (vendored, works offline).

Usage with AKQuant::

    import akquant_lwc  # patches BacktestResult on import

    result = run_backtest(...)
    result.report_lwc(market_data={"600000": df}, show=True)
    result.serve_review(market_data={"600000": df}, port=8765)

The module-level functions accept any duck-typed result object (anything
exposing ``trades_df`` / ``equity_curve`` / ``metrics`` / ``trade_metrics``),
so the plugin also works without the patch or with akquant not installed::

    from akquant_lwc import plot_report, serve_review

    plot_report(result, market_data={"600000": df}, filename="report.html")
    serve_review(result, market_data={"600000": df})
"""

from ._patch import patch_result_methods
from .report import build_app_data, plot_report, render_html
from .server import serve_review

__version__ = "0.1.0"

__all__ = [
    "build_app_data",
    "patch_result_methods",
    "plot_report",
    "render_html",
    "serve_review",
]

# Auto-patch BacktestResult on import (idempotent, skipped without akquant).
patch_result_methods()
