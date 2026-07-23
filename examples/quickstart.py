"""akquant-lwc 快速开始示例：静态报告 + 交互式复盘服务.

数据通过 AKShare 获取真实行情，策略为阳线买/阴线卖的简单示例。
"""

import akshare as ak
import pandas as pd
from akquant import Bar, Strategy, run_backtest

import akquant_lwc  # noqa: F401  (导入即注入 report_lwc / serve_review)


class BullBearStrategy(Strategy):
    """阳线买、阴线卖的简单趋势策略."""

    def on_bar(self, bar: Bar) -> None:
        """阳线无仓则买，阴线持仓则平."""
        pos = self.get_position(bar.symbol)
        if pos == 0 and bar.close > bar.open:
            self.buy(bar.symbol, 100)
        elif pos > 0 and bar.close < bar.open:
            self.close_position(bar.symbol)


def load_data(symbols: list[str]) -> dict[str, pd.DataFrame]:
    """Fetch daily bars for the given symbols via AKShare."""
    frames: dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        df = ak.stock_zh_a_daily(
            symbol="sh" + symbol, start_date="20230101", end_date="20261231"
        )
        df["symbol"] = symbol
        frames[symbol] = df
    return frames


if __name__ == "__main__":
    SYMBOLS = ["600000", "600004", "600006"]
    market_data = load_data(SYMBOLS)

    print("Running Backtest...")
    result = run_backtest(
        data=market_data,
        strategy=BullBearStrategy,
        symbols=SYMBOLS,
        initial_cash=1_000_000.0,
        show_progress=True,
    )
    print(f"Total Trades: {len(result.trades_df)}")

    # 1) 静态单文件报告：全部标的内嵌，页面内热切换；
    #    附带基准对比与自定义指标预览区块
    benchmark = market_data["600000"].set_index("date")["close"].pct_change().dropna()
    benchmark.name = "600000"
    report_file = result.report_lwc(
        title="AKQuant 策略回测报告 (Lightweight Charts)",
        filename="akquant_lwc_report.html",
        market_data=market_data,
        benchmark=benchmark,
        include_indicators=True,
        show=True,
    )
    print(f"Report written to {report_file}")

    # 2) 交互式复盘服务：页面输入任意代码，经 data_provider 按需加载
    def data_provider(code: str) -> pd.DataFrame:
        """Resolve a bare 6-digit code into an OHLCV frame via AKShare."""
        prefix = "sh" if code.startswith("6") else "sz"
        df = ak.stock_zh_a_daily(
            symbol=prefix + code, start_date="20230101", end_date="20261231"
        )
        df["symbol"] = code
        return df

    result.serve_review(
        market_data=market_data,
        data_provider=data_provider,
        port=8765,
    )
