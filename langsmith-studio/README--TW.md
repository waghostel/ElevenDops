# LangSmith Studio

用於除錯 ElevenDops LangGraph 工作流程的本機開發工具。

## 設定

```bash
cd langsmith-studio
pnpm install
```

## 配置

設定以下環境變數（或建立 `.env` 檔案）：

```bash
# 可選 - LangSmith API 金鑰用於雲端功能
LANGCHAIN_API_KEY=your_api_key_here

# 可選 - 後端 URL（預設為 localhost:8000）
BACKEND_URL=http://localhost:8000

# 可選 - LangSmith 專案名稱
LANGCHAIN_PROJECT=elevendops-langgraph-debug
```

## 使用方式

### 啟動 Studio

```bash
pnpm dev
```

這將會：

1. 檢查與後端除錯 API 的連線
2. 顯示 LangSmith 儀表板 URL
3. 顯示可用的除錯端點

### 測試連線

```bash
pnpm test
```

驗證後端除錯 API 是否可存取並正常回應。

## 除錯端點

後端提供以下除錯端點：

| 方法 | 端點                           | 說明                   |
| ---- | ------------------------------ | ---------------------- |
| POST | `/api/debug/script-generation` | 執行帶有追蹤的工作流程 |
| GET  | `/api/debug/sessions`          | 列出除錯工作階段       |
| POST | `/api/debug/sessions`          | 建立新的工作階段       |
| GET  | `/api/debug/sessions/{id}`     | 取得工作階段詳細資訊   |
| GET  | `/api/debug/health`            | 健康檢查               |

## 範例：除錯腳本生成

```bash
curl -X POST http://localhost:8000/api/debug/script-generation \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_content": "Patient education about diabetes management...",
    "prompt": "Generate a clear, empathetic script for patients",
    "model_name": "gemini-2.0-flash",
    "debug_level": "debug",
    "session_name": "diabetes-test-1"
  }'
```

回應包含：

- `trace_id` - 唯一的追蹤識別碼
- `session_id` - 工作階段 ID（如果提供了工作階段名稱）
- `execution_status` - completed/error（已完成/錯誤）
- `steps` - 詳細的逐步執行資料
- `langsmith_url` - LangSmith 儀表板連結
