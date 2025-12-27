# AI 代理人工作流指南 (Agent Workflow Guide)

本文件說明了 `.agent` 目錄的用途，以及如何利用工作流 (Workflows) 來提升開發效率。

## 1. `uv-package-manager.md` 的功能

這個檔案是專門為 **Python 依賴管理** 設計的工作流手冊。它的主要功能包括：

- **標準化指令**：指示 AI (Antigravity) 如何使用 `uv` 執行同步 (`uv sync`)、新增套件 (`uv add`)、升級套件等動作。
- **環境一致性**：確保 AI 在幫你安裝新的 Library 時，會遵循專案的 `pyproject.toml` 與 `uv.lock` 規範，避免版本衝突。
- **快速執行**：指導 AI 使用 `uv run` 啟動後端伺服器 (FastAPI) 或執行測試。

## 2. `.agent` 目錄的用途

`.agent` 目錄是 AI 代理人的「大腦筆記本」，主要用途如下：

- **存儲工作流 (Workflows)**：存放於 `.agent/workflows/` 下的 Markdown 檔案是 AI 的操作手冊。當你下達指令或我感知道需要進行特定任務時，我會主動閱讀這些檔案。
- **定義專案規範**：幫助 AI 快速理解該專案的技術棧 (Tech Stack)、命名規則與開發慣例。
- **提升自動化程度**：透過特定的標記（如 `// turbo`），AI 可以更智能地判斷哪些指令是可以安全自動執行的。

## 3. 建議為此專案新增的工作流

根據 `ElevenDops` 的專案結構（FastAPI + Streamlit + Docker + Kiro Spec），以下是建議設定的自動化工作流：

| 工作流建議         | 檔案名稱建議             | 說明                                                         |
| :----------------- | :----------------------- | :----------------------------------------------------------- |
| **環境初始化**     | `dev-setup--init.md`     | 同時完成 `uv sync`、`.env` 配置與 `pnpm install`。           |
| **測試與品質檢驗** | `test--quality-check.md` | 一鍵執行 `pytest` 並運行 `oxlint` 與 `eslint` 進行代碼檢查。 |
| **功能開發流程**   | `feature--kiro-spec.md`  | 定義如何從 `.kiro/specs` 讀取需求並實作新功能的標準步驟。    |
| **啟動專案**       | `run--project-start.md`  | 自動啟動 FastAPI 後端與 Streamlit 前端。                     |
| **命名規範檢查**   | `check--file-naming.md`  | 自動掃描新產生的檔案是否符合「雙橫線分隔」的命名規則。       |

---

> [!TIP]
> 如果你想讓我為你實作其中任何一個工作流，只需告訴我：「請幫我建立 `check--file-naming.md` 工作流」，我就會為你準備好！
