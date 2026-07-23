# ROADMAP — akquant-lwc

> 维护约定：本文件只记录"方向与验收标准"，实现细节与结论沉淀到对应
> PR / 文档。版本节奏与发版纪律见 `CONTRIBUTING.md`。

## 当前状态

- `0.1.0`（未发布）：全量 plotly-free 报告（指标卡/净值回撤/热力图/滚动/
  基准/交易分析/归因容量/策略归属/风控强平/指标预览）、K线买卖点复盘
  热切换、`serve_review` 服务模式、散点点击联动、明暗主题、
  `external_data` 单文件外置数据（一次文件授权）。

## 实验方向（spike 驱动，独立分支验证后再决定是否入库）

### E1. parquet-wasm 直读本地 parquet（分支：`exp/parquet-wasm`）

**动机**：`external_data` 目前是 JSON 伴随文件，需生成时转换一次且体积
偏大（同数据约为 parquet 的 2~4 倍）。若页面能直接读 parquet，则可
**零转换**复用现有数据管道产物（parquet 文件）。

**方案**：引入 Apache Arrow 官方 `parquet-wasm`（Rust→WASM，~1-2MB）
+ `apache-arrow` JS 读表；报告侧 `plot_report(..., parquet_file=...)` 只
引用不转换；页内一次文件授权后按 symbol 在 JS 侧过滤出 K线/买卖点。

**验收标准**：
1. `file://` 页面经一次文件授权后可读取本地 parquet 并渲染任意标的；
2. 与 JSON 路径同一批真实数据（≥3 标的）渲染结果逐点一致；
3. 首屏加载与切换耗时不超过 JSON 路径的 1.5 倍；
4. wasm 资产可 vendored 进包（离线可用），给出体积评估。

**风险**：无 SQL，整表进内存——大宇宙场景内存仍是全量（只省转换与
体积，不省内存）；与 `external_data` JSON 的取舍需实测后定。

### E2. DuckDB-WASM 按需 SQL 取数（分支：`exp/duckdb-wasm`）

**动机**：超大宇宙（如全 A 股分钟线复盘）下，JSON/parquet-wasm 都需
全量进内存。DuckDB-WASM 利用 parquet 列存 + row group 结构，可按
`WHERE instrument=...` **真·按需读取**，内存与当前复盘标的数无关。

**方案**：引入 duckdb-wasm（~10-15MB），页内授权 parquet 文件后
`SELECT ... WHERE instrument=?` 现场取数；评测懒加载 SQL（httpfs 本地
File System Access API 句柄）与全量挂载两种接入方式。

**验收标准**：
1. 浏览器内 duckdb-wasm 可对本地 parquet 执行
   `SELECT * WHERE instrument='600519.SH'` 并返回正确行数；
2. 大文件（≥1GB 或百万行级）下，单标的首查与切换延迟可交互（目标
   <2s），内存占用显著低于全量加载；
3. wasm 体积对报告首屏的影响可接受（可懒加载/分包）；
4. 与 E1 同一数据集对拍一致。

**风险**：wasm 体积大、初始化慢；file:// 下 parquet 挂载方式（File
System Access API 兼容性）需实测；若延迟不达标则退回 E1/JSON。

## 远期候选（未排期）

- 复盘区指标叠加（MA/EMA 等常用均线开关）
- 分钟级数据报告路径的完整验证（intraday token 已支持，缺大样本实测）
- 报告区块的可配置显隐（轻量配置项）
