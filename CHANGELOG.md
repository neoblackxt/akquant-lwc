# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

首个候选版本（0.1.0，待发）。AKQuant 可视化报告的 plotly 替代插件，基于
TradingView Lightweight Charts。

### Added

- **完整报告**（功能对齐原版 plotly `result.report()`）：
  - 报告概要（回测区间/时长/初始资金/最终权益）与 15 项核心指标卡
  - 净值曲线 + 回撤曲线（时间轴联动）+ 月度收益热力图
  - 收益分析：年度收益柱图、日收益分布 + 正态拟合、滚动夏普/波动率（126）
  - 基准对比：7 指标卡 + 策略/基准/超额三线累计收益图
  - 交易分析：盈亏分布直方图、盈亏 vs 持仓时长散点
  - 组合归因与容量分析、策略归属聚合（订单/成交/拒单/强平审计明细表）
  - 风控拒单与强平分析：策略级占比、原因占比、按日拒单/原因/策略趋势、
    强平计数与计息、拒单原因 Top 8
  - 自定义指标多面板预览（`include_indicators=True`）
- **交易复盘（K线买卖点）**：
  - 网页输入代码 + 自动补全热切换复盘标的；B/S 箭头标记开平仓
  - 悬停买卖点显示开平仓时间/价格/收益率/净利润
  - 交易明细表点击行自动缩放到该笔交易区间
  - 盈亏 vs 持仓时长散点悬停显示完整交易卡片，点击散点联动复盘图切换标的
  - `serve_review` 本地服务模式：页面按需加载任意代码，支持
    `data_provider` 回调解析
- 页内明暗主题切换：报告页右上角按钮，切换只重着色不重建数据
  （payload 主题无关，图表/表格/canvas 图全部跟随）
- `plot_report(external_data=True)` 外置数据模式：标的行情写入单个伴随
  文件 `<报告名>.data.json`，HTML 保持小巧；页面一次"打开数据文件"授权
  （浏览器安全要求）后即可热切换全部标的，适合宽截面宇宙
- **接入方式**：`import akquant_lwc` 即自动向 `BacktestResult` 注入
  `report_lwc` / `serve_review` 方法；模块级 `plot_report` / `serve_review`
  函数对任意 duck-typed 结果对象可用
- **工程**：GitHub Release / push 到 main 触发的 PyPI Trusted Publisher
  发布流水线（OIDC 免 token，含版本守卫与人工审批门）；dev CI
  （lint + 单测 + 构建检查）；ruff 代码规范；pytest 单元测试
