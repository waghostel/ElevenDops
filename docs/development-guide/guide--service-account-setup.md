# Google Cloud Service Account Setup Guide

本指南詳細說明如何建立並設定服務帳號 (Service Account)，以在本地開發環境支援 Google Cloud Storage (GCS) 的「簽章網址 (Signed URL)」功能，並涵蓋資安風險與部署策略。

## 1. 為什麼需要服務帳號？

您目前使用的 `gcloud auth application-default login` 是「使用者憑證」，它只包含存取權限的 Token，但不包含「私鑰」。GCP 的 Signed URL 需要私鑰來進行加密簽章。因此，我們需要一個服務帳號並下載其 JSON Key 來進行本地測試。

## 2. 建立服務帳號與權限設定

### 步驟流程

1. **前往 GCP 控制台**：導覽至 [IAM 與管理 > 服務帳號](https://console.cloud.google.com/iam-admin/serviceaccounts)。
2. **建立帳號**：點擊「建立服務帳號」，輸入名稱（例如 `elevendops-dev`）。
3. **授予權限 (關鍵步驟)**：
   請賦予以下兩個角色，並了解其用途：

   | 角色名稱 (英文)                                      | 角色名稱 (中文)                         | 用途與權限解釋                                                                                                                                                             |
   | :--------------------------------------------------- | :-------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | **`Storage Object Admin`**                           | 儲存物件管理員                          | **GCS 存取權**：<br>允許讀取、寫入、刪除 Bucket 內的檔案。更重要的是，它隱含了「代表此帳號簽署網址」的權限，讓後端能產生 Signed URL。                                      |
   | **`Firebase Admin`**<br>_(或 Cloud Datastore Owner)_ | Firebase 管理員<br>_(雲端資料庫擁有者)_ | **Firestore 存取權**：<br>由於您使用了自定義資料庫 ID (`elevendops-db`)，預設的 User 角色可能權限不足。此高權限角色確保後端能順利讀寫資料庫，避免本地開發時出現 403 錯誤。 |

4. **建立金鑰 (Key)**：
   - 進入該服務帳號詳情 >「金鑰」分頁 >「新增金鑰」>「建立新金鑰」> 選擇 **JSON**。
   - **⚠️ 重要**：下載的 JSON 檔案即為您的私鑰，擁有此檔案等同擁有上述權限。

---

## 3. 資安風險：如果 Key 被盜用會怎樣？

這是一個非常重要的問題。如果駭客取得了您的 `service-account-key.json`，根據我們賦予的權限，潛在風險包括：

1.  **資料外洩 (GCS)**：駭客可以下載 Bucket 內的所有音訊檔案，包括敏感的病患對話錄音。
2.  **資料篡改/破壞 (GCS)**：駭客可以刪除所有備份，或上傳惡意軟體偽裝成音訊檔。
3.  **資料庫破壞 (Firestore)**：如果賦予了 `Cloud Datastore Owner` 或 `Firebase Admin`，駭客可以讀取、修改甚至「刪除」整個資料庫的內容，造成毀滅性打擊。
4.  **惡意簽章**：駭客可以用此 Key 產生無限期的 Signed URL，長期盜連您的資源，甚至造成鉅額流量費用。

> [!CAUTION] > **絕對禁止**將此 JSON 檔案 Commit 到 Git 倉庫！請務必確保它列在 `.gitignore` 中。

---

## 4. Cloud Run 部署設定

當您將應用程式部署到 Cloud Run 時，**不需要 (也不應該)** 上傳這個 JSON Key。

### Google 的建議作法：託管識別 (Managed Identity)

Cloud Run 運作在 Google 的基礎設施上，它會自動使用「關聯的服務帳號」來獲取權限，無需實體金鑰檔案。

#### 您需要做的事：

1.  **不要設定** `GOOGLE_APPLICATION_CREDENTIALS` 環境變數 (在 Cloud Run 上)。
2.  **指派服務帳號**：
    - 在部署 Cloud Run 時，您可以選擇 "Security" (安全性) 選項卡。
    - 在 "Service Account" 欄位，選擇您剛剛建立的 `elevendops-dev` (或是新建一個專用的 `elevendops-prod`)。
3.  **權限繼承**：Cloud Run 會自動繼承該服務帳號的 IAM 權限 (Storage Object Admin + Firebase Admin)。
    - **注意**：在 Cloud Run 環境下，Google 的 SDK 會自動改用一種「IAM API 呼叫」的方式來產生 Signed URL（稱為 `signBlob` API），而不需要本地讀取私鑰檔案。這也是為什麼我們在程式碼中會看到不同的簽章邏輯。

---

## 5. 開發結束後的金鑰管理 (Best Practices)

### Q: 開發結束後需要刪除這個 Key 嗎？

**A: 強烈建議刪除，或至少定期輪替。**

- **最佳實踐**：
  1.  **短期使用**：完成本地功能的開發與驗證後，若短期內不再需要模擬 Signed URL，請直接在 GCP 控制台「刪除」該 Key。這能將風險降到零。
  2.  **定期輪替**：若需長期開發，請每隔一段時間（如 90 天）刪除舊 Key 並建立新 Key。
  3.  **最小權限原則**：如果開發者只需要讀取 GCS 不需寫入，可以另外建立一個權限較小的服務帳號供本地使用。

**刪除步驟**：
前往 GCP 控制台 > IAM > 服務帳號 > 選擇帳號 >「金鑰」分頁 > 點擊垃圾桶圖示刪除。

---

## 6. 本地開發設定回顧

將下載的 JSON 檔案放入專案根目錄（確保已 `.gitignore`），設定 `.env`：

```bash
# 指向 JSON 金鑰的路徑
GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"
```

只要設定了此變數，我們的後端程式 (`audio_service.py`) 就會自動切換為 **Signed URL 模式**，讓您在本地也能看到與生產環境一致的簽章網址行為。
