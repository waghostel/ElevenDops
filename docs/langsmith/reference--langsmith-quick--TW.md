# LangSmith Debug 整合 - 快速參考

在 ElevenDops 中使用 LangSmith 除錯功能的快速參考指南。

## 快速設定

### 1. 環境設定

```bash
# 加入 .env 檔案
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=elevendops-langgraph-debug
LANGSMITH_TRACING=true
LANGSMITH_TRACE_LEVEL=info
```

### 2. 啟動後端

```bash
uv run uvicorn backend.main:app --reload
```

### 3. 驗證設定

```bash
curl http://localhost:8000/api/debug/health
```

## 快速指令

### 健康檢查

```bash
curl http://localhost:8000/api/debug/health
```

### 除錯腳本生成

```bash
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_content": "糖尿病是一種慢性疾病...",
    "prompt": "建立關於糖尿病的病患衛教腳本"
  }'
```

### 建立除錯工作階段

```bash
curl -X POST http://localhost:8000/api/debug/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "我的除錯工作階段"}'
```

### 列出除錯工作階段

```bash
curl http://localhost:8000/api/debug/sessions
```

### 本地 Studio

```bash
cd langsmith-studio
pnpm run dev
```

## 除錯層級

| 層級    | 使用情境     | 擷取的資料                      |
| ------- | ------------ | ------------------------------- |
| `debug` | 詳細疑難排解 | 所有工作流程資料、輸入/輸出狀態 |
| `info`  | 一般監控     | 基本資訊、時間、狀態            |
| `error` | 生產環境監控 | 僅錯誤和堆疊追蹤                |

## 常見工作流程

### 基本除錯工作階段

```bash
# 1. 建立工作階段
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/debug/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "測試工作階段"}' | jq -r '.session_id')

# 2. 執行除錯
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d "{
    \"knowledge_content\": \"測試內容\",
    \"prompt\": \"測試提示\",
    \"session_name\": \"測試工作階段\",
    \"debug_level\": \"debug\"
  }"

# 3. 結束工作階段
curl -X POST http://localhost:8000/api/debug/sessions/$SESSION_ID/end
```

### 檢查設定

```bash
uv run python -c "
from backend.config import get_settings
settings = get_settings()
print(f'LangSmith configured: {settings.is_langsmith_configured()}')
print(f'Project: {settings.langsmith_project}')
print(f'Trace level: {settings.langsmith_trace_level}')
"
```

### 測試追蹤器服務

```bash
uv run python -c "
from backend.services.langsmith_tracer import get_tracer
tracer = get_tracer()
print(f'Tracer available: {tracer.is_available()}')
"
```

## API 端點快速參考

| 端點                           | 方法 | 用途             |
| ------------------------------ | ---- | ---------------- |
| `/api/debug/health`            | GET  | 檢查服務狀態     |
| `/api/debug/script-generation` | POST | 執行追蹤工作流程 |
| `/api/debug/sessions`          | GET  | 列出除錯工作階段 |
| `/api/debug/sessions`          | POST | 建立除錯工作階段 |
| `/api/debug/sessions/{id}`     | GET  | 取得工作階段詳情 |
| `/api/debug/sessions/{id}/end` | POST | 結束除錯工作階段 |

## 環境變數

| 變數                    | 預設值                       | 說明                       |
| ----------------------- | ---------------------------- | -------------------------- |
| `LANGCHAIN_API_KEY`     | -                            | LangSmith API 金鑰（必需） |
| `LANGCHAIN_PROJECT`     | `elevendops-langgraph-debug` | 專案名稱                   |
| `LANGSMITH_TRACING`     | `true`                       | 啟用/停用追蹤              |
| `LANGSMITH_TRACE_LEVEL` | `info`                       | 追蹤詳細程度               |

## 疑難排解快速修復

### LangSmith 未設定

```bash
# 檢查 API 金鑰是否已設定
echo $LANGCHAIN_API_KEY

# 設定 API 金鑰
export LANGCHAIN_API_KEY=your_key_here
```

### 服務不可用

```bash
# 檢查網路連線
curl -I https://api.smith.langchain.com

# 系統會優雅降級 - 檢查健康檢查端點
curl http://localhost:8000/api/debug/health
```

### 本地 Studio 連線失敗

```bash
# 檢查後端是否執行中
curl http://localhost:8000/api/debug/health

# 啟動 studio
cd langsmith-studio && pnpm run dev
```

## 測試指令

### 執行所有除錯測試

```bash
uv run python -m pytest tests/ -k "debug" -v
```

### 執行 LangSmith 測試

```bash
uv run python -m pytest tests/ -k "langsmith" -v
```

### 執行特定測試檔案

```bash
uv run python -m pytest tests/test_debug_api_props.py -v
```

## 網址

| 服務             | 網址                                       |
| ---------------- | ------------------------------------------ |
| 後端 API         | http://localhost:8000                      |
| 除錯健康檢查     | http://localhost:8000/api/debug/health     |
| API 文件         | http://localhost:8000/docs                 |
| LangSmith 儀表板 | https://smith.langchain.com                |
| 本地 Studio      | 在 langsmith-studio/ 中執行 `pnpm run dev` |

## 檔案位置

| 元件         | 路徑                                                 |
| ------------ | ---------------------------------------------------- |
| Debug API    | `backend/api/routes/debug.py`                        |
| 追蹤器服務   | `backend/services/langsmith_tracer.py`               |
| 工作流程服務 | `backend/services/langgraph_workflow.py`             |
| 設定         | `backend/config.py`                                  |
| 本地 Studio  | `langsmith-studio/`                                  |
| 測試         | `tests/test_*debug*.py`、`tests/test_*langsmith*.py` |

## 效能影響

| 除錯層級 | 延遲開銷      | 頻寬使用           |
| -------- | ------------- | ------------------ |
| `debug`  | ~100-200 毫秒 | 每次追蹤約 10-50KB |
| `info`   | ~50-100 毫秒  | 每次追蹤約 2-10KB  |
| `error`  | ~10-20 毫秒   | 每次追蹤約 1-5KB   |

## 整合狀態

✅ **已完成功能：**

- LangSmith 追蹤器服務
- Debug API 端點
- 工作階段管理
- 優雅降級
- 本地 Studio 環境
- 基於屬性的測試（53 個測試通過）

---

**快速連結：**

- [完整文件](integration--langsmith-debug.md)
- [Debug API 參考](DEBUG_API_REFERENCE.md)
- [架構指南](MVP1_ARCHITECTURE.md)
