# Cloud Run 整合

## 關鍵字

- **Secret Volume**：將 Secret 掛載為檔案系統中的檔案。
- **Secret Environment Variable**：將 Secret 注入為環境變數。
- **Service Account**：Cloud Run 服務用來存取 Secret 的身分。

## 學習目標

完成本章節後，您將能夠：

1. 在 Cloud Run 部署時設定 Secret 存取
2. 選擇 Volume 或 Environment Variable 方式
3. 設定正確的 IAM 權限

## 步驟說明

### 步驟 1：理解兩種注入方式

#### 我們在做什麼？

Cloud Run 支援兩種方式將 Secret 提供給應用程式。

#### 比較表

| 方式                     | 優點                | 缺點                  | 適用情境     |
| ------------------------ | ------------------- | --------------------- | ------------ |
| **Environment Variable** | 程式碼改動小        | Secret 更新需重新部署 | 簡單配置     |
| **Secret Volume**        | Secret 更新自動生效 | 需讀取檔案            | 需要即時輪換 |

### 步驟 2：設定 IAM 權限

#### 我們在做什麼？

授權 Cloud Run 的 Service Account 存取 Secret。

#### 為什麼需要這樣做？

Cloud Run 服務使用 Service Account 身分執行。該 Service Account 必須有 `Secret Manager Secret Accessor` 角色。

#### 命令列範例

```bash
# 查看 Cloud Run 使用的 Service Account
gcloud run services describe my-service --region=asia-east1 \
    --format="value(spec.template.spec.serviceAccountName)"

# 預設為 {PROJECT_NUMBER}-compute@developer.gserviceaccount.com

# 授權存取特定 Secret
gcloud secrets add-iam-policy-binding ELEVENLABS_API_KEY \
    --member="serviceAccount:123456789-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 步驟 3：部署時設定 Secret 環境變數

#### 我們在做什麼？

在部署 Cloud Run 時，將 Secret 注入為環境變數。

#### 命令列範例

```bash
gcloud run deploy my-service \
    --image=gcr.io/my-project/my-app \
    --region=asia-east1 \
    --set-secrets="ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:latest"
    # 格式: ENV_VAR_NAME=SECRET_NAME:VERSION
```

#### 在程式中使用

```python
import os

# 直接讀取環境變數，不需要 Secret Manager SDK
api_key = os.environ.get("ELEVENLABS_API_KEY")
```

### 步驟 4：使用 Secret Volume

#### 我們在做什麼？

將 Secret 掛載為檔案，程式讀取檔案內容。

#### 命令列範例

```bash
gcloud run deploy my-service \
    --image=gcr.io/my-project/my-app \
    --region=asia-east1 \
    --set-secrets="/secrets/api-key=ELEVENLABS_API_KEY:latest"
    # 格式: MOUNT_PATH=SECRET_NAME:VERSION
```

#### 在程式中使用

```python
from pathlib import Path

def get_secret_from_file(path: str) -> str:
    """
    從掛載的 Secret 檔案讀取值
    """
    return Path(path).read_text().strip()

# 使用範例
api_key = get_secret_from_file("/secrets/api-key")
```

#### 流程圖

```mermaid
graph TD
    subgraph Cloud Run
        A[Container]
        B[/secrets/api-key]
    end

    subgraph Secret Manager
        C[ELEVENLABS_API_KEY]
    end

    C -->|掛載| B
    A -->|讀取| B
```

## 常見問題 Q&A

### Q1：更新 Secret 後需要重新部署嗎？

**答：**

- **Environment Variable**：需要重新部署
- **Secret Volume**：Container 重啟時自動更新（但運行中不會）

### Q2：如何在 Cloud Build 中使用 Secret？

**答：** 在 `cloudbuild.yaml` 中使用 `secretEnv`。

```yaml
steps:
  - name: "gcr.io/cloud-builders/gcloud"
    entrypoint: "bash"
    args: ["-c", "echo $$API_KEY"]
    secretEnv: ["API_KEY"]

availableSecrets:
  secretManager:
    - versionName: projects/my-project/secrets/ELEVENLABS_API_KEY/versions/latest
      env: "API_KEY"
```

## 重點整理

| 方式        | 設定指令                               | 程式讀取方式       |
| ----------- | -------------------------------------- | ------------------ |
| **Env Var** | `--set-secrets="VAR=SECRET:VERSION"`   | `os.environ.get()` |
| **Volume**  | `--set-secrets="/path=SECRET:VERSION"` | 讀取檔案           |

---

## 參考程式碼來源

| 檔案路徑            | 說明             |
| ------------------- | ---------------- |
| `backend/config.py` | 環境變數讀取邏輯 |
