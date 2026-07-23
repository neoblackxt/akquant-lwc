# 贡献指南 (Contributing Guide)

感谢你对 akquant-lwc 的关注！我们需要你的帮助来让这个插件变得更好。无论你是修复 Bug、改进文档，还是增加新功能，我们都非常欢迎！

为了方便"萌新"上手，我们准备了这份详细的 GitHub 合作开发指南。

## 🚀 开发流程 (Workflow)

我们采用 **Git Flow** 的简化模式进行开发。

- **`main` 分支**: 稳定分支，对应 PyPI 发布的版本。
- **`dev` 分支**: 开发分支，所有的日常开发和 PR 都应合并到此分支。

### 1. Fork & Clone (复刻与克隆)

1.  **Fork 项目**: 点击 GitHub 页面右上角的 `Fork` 按钮，将 `akquant-lwc` 仓库复刻到你自己的账号下。
2.  **Clone 到本地**:
    ```bash
    # 将 <your-username> 替换为你的 GitHub 用户名
    git clone https://github.com/<your-username>/akquant-lwc.git
    cd akquant-lwc
    ```
3.  **设置上游仓库 (Upstream)**:
    为了保持你的代码与官方仓库同步，需要添加上游仓库地址：
    ```bash
    git remote add upstream https://github.com/neoblackxt/akquant-lwc.git
    ```

### 2. 环境搭建 (Setup)

本项目为**纯 Python 包**（无 Rust 编译步骤），可视化资产（Lightweight Charts JS）已 vendored 进包内：

1.  **创建 Python 虚拟环境 (推荐 uv)**:
    ```bash
    uv venv --python 3.10
    # Windows:
    .venv\Scripts\activate
    # macOS / Linux:
    source .venv/bin/activate
    ```
2.  **安装开发依赖**:
    ```bash
    uv pip install -e ".[dev]"
    ```
    说明：`dev` 额外依赖包含 `akquant`，用于端到端集成验证（补丁注入、
    真实回测结果渲染）。只调试纯渲染逻辑时可不装，`akquant_lwc` 本体仅
    依赖 `pandas`。

### 3. 开始开发 (Coding)

1.  **同步最新代码**:
    每次开发前，先确保你的本地 `dev` 分支是最新的：
    ```bash
    git checkout dev
    git pull upstream dev
    ```

2.  **创建功能分支**:
    **不要**直接在 `dev` 或 `main` 上修改。请为每个任务创建一个新分支：
    ```bash
    git checkout -b feature/my-new-feature
    # 或者修复 bug
    git checkout -b fix/bug-fix-name
    ```

3.  **编写代码**:
    *   遵循 PEP 8 编码规范。
    *   确保添加了类型注解 (Type Hints)。
    *   提交前请运行检查：
        ```bash
        uv run ruff check .
        uv run ruff format --check .
        ```
    *   前端部分说明：`src/akquant_lwc/_app_js.py`（页面 JS）与
        `src/akquant_lwc/_template.py`（HTML/CSS）内嵌在 Python 字符串中，
        这两处豁免 E501 行宽限制；修改 JS 后建议用 `node --check` 做一次
        语法校验。

### 4. 提交与推送 (Commit & Push)

1.  **提交代码**:
    ```bash
    git add .
    git commit -m "feat: 添加了xxx功能"
    ```
    *(推荐使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式)*

2.  **推送到你的 Fork 仓库**:
    ```bash
    git push origin feature/my-new-feature
    ```

### 5. 版本与 Changelog 规则 (Versioning & Changelog)

- `pyproject.toml` 中的 `project.version` 是唯一的版本号来源（纯 Python
  包，无 Rust 侧版本需要同步）。
- 正式发布经 **PyPI Trusted Publisher**（`.github/workflows/publish.yml`）
  OIDC 免 token 自动完成，无需手工 twine upload。两种触发方式：
  1. **合并 dev 到 main**：push 到 main 自动构建并检查版本号——
     `pyproject.toml` 中的版本在 PyPI 不存在时自动发布，已存在则跳过
     （日常合并不 bump 版本不会报错）；
  2. **GitHub Release**（形如 `v0.1.0` 的 tag）：同一版本守卫，重复版本自动跳过。
- dev 分支与 PR 由 `ci.yml` 做 lint + 单测 + 构建检查，不触发发布。
- `CHANGELOG.md` 只保留 `Unreleased` 和当前主线版本记录；更早的版本历史
  统一以 Git tag、GitHub Releases 或历史提交记录为准。

维护 `CHANGELOG.md` 时请遵循以下约定：

- 日常开发只更新 `Unreleased` 区块。
- 发版时，将 `Unreleased` 中与本次发布相关的内容整理为对应的正式版本条目。
- 变更说明优先写"用户可感知的行为变化"，避免只写纯内部重构细节。
- 建议使用 `Added`、`Changed`、`Fixed`、`Removed` 分类。

### 6. 测试与验证 (Testing)

1.  **运行单元测试**:
    ```bash
    uv run pytest tests/
    ```

2.  **端到端验证（真实数据，可选）**:
    涉及渲染结果的改动，建议跑一次真实回测验证（需要 akquant 环境 +
    真实行情数据），并在浏览器中打开生成的 HTML 确认各区块渲染与交互
    （图表渲染、tooltip、热切换、点击联动），控制台应无 JS 错误。
    仓库的 e2e 测试默认跳过，设置 `AKQUANT_LWC_E2E=1` 后启用。

3.  **打包完整性检查**:
    修改包结构或资产后，验证 wheel 内容完整（含 `assets/*.js`）：
    ```bash
    uv build
    unzip -l dist/*.whl | grep assets
    ```

---

## ✅ 提交前的检查清单

在提交 PR 之前，请检查：

- [ ] 运行了 `uv run ruff check .` 和 `uv run ruff format --check .` 没有报错。
- [ ] 运行了 `uv run pytest tests/` 且通过。
- [ ] 修改 JS/HTML 模板后已在浏览器实测生成报告（控制台无错误）。
- [ ] 如果是新功能，是否添加了简单的测试或示例？
- [ ] 文档（README / docstring / CHANGELOG 的 Unreleased 区块）是否已更新？

## ❓ 遇到问题？

如果你在配置环境或提交代码时遇到困难，欢迎在 [Issues](https://github.com/neoblackxt/akquant-lwc/issues) 中提问，我们会尽快回复！

再次感谢你的贡献！🎉
