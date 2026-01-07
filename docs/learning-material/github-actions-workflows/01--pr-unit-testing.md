# PR 階段的單元測試 (Unit Testing in PR Stage)

## 關鍵字

- **Pull Request (PR)**：GitHub 中用於建議程式碼變更的機制。
- **Continuous Integration (CI)**：持續整合，自動化測試與建置的實踐。
- **pytest**：Python 的測試框架。
- **workflow trigger**：觸發 GitHub Action 執行的事件（如 `pull_request`）。

## 學習目標

完成本章節後，您將能夠：

1. 理解如何在 PR 建立或更新時自動觸發測試。
2. 配置 GitHub Actions 環境以執行 Python 單元測試。
3. 設定測試失敗時阻擋 PR 合併的安全門檻。

## 步驟說明

### 步驟 1：定義 PR 觸發條件

#### 我們在做什麼？

在 Workflow 配置中設定 `on.pull_request`，並指定目標分支為 `main`。

#### 為什麼需要這樣做？

這是保護主分支的第一道防線。透過在 PR 階段執行測試，可以確保新開發的功能不會破壞現有的系統邏輯。

#### 程式碼範例

```yaml
# .github/workflows/test.yml
name: Unit Tests

on:
  pull_request:
    branches: ["main"] # 僅在針對 main 分支的 PR 觸發
```

### 步驟 2：配置測試環境與執行測試

#### 我們在做什麼？

使用 GitHub 提供的虛擬環境，安裝相依套件並執行 `pytest`。

#### 為什麼需要這樣做？

測試需要正確的 Python 環境。我們使用 `uv`（如專案規範所述）來快速安裝套件。

#### 程式碼範例

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 安裝 uv 並同步相依性
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          uv sync

      - name: 執行 Pytest
        run: uv run pytest tests/
```

#### 流程圖

```mermaid
graph TD
    A[開發者建立 PR] --> B[觸發 GitHub Action]
    B --> C[簽出程式碼]
    C --> D[安裝相依性 (uv sync)]
    D --> E[執行 pytest]
    E -->|通過| F[PR 顯示綠勾, 可合併]
    E -->|失敗| G[PR 顯示紅叉, 阻擋合併]
```

## 常見問題 Q&A

### Q1：如果測試需要敏感資訊（如 API Key）怎麼辦？

**答：** 應將這些資訊儲存在 GitHub 的 **Secrets** 中，並在工作流中透過 `env` 變數傳入。但建議單元測試應盡量使用 Mock 數據，避免依賴外部 API。

### Q2：如何確保所有測試都必須通過才能合併？

**答：** 您需要在 GitHub 儲存庫的 **Settings > Branches** 中設定 **Branch protection rule**，並啟用 "Require status checks to pass before merging"。

## 重點整理

| 配置項            | 說明               | 目的                   |
| ----------------- | ------------------ | ---------------------- |
| `on.pull_request` | 偵測 PR 事件       | 自動化啟動測試程序     |
| `ubuntu-latest`   | 執行測試的作業系統 | 提供乾淨一致的測試環境 |
| `uv run pytest`   | 測試執行命令       | 驗證程式碼邏輯正確性   |

## 延伸閱讀

- [GitHub Actions 官方文件](https://docs.github.com/en/actions)
- [Pytest 官方手冊](https://docs.pytest.org/)

---

## 參考程式碼來源

本文件中的程式碼範例參考自以下專案檔案：

| 檔案路徑         | 說明                 |
| ---------------- | -------------------- |
| `pyproject.toml` | 定義了 Python 相依性 |
| `tests/`         | 專案的測試目錄       |
