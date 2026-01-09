# 資料持久化模型 (Data Persistence)

## 關鍵字

- **Emulator (模擬器)**：在記憶體中模擬雲端服務的本地程式
- **Firestore Native Mode**：Firestore 的標準運作模式（文件/集合結構）
- **Blob (Binary Large Object)**：二進位大型物件（如圖片、音檔）
- **Bucket (儲存桶)**：存放 Blob 的容器

## 學習目標

完成本章節後，您將能夠：

1. 理解模擬器與真實服務在「資料保存」上的差異
2. 認識 Firestore 的集合文件結構
3. 理解 GCS 的物件儲存概念

## 步驟說明

### 步驟 1：理解模擬器 vs 真實服務

#### 我們在做什麼？

比較 `USE_FIRESTORE_EMULATOR=true` 與 `false` 的行為差異。

#### 為什麼需要這樣做？

- **模擬器 (Emulator)**：
  - 資料通常存在 **記憶體 (RAM)** 中。
  - 重新啟動 Docker/電腦後，資料**會消失**（除非設定了 import/export）。
  - 速度極快，零成本，無網路延遲。
- **真實服務 (Real Service)**：
  - 資料存在 **Google 資料中心** 的硬碟中。
  - 永久保存，隨時隨地可存取。
  - 會產生極微小的費用與網路延遲。

遷移到真實服務後，您今天寫入的測試資料，明天打開電腦還會在。

### 步驟 2：Firestore 資料結構

#### 我們在做什麼？

理解 Firestore 的 `Collection` (集合) 與 `Document` (文件) 結構。

#### 為什麼需要這樣做？

Firestore 是 **NoSQL** 資料庫，結構像 JSON 樹：

- **Collection**: 資料夾 (如 `users`)
- **Document**: 檔案 (如 `user_123`)
  - **Data**: 檔案內容 (JSON)
  - **Sub-collection**: 子資料夾 (如 `orders`)

在遷移後，您可以使用 GCP Console 的強大 GUI 來瀏覽這些資料，比本地模擬器更直觀。

#### 程式碼範例

```python
# backend/services/firestore_data_service.py
# 這是我們如何操作 Firestore 結構的範例

async def create_user_doc(self, user_id, data):
    # 存取 'users' 集合中的 'user_id' 文件
    doc_ref = self._db.collection("users").document(user_id)
    # 寫入資料
    await doc_ref.set(data)
```

### 步驟 3：GCS 物件儲存

#### 我們在做什麼？

將音檔 (.mp3) 存入 Cloud Storage Bucket。

#### 為什麼需要這樣做？

Firestore 只適合存「文字資料」（文件），不適合存大檔案。
**Cloud Storage (GCS)** 專門設計用來存圖片、影片、音檔。

- **Bucket**：像是一個頂層磁碟機 (D 槽)。
- **Object**：檔案本身。

遷移後，您的音檔會有一個公開或簽署的 **URL** (`https://storage.googleapis.com/...`)，這讓前端可以在任何地方播放它，而不僅限於您的 `localhost`。

## 常見問題 Q&A

### Q1：切換到真實服務後，我原本建立的 Agent 還在嗎？

**答：** **不在了**。因為模擬器的資料是獨立的。當您切換 `CONNECTION_STRING` 或設定到真實專案時，您面對的是一個全新的、空的資料庫。您需要重新建立測試資料。

### Q2：會很花錢嗎？

**答：** Firestore 和 GCS 都有**免費額度 (Free Tier)**。

- Firestore：每天 50,000 次讀取，20,000 次寫入。
- GCS：5GB 的標準儲存空間。
  開發測試通常遠低於此用量，幾乎是免費的。

## 重點整理

| 概念         | 模擬器 (Local)    | 真實服務 (Cloud)      |
| ------------ | ----------------- | --------------------- |
| **資料保存** | 重啟即消失 (預設) | 永久保存              |
| **存取速度** | 極快 (Localhost)  | 視網路狀況 (Internet) |
| **檢視工具** | 需特定 UI         | GCP Console (強大)    |
| **費用**     | $0                | 用量計費 (有免費額度) |

## 延伸閱讀

- [Firestore Data Model](https://firebase.google.com/docs/firestore/data-model)
- [GCS Objects](https://cloud.google.com/storage/docs/objects)

---

## 參考程式碼來源

| 檔案路徑                    | 說明                            |
| --------------------------- | ------------------------------- |
| `backend/models/schemas.py` | 定義了寫入 Firestore 的資料形狀 |
| `docker-compose.dev.yml`    | 定義了模擬器的啟動參數          |

---

[⬅️ 返回 GCP 遷移與基礎概念 索引](./index.md)
