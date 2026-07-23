"""Monkey-patch akquant's ``BacktestResult`` with lwc convenience methods.

Importing :mod:`akquant_lwc` calls :func:`patch_result_methods` once, so
``result.report_lwc(...)`` and ``result.serve_review(...)`` become available
on any ``akquant.backtest.result.BacktestResult`` instance. The patch is
idempotent and silently skipped when akquant is not installed, in which case
the module-level functions (:func:`akquant_lwc.plot_report`,
:func:`akquant_lwc.serve_review`) remain fully usable with any duck-typed
result object.

Note: following upstream's break-cleanly convention (viz namespace RFC), the
plugin deliberately does NOT shadow upstream method names — no ``report``
alias is injected; use ``report_lwc`` or the module-level functions.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd


def patch_result_methods() -> bool:
    """Attach ``report_lwc``/``serve_review`` to akquant's BacktestResult.

    :return: ``True`` when akquant was importable and the patch is active,
        ``False`` otherwise (module-level API stays usable regardless).
    """
    try:
        from akquant.backtest.result import BacktestResult
    except Exception:
        return False
    if getattr(BacktestResult, "_lwc_patched", False):
        return True

    def report_lwc(
        self: Any,
        title: str = "AKQuant 策略回测报告 (Lightweight Charts)",
        filename: str = "akquant_lwc_report.html",
        show: bool = False,
        market_data: Optional[Union[pd.DataFrame, Dict[str, pd.DataFrame]]] = None,
        symbols: Optional[List[str]] = None,
        plot_symbol: Optional[str] = None,
        compact_currency: bool = True,
        include_trade_kline: bool = True,
        include_indicators: bool = False,
        indicator_name: Optional[str] = None,
        indicator_symbol: Optional[str] = None,
        indicator_include_warmup: bool = True,
        benchmark: Optional[Union[str, "pd.Series"]] = None,
        curve_freq: str = "D",
    ) -> str:
        """生成基于 TradingView Lightweight Charts 的 HTML 回测报告.

        该方法由 akquant-lwc 插件注入，功能对齐原版 plotly 报告，且报告为
        单文件 HTML（内嵌图表库，无 CDN 依赖）。被复盘的股票可在网页中
        热切换：在输入框中键入代码即可。

        :param title: 报告标题
        :param filename: 保存的文件名
        :param show: 是否在浏览器中自动打开 (默认 False)
        :param market_data: 可选行情数据；传入 ``{symbol: frame}`` 字典时
            所有标的都会被内嵌进页面，可在页面上互相热切换
        :param symbols: 可选标的子集，仅内嵌这些标的
        :param plot_symbol: 可选标的代码，指定初始复盘标的
        :param compact_currency: 是否将金额用 K/M/B 紧凑显示 (默认 True)
        :param include_trade_kline: 是否包含 K 线复盘区块 (默认 True)
        :param include_indicators: 是否包含自定义指标预览区块 (默认 False)
        :param indicator_name: 可选指标键过滤
        :param indicator_symbol: 可选指标标的过滤
        :param indicator_include_warmup: 指标预览是否保留预热点 (默认 True)
        :param benchmark: 基准日收益序列 (pd.Series) 或标识字符串
        :param curve_freq: 净值曲线频率，``"D"`` 日频末值 / ``"raw"`` 原始频率
        :return: 生成的 HTML 文件绝对路径
        """
        from .report import plot_report

        return plot_report(
            result=self,
            market_data=market_data,
            title=title,
            filename=filename,
            symbols=symbols,
            plot_symbol=plot_symbol,
            show=show,
            compact_currency=compact_currency,
            include_trade_kline=include_trade_kline,
            include_indicators=include_indicators,
            indicator_name=indicator_name,
            indicator_symbol=indicator_symbol,
            indicator_include_warmup=indicator_include_warmup,
            benchmark=benchmark,
            curve_freq=curve_freq,
        )

    def serve_review(
        self: Any,
        market_data: Optional[Union[pd.DataFrame, Dict[str, pd.DataFrame]]] = None,
        data_provider: Optional[Callable[[str], pd.DataFrame]] = None,
        host: str = "127.0.0.1",
        port: int = 8765,
        title: str = "AKQuant 交易复盘 (Lightweight Charts)",
        open_browser: bool = True,
    ) -> None:
        """启动交互式交易复盘 Web 服务 (阻塞, akquant-lwc 插件注入).

        页面按需加载各标的 K 线与买卖点：在网页输入框中键入任意可解析的
        股票代码即可热切换复盘标的，无需重新生成文件。

        :param market_data: 可选预加载行情数据 ``{symbol: frame}``
        :param data_provider: 可选回调 ``(code) -> DataFrame``，用于解析
            ``market_data`` 中不存在的标的代码
        :param host: 监听地址
        :param port: 监听端口，0 表示自动选择空闲端口
        :param title: 页面标题
        :param open_browser: 启动后是否自动打开浏览器
        """
        from .server import serve_review

        return serve_review(
            result=self,
            market_data=market_data,
            data_provider=data_provider,
            host=host,
            port=port,
            title=title,
            open_browser=open_browser,
        )

    BacktestResult.report_lwc = report_lwc  # type: ignore[attr-defined]
    BacktestResult.serve_review = serve_review  # type: ignore[attr-defined]
    BacktestResult._lwc_patched = True  # type: ignore[attr-defined]
    return True
