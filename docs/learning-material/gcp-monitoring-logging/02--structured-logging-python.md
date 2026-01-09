# Python 結構化日誌

## 關鍵字

- **Structured Logging**：以 JSON 格式輸出日誌，方便程式解析。
- **jsonPayload**：Cloud Logging 自動解析的 JSON 日誌欄位。
- **Log Correlation**：將同一請求的多條日誌關聯在一起。

## 學習目標

完成本章節後，您將能夠：

1. 在 Python 中輸出 JSON 格式日誌
2. 添加上下文資訊（如 request_id）
3. 設定日誌等級與格式

## 步驟說明

### 步驟 1：理解結構化日誌的優勢

#### 我們在做什麼？

將日誌從純文字改為 JSON 格式。

#### 比較

```python
# 傳統純文字日誌
logger.info("User login failed: user_id=123, reason=invalid_password")

# 結構化 JSON 日誌
logger.info("User login failed", extra={
    "user_id": "123",
    "reason": "invalid_password"
})
# 輸出: {"message": "User login failed", "user_id": "123", "reason": "invalid_password"}
```

#### 為什麼需要這樣做？

| 純文字             | 結構化 JSON        |
| ------------------ | ------------------ |
| 需要正規表達式解析 | 直接用欄位查詢     |
| 難以統計分析       | 可用 BigQuery 分析 |
| 格式不一致         | 格式統一           |

### 步驟 2：設定 JSON Formatter

#### 我們在做什麼？

自訂 Python logging 的輸出格式為 JSON。

#### 程式碼範例

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    將日誌格式化為 JSON，供 Cloud Logging 解析
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "logging.googleapis.com/sourceLocation": {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }
        }

        # 加入 extra 欄位
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry, ensure_ascii=False)

# 設定 Logger
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger
```

### 步驟 3：添加請求上下文

#### 我們在做什麼？

在每條日誌中自動附加 request_id，方便追蹤。

#### FastAPI 中介軟體範例

```python
import uuid
from contextvars import ContextVar
from fastapi import FastAPI, Request

# 使用 ContextVar 儲存請求級別的資料
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

app = FastAPI()

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# 自訂 LogAdapter 自動附加 request_id
class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        extra["request_id"] = request_id_var.get()
        kwargs["extra"] = extra
        return msg, kwargs

# 使用
logger = ContextAdapter(logging.getLogger(__name__), {})
logger.info("處理請求中")
# 輸出: {"message": "處理請求中", "request_id": "abc12345", ...}
```

### 步驟 4：使用 google-cloud-logging 套件

#### 我們在做什麼？

使用官方套件自動整合 Cloud Logging。

#### 程式碼範例

```python
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
import logging

# 建立 Cloud Logging 客戶端
client = google.cloud.logging.Client()

# 設定 Handler
handler = CloudLoggingHandler(client)
handler.setLevel(logging.INFO)

# 附加到 root logger
logging.getLogger().addHandler(handler)

# 使用
logger = logging.getLogger(__name__)
logger.info("這條日誌會出現在 Cloud Logging")
```

## 常見問題 Q&A

### Q1：本地開發時如何關閉 Cloud Logging？

**答：** 檢查環境變數，本地使用一般的 StreamHandler。

```python
import os

if os.getenv("USE_CLOUD_LOGGING", "false").lower() == "true":
    # 使用 CloudLoggingHandler
    pass
else:
    # 使用 StreamHandler
    pass
```

### Q2：日誌太多怎麼辦？

**答：** 調整日誌等級，只記錄 WARNING 以上；或使用取樣機制。

## 重點整理

| 概念           | 說明         | 實作方式                |
| -------------- | ------------ | ----------------------- |
| **JSON 格式**  | 便於查詢分析 | 自訂 Formatter          |
| **Request ID** | 追蹤請求流程 | Middleware + ContextVar |
| **Cloud 整合** | 官方 SDK     | google-cloud-logging    |

---

## 參考程式碼來源

| 檔案路徑                               | 說明                 |
| -------------------------------------- | -------------------- |
| `backend/main.py`                      | FastAPI 中介軟體設定 |
| `backend/services/langsmith_tracer.py` | 追蹤相關實作         |

---

[⬅️ 返回 GCP Monitoring & Logging 索引](./index.md)
