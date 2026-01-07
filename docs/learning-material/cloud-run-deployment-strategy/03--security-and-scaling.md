# 安全性與縮放配置 (Security and Scaling)

## 關鍵字

- **Non-root User**：防止容器內的進程擁有系統管理權限。
- **Secret Manager**：安全地管理與注入 API 金鑰。
- **Auto-scaling**：根據流量自動調整執行個體數量。
- **Environment Variables**：配置應用程式運行所需的環境參數。

## 學習目標

完成本章節後，您將能夠：

1. 理解如何在容器中實作非根用戶安全規範。
2. 掌握透過 Secret Manager 管理機敏資訊的方法。
3. 了解 Cloud Run 的縮放機制（0 到 10 個執行個體）。

## 步驟說明

### 步驟 1：實作非根用戶安全

#### 我們在做什麼？

在 Dockerfile 中建立 `appuser` 並切換至該用戶執行程式，而非使用預設的 `root`。

#### 為什麼需要這樣做？

這是資安的最佳實踐（最小權限原則）。如果程式存在漏洞被攻擊者入侵，非根用戶能將損害限制在應用層，防止攻擊者控制整個宿主系統。

#### 程式碼範例

```dockerfile
# 建立非根用戶
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

# 變更檔案所有權
COPY --chown=appuser:appuser backend/ ./backend/

# 切換用戶
USER appuser
```

### 步驟 2：整合 Secret Manager

#### 我們在做什麼？

在 `cloudbuild.yaml` 的部署參數中，將 Secrets 對應到環境變數。

#### 為什麼需要這樣做？

不應將 API Key（如 ElevenLabs 或 OpenAI）直接寫在代碼或環境變數設定中。Secret Manager 提供加密儲存，且只有具備權限的服務帳戶能存取。

#### 程式碼範例

```yaml
# cloudbuild.yaml 中的部署步驟
- "--set-secrets"
- "ELEVENLABS_API_KEY=elevenlabs-api-key:latest"
```

### 步驟 3：配置自動縮放 (Scaling)

#### 我們在做什麼？

設定最小實例數（min-instances）為 0，最大實例數（max-instances）為 10。

#### 為什麼需要這樣做？

- **Min 0**：在沒有流量時完全關閉實例，節省成本（零成本待機）。
- **Max 10**：在高流量時限制擴展規模，防止帳單爆表（成本控制）。

## 常見問題 Q&A

### Q1：設定 Min instances 為 0 會有「冷啟動」 (Cold Start) 問題嗎？

**答：** 會。第一個請求可能需要幾秒鐘來啟動容器。如果您的應用對響應時間極度敏感，建議將 Min instances 設為 1，但這會產生持續的基礎費用。

### Q2：如何更新 Secret 的內容？

**答：** 在 GCP 控制台的 Secret Manager 中新增一個「版本」(Version)。由於我們的部署腳本使用 `:latest`，下一次自動部署時就會抓取最新的金鑰。

## 重點整理

| 配置項  | 設定值           | 目的                       |
| ------- | ---------------- | -------------------------- |
| User    | `appuser`        | 安全合規，防止權限提升攻擊 |
| Secret  | `Secret Manager` | 加密管理，集中金鑰控制     |
| Scaling | `0 - 10`         | 成本優化與負載平衡         |

## 延伸閱讀

- [Secret Manager 管理指南](../../docs/cloud-run-deployment/guide--secret-management.md)
- [Cloud Run 自動縮放原理](https://cloud.google.com/run/docs/configuring/max-instances)

---

## 參考程式碼來源

本文件中的程式碼範例參考自以下專案檔案：

| 檔案路徑              | 說明                        |
| --------------------- | --------------------------- |
| `Dockerfile.cloudrun` | 包含使用者權限配置          |
| `cloudbuild.yaml`     | 包含 Secret 與 Scaling 設定 |
