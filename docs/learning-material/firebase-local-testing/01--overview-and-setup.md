# Firebase 本地測試指南

## 關鍵字

- **Firebase Emulator**：Google 提供的本地測試工具，可模擬 Firestore、Storage 等服務。
- **Firestore**：NoSQL 文件資料庫，用於儲存應用程式資料。
- **本地開發 (Local Development)**：在開發者電腦上進行程式碼編寫與測試的過程。

## 學習目標

完成本章節後，您將能夠：

1. 理解如何在本地環境設定 Firestore 測試。
2. 區分「使用 Emulator」與「連線真實 Firebase」的差異與設定方式。
3. 了解如何透過設定檔切換測試模式。

## 步驟說明

### 步驟 1：理解兩種測試模式

#### 我們在做什麼？

在進行資料庫相關功能的開發時，我們主要有兩種測試環境的選擇：

1. **使用 Emulator (模擬器)**：在本地 Docker 容器中運行的虛擬資料庫。
2. **連線真實 Firebase**：直接連線到 Google Cloud 上的真實專案。

#### 為什麼需要這樣做？

- **Emulator** 是開發首選，因為它速度快、資料隨用隨丟 (Ephemeral)，且不會產生費用或弄髒真實數據。
- **真實 Firebase** 則用於最終驗證，確保權限、網路連線與雲端環境設定無誤。

#### 比較表

| 特性           | Emulator (模擬器)             | 真實 Firebase                    |
| :------------- | :---------------------------- | :------------------------------- |
| **資料持久性** | 重啟後通常消失 (除非設定掛載) | 永久保存                         |
| **費用**       | 免費                          | 可能產生流量或儲存費用           |
| **網路依賴**   | 不需要 (本地運行)             | 需要網路連線                     |
| **用途**       | 開發、單元測試、整合測試      | 驗收測試、與其他雲端服務整合驗證 |

### 步驟 2：設定使用 Emulator (推薦)

#### 我們在做什麼？

設定專案以使用本地 Docker 運行的 Firestore Emulator。

#### 程式碼範例

在 `.env` 檔案中設定：

```bash
# .env
# 啟用 Emulator 模式
USE_FIRESTORE_EMULATOR=True
USE_GCS_EMULATOR=True

# Emulator 連線位置 (對應 docker-compose 設定)
FIRESTORE_EMULATOR_HOST=localhost:8080
GCS_EMULATOR_HOST=http://localhost:4443
```

啟動 Emulator 的命令：

```powershell
# 啟動 docker-compose 定義的服務
docker-compose -f docker-compose.dev.yml up -d
```

### 步驟 3：設定連線真實 Firebase

#### 我們在做什麼？

設定專案以連線到 Google Cloud 上的真實 Firestore 實例。

#### 為什麼需要這樣做？

當您需要驗證資料是否能正確寫入雲端，或者測試某些 Emulator 不支援的功能時。

#### 程式碼範例

1. 修改 `.env` 設定：

```bash
# .env
# 停用 Emulator，改用真實連線
USE_FIRESTORE_EMULATOR=False
USE_GCS_EMULATOR=False

# 設定您的 Google Cloud 專案 ID
GOOGLE_CLOUD_PROJECT=your-project-id
```

2. 進行本地身分驗證：

```powershell
# 登入 Google Cloud SDK 以取得憑證
gcloud auth application-default login
```

## 常見問題 Q&A

### Q1：我怎麼知道現在連線的是 Emulator 還是真實資料庫？

**答：** 您可以檢查 `backend/services/firestore_service.py` 的初始化日誌。
如果看到 `Connecting to Firestore Emulator at ...` 表示正在使用模擬器；
如果看到 `Connecting to production Firestore` 則表示連線到真實環境。

### Q2：使用真實 Firebase 測試會影響現有資料嗎？

**答：** **會的**。寫入、刪除操作都會直接反映在雲端資料庫上。建議建立一個專門的開發用專案 (例如 `project-dev`)，不要直接連線到正式環境 (Production) 專案進行開發測試。

## 重點整理

| 設定                     | Emulator 模式       | 真實模式                                |
| :----------------------- | :------------------ | :-------------------------------------- |
| `USE_FIRESTORE_EMULATOR` | `True`              | `False`                                 |
| `GOOGLE_CLOUD_PROJECT`   | (任意或指定本地 ID) | **必須**是真實專案 ID                   |
| 認證方式                 | 不需要              | `gcloud auth application-default login` |

## 延伸閱讀

- [Firebase Local Emulator Suite 官方文件](https://firebase.google.com/docs/emulator-suite)
- [Docker Compose 官方文件](https://docs.docker.com/compose/)

---

[⬅️ 返回 Firebase 本地測試索引](./index.md)
