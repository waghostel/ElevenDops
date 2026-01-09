# Cloud Run MCP 簡介

## 關鍵字

- **MCP (Model Context Protocol)**：一種連接 AI 模型與外部工具的標準協定。
- **Cloud Run**：Google Cloud 的全託管容器運算平台。
- **Serverless**：無伺服器架構，讓開發者專注於程式碼而非基礎設施。

## 學習目標

完成本章節後，您將能夠：

1. 理解 Cloud Run MCP Server 的用途。
2. 認識透過 AI Agent 操作 Cloud Run 的優勢。
3. 了解使用前的準備工作。

## 步驟說明

### 步驟 1：認識 Cloud Run MCP

#### 我們在做什麼？

了解 Cloud Run MCP Server 在開發流程中的角色。它是一個橋樑，讓 AI Agent (如 Cursor, Windsurf 等) 能夠直接與您的 Google Cloud Run 專案互動。

#### 為什麼需要這樣做？

傳統上，要檢查 Cloud Run 狀態、閱讀 Log 或部署服務，開發者需要切換到瀏覽器開啟 Google Cloud Console 或使用終端機的 `gcloud` 指令。透過 MCP，您可以在 IDE 內直接用自然語言請 AI 幫您完成這些任務，大幅減少 Context Switch。

### 步驟 2：事前準備

#### 我們在做什麼？

確保您的環境已準備好使用 Cloud Run MCP。

1. **Google Cloud Project**：您需要有一個已啟用 Cloud Run API 的 GCP 專案。
2. **權限設定**：您的環境需要有適當的 `gcloud` 憑證。通常透過 `gcloud auth application-default login` 設定。
3. **MCP Server 安裝**：確保您的 AI 編輯器已設定 `cloudrun` MCP server。

#### 為什麼需要這樣做？

MCP Server 依賴原本的 GCP 憑證來進行驗證與授權。如果沒有正確登入，AI Agent 將無法存取您的雲端資源。

## 常見問題 Q&A

### Q1：Cloud Run MCP 可以完全取代 Cloud Console 嗎？

**答：** 不行。MCP 主要提供常用的操作（如查詢服務、看 Log、簡單部署）。對於複雜的權限設定 (IAM)、網路詳細配置或計費管理，仍建議使用 Google Cloud Console。

### Q2：使用這個 MCP 需要付費嗎？

**答：** MCP Server 本身是免費的開源工具。但它所操作的 Google Cloud Run 資源會依照 Google Cloud 的定價標準收費。

## 重點整理

| 概念         | 說明                                  |
| ------------ | ------------------------------------- |
| **整合性**   | 直接在 IDE 內操作雲端資源，維持心流。 |
| **可觀察性** | 透過 AI 快速檢索與分析服務 Log。      |
| **自動化**   | 簡化部署流程，減少指令輸入錯誤學。    |

---

[⬅️ 返回 Cloud Run MCP 索引](./index.md)
