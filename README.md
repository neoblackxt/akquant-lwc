# akquant-lwc

基于 **TradingView Lightweight Charts** 的 [AKQuant](https://github.com/akfamily/akquant) 回测报告与交易复盘插件（plotly 替代方案）。

图表库已 vendored 进包内，生成的报告为**单文件 HTML，离线可开**；复盘标的支持**网页内热切换**。

![报告总览](https://raw.githubusercontent.com/neoblackxt/akquant-lwc/main/docs/assets/report-overview.png)

## 与上游 `result.viz` 的关系

akquant ≥ 0.3.19 把可视化收敛为 `result.viz.*`，并自带 `viz.review()`（LWC
K线复盘）与 `viz.report()`（plotly 全量报告）。本插件与其**互补不冲突**，
定位收敛在上游明确不做的三件事：

| 能力 | 上游 `result.viz` | 本插件 |
|---|---|---|
| K线交互复盘（买卖点/热切换/明暗主题） | ✅ `viz.review()` | ✅（另有散点联动、输入框任意代码） |
| 全量分析报告（指标/热力图/滚动/基准/归因/风控） | ✅ `viz.report()`，**基于 plotly** | ✅ **零 plotly**（LWC + canvas + HTML） |
| 复盘 HTTP 服务（`data_provider` 按需解析任意代码） | ❌（官方 RFC 明确后置） | ✅ `serve_review()` |
| 散点点击 → 联动复盘图切换标的 | ❌ | ✅ |
| 运行依赖 | plotly（~3.5MB CDN） | 仅 pandas，报告离线单文件 |

怎么选：只要交互式 K 线复盘 → 上游 `result.viz.review()` 即可；要**无
plotly 环境的全量报告**、复盘服务化、或散点联动复盘 → 用本插件。

## 为什么不用 plotly

原版 plotly 报告在交易复盘（K线买卖点）场景下的痛点：

- 买卖点标记与 K 线图案区分度不够，难以快速定位开平仓；
- 鼠标左键拖拽平移、滚轮缩放交互不友好；
- 缩放平移时 y 轴不自动贴合可视区数据，图像经常在垂直方向上偏出合理区域；
- plotly.js ~3.5MB 且走 CDN，离线/弱网环境报告无法打开。

Lightweight Charts 是 TradingView 开源的金融图表库：拖拽平移、以鼠标为中心的滚轮缩放、可视区 y 轴自动缩放均为原生行为，体积仅 ~160KB。

## 安装

```bash
pip install git+https://github.com/neoblackxt/akquant-lwc.git
```

> PyPI 上架筹备中（当前处于 0.1.0 未发布状态），上架后可
> `pip install akquant-lwc`。

## 快速开始

```python
import akquant_lwc  # 导入即自动给 BacktestResult 注入 report_lwc / serve_review
from akquant import run_backtest

result = run_backtest(...)

# 1) 静态单文件报告（含交易复盘，页面内可热切换标的）
result.report_lwc(
    market_data={"600000": df1, "600004": df2},  # {symbol: DataFrame}
    filename="akquant_lwc_report.html",
    show=True,
)

# 2) 交互式复盘服务：页面输入任意代码，服务端按需加载
result.serve_review(
    market_data={"600000": df1},
    data_provider=lambda code: load_df(code),  # 可选，解析未预载的代码
    port=8765,
)
```

也可以不依赖注入，直接调用模块级函数（对任何带 `trades_df` /
`equity_curve` / `metrics` / `trade_metrics` 属性的结果对象都可用）：

```python
from akquant_lwc import plot_report, serve_review

plot_report(result, market_data={"600000": df1}, filename="report.html")
serve_review(result, market_data={"600000": df1})
```

### 从官方 `result.report()` 迁移

akquant **≥ 0.3.19** 将可视化方法收敛到 `result.viz.*` 并删除了
`result.report()`。本插件遵循上游的纯净断裂原则，**不注入同名影子方法**；
迁移只需把调用点改为插件自己的方法（签名与旧版完全一致）：

```python
import akquant_lwc  # 注入 report_lwc / serve_review

result.report_lwc(  # 旧 result.report(...) 的参数原样可用
    market_data={"600000": df1},
    filename="report.html",
    benchmark=benchmark_returns,
)
```

或使用模块级函数（不改 result 类，对任何 duck-typed 结果对象可用）：
`akquant_lwc.plot_report(result, ...)`。

## 功能

**报告区块（全面对齐原版 plotly 报告）**

- 报告概要（回测区间、初始/期末资金、持续天数）
- 绩效指标卡（收益/回撤/夏普/索提诺/卡玛/波动率/胜率/盈亏比/SQN 等）
- 净值曲线 + 回撤曲线（时间轴联动）
- 滚动指标（滚动夏普/波动率）、日收益分布、年度收益、月度收益热力图
- 基准对比（累计收益/超额收益曲线，年化超额、跟踪误差、信息比率、Beta、Alpha）
- 交易分析：盈亏分布、盈亏 vs 持仓时长散点（悬停显示完整交易卡片，
  **点击散点直接联动下方 K 线复盘图切换标的**）
- 风控拒单分析（策略级占比、原因占比、按日趋势、强平审计）
- 明细表：交易/委托/成交/持仓/风险敞口/归因/容量分析
- 自定义指标预览区块（`include_indicators=True`）

**交易复盘（K线买卖点）**

- 代码输入框 + 自动补全，回车即热切换复盘标的，无需重新生成报告
- B/S 箭头标记开平仓（A股红涨绿跌配色），悬停显示开平仓时间/价格/收益率/净利润
- 交易明细表点击行自动缩放到该笔交易区间
- 服务模式支持 `data_provider` 回调，页面可解析任意新代码

![买卖点复盘](https://raw.githubusercontent.com/neoblackxt/akquant-lwc/main/docs/assets/trade-review-markers.png)

![悬停交易详情](https://raw.githubusercontent.com/neoblackxt/akquant-lwc/main/docs/assets/trade-tooltip.png)

## API

**`plot_report`**

```python
plot_report(result, market_data=None, title="...", filename="...",
            symbols=None, plot_symbol=None, show=False, compact_currency=True,
            include_indicators=False, benchmark=None, curve_freq="D",
            external_data=False) -> str
```

生成静态单文件报告，返回文件绝对路径。

- `market_data`: `{symbol: DataFrame}` 字典、单只 DataFrame，或带 symbol 列的长表（OHLCV 列容忍中英文命名）
- `symbols`: 仅内嵌指定标的子集
- `benchmark`: 基准收益率序列（`pd.Series`）
- `external_data`: `True` 时标的行情不内嵌 HTML，而是写出单个伴随文件
  `<报告名>.data.json`（与 HTML 同目录）；打开报告后按页内提示点一次
  "打开数据文件"完成授权（浏览器安全限制要求一次用户手势），之后全部
  标的均可热切换。适合数百只标的的宽截面场景，HTML 保持小巧

**`serve_review`**

```python
serve_review(result, market_data=None, data_provider=None,
             host="127.0.0.1", port=8765, title="...", open_browser=True)
```

启动交互式复盘服务（阻塞，Ctrl+C 停止）。

- `data_provider`: `(code) -> DataFrame` 回调，解析 `market_data` 中不存在的代码

**`BacktestResult.report_lwc(...) / .serve_review(...)`**

导入 `akquant_lwc` 后自动注入，参数同上。未安装 akquant 时注入自动跳过，模块级函数不受影响。

## 开发

```bash
pip install -e ".[dev]"
pytest tests/
ruff check src/
```

## License

MIT。内嵌的 [Lightweight Charts](https://github.com/tradingview/lightweight-charts)
遵循 Apache License 2.0。
