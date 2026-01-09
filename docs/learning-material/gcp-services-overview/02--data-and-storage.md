# 資料與儲存服務

## 關鍵字

- **Firestore**：Google Cloud 的 NoSQL 文件資料庫。
- **Cloud Storage (GCS)**：物件儲存服務，類似 Amazon S3。
- **Singleton Pattern**：單例模式，確保應用程式中只有一個服務實例。

## 學習目標

完成本章節後，您將能夠：

1. 理解 Firestore 與 Cloud Storage 在專案中的應用場景。
2. 閱讀 `firestore_service.py` 與 `storage_service.py` 的核心邏輯。
3. 區分模擬器模式與正式環境模式的初始化差異。

## 步驟說明

### 步驟 1：認識 Firestore 服務

#### 我們在做什麼？

分析 `backend/services/firestore_service.py`，了解如何透過 Python SDK 連線 Firestore。

#### 為什麼需要這樣做？

Firestore 是本專案的主要資料儲存服務。理解其連線邏輯有助於除錯與效能優化。

#### 程式碼範例

```python
# 取自 backend/services/firestore_service.py
from google.cloud import firestore

class FirestoreService:
    """Firestore 客戶端，同時支援模擬器與正式環境。"""

    _instance = None  # 單例模式
    _db = None

    def __init__(self):
        if self._db is not None:
            return  # 已初始化則跳過

        settings = get_settings()

        if settings.use_firestore_emulator:
            # 設定模擬器主機位址
            os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore_emulator_host

        # 建立 Firestore 客戶端
        project = settings.google_cloud_project or "elevenlabs-local"
        self._db = firestore.Client(project=project)
```

#### 重點說明

| 項目                      | 說明                                            |
| ------------------------- | ----------------------------------------------- |
| `FIRESTORE_EMULATOR_HOST` | 環境變數，當設定此值時 SDK 會自動連線至模擬器。 |
| 單例模式                  | 避免重複建立連線，節省資源。                    |
| `project` 參數            | 即使使用模擬器也需要指定專案 ID。               |

---

### 步驟 2：認識 Cloud Storage 服務

#### 我們在做什麼？

分析 `backend/services/storage_service.py`，了解如何上傳與管理檔案。

#### 為什麼需要這樣做？

音頻檔案與使用者上傳的文件都儲存在 GCS。理解此服務的運作方式是開發音頻功能的基礎。

#### 程式碼範例

```python
# 取自 backend/services/storage_service.py
from google.cloud import storage
from google.auth.credentials import AnonymousCredentials

class StorageService:
    """GCS 客戶端，支援 fake-gcs-server 與正式環境。"""

    def __init__(self):
        settings = get_settings()

        if settings.use_mock_storage:
            # 使用本地檔案系統模擬
            self._mock_storage_dir = Path("temp_storage") / self._bucket_name
            self._mock_storage_dir.mkdir(parents=True, exist_ok=True)

        elif settings.use_gcs_emulator:
            # 連線至 fake-gcs-server
            self._client = storage.Client(
                credentials=AnonymousCredentials(),
                project=settings.google_cloud_project or "elevenlabs-local",
            )
            self._client._http._base_url = settings.gcs_emulator_host
        else:
            # 正式環境
            self._client = storage.Client(project=settings.google_cloud_project)
```

#### 重點說明

| 模式             | 使用情境                                     | 設定方式                |
| ---------------- | -------------------------------------------- | ----------------------- |
| **Mock Storage** | 最輕量測試，使用本地檔案系統。               | `USE_MOCK_STORAGE=true` |
| **GCS Emulator** | 接近真實的開發測試，使用 `fake-gcs-server`。 | `USE_GCS_EMULATOR=true` |
| **Production**   | 正式環境，連線真實 GCS。                     | 預設行為                |

## 常見問題 Q&A

### Q1：使用模擬器的資料在重啟後會消失嗎？

**答：** 預設情況下會消失。若需要保留資料，可以設定 Docker Volume 進行資料持久化。

### Q2：如何在程式碼中取得這些服務？

**答：** 使用提供的工廠函式：

```python
from backend.services.firestore_service import get_firestore_service
from backend.services.storage_service import get_storage_service

firestore = get_firestore_service()
storage = get_storage_service()
```

## 重點整理

| 服務              | 用途                         | 關鍵檔案                                            |
| ----------------- | ---------------------------- | --------------------------------------------------- |
| **Firestore**     | 對話紀錄、音頻歷史、設定資料 | `firestore_service.py`, `firestore_data_service.py` |
| **Cloud Storage** | 音頻檔案、上傳文件           | `storage_service.py`                                |

---

## 參考程式碼來源

| 檔案路徑                                | 說明                     |
| --------------------------------------- | ------------------------ |
| `backend/services/firestore_service.py` | Firestore 客戶端封裝     |
| `backend/services/storage_service.py`   | Cloud Storage 客戶端封裝 |

---

[⬅️ 返回 GCP 服務總覽 索引](./index.md)
