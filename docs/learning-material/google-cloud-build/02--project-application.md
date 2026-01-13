# ElevenDops 專案中的 Cloud Build 應用

## 關鍵字

- **Dockerfile.cloudrun**：專為 Cloud Run 生產環境優化的 Docker 設定檔。
- **Container Registry / Artifact Registry**：ElevenDops 使用 Artifact Registry 來儲存應用程式映像檔。
- **CI/CD Pipeline**：持續整合與持續部署的自動化流程。
- **gcloud run deploy**：用於執行部署動作的建置器命令。
- **Secret Management**：在部署時從 Google Cloud Secret Manager 注入私鑰或 API Key。

## 學習目標

完成本章節後，您將能夠：

1. 詳解 ElevenDops 專案中 `cloudbuild.yaml` 的各個步驟。
2. 理解專案如何進行自動化建置、推送與部署。
3. 了解部署過程中環境變數與機密資訊的處理方式。

## 步驟說明

### 步驟 1：建置容器映像檔 (Build)

#### 我們在做什麼？

使用 `docker build` 命令，並指定 `Dockerfile.cloudrun` 作為藍圖，將後端 FastAPI 與前端 Streamlit 程式碼打包進容器。

#### 為什麼需要這樣做？

確保開發環境與生產環境的一致性，並將應用程式封裝為可運行的單元。

#### 程式碼範例 (`cloudbuild.yaml`)

```yaml
# 使用 Docker 建置器
- name: "gcr.io/cloud-builders/docker"
  id: "build"
  args:
    - "build"
    - "-t"
    - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:${SHORT_SHA}"
    - "-t"
    - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:latest"
    - "-f"
    - "Dockerfile.cloudrun"
    - "."
```

---

### 步驟 2：推送到 Artifact Registry (Push)

#### 我們在做什麼？

將建置好的映像檔推送至 Google Cloud 上的私有儲存庫（Artifact Registry）。

#### 為什麼需要這樣做？

讓 Cloud Build 接下來的部署步驟（以及 Cloud Run 服務）可以存取這個映像檔。我們同時推送 `SHORT_SHA`（用於版本追蹤）與 `latest`（用於快速識別最新版）標籤。

#### 程式碼範例 (`cloudbuild.yaml`)

```yaml
- name: "gcr.io/cloud-builders/docker"
  id: "push"
  args:
    - "push"
    - "--all-tags"
    - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app"
  waitFor:
    - "build" # 確保建置完成後才執行推送
```

---

### 步驟 3：部署到 Cloud Run (Deploy)

#### 我們在做什麼？

呼叫 `gcloud run deploy` 命令，指定剛才推送的映像檔，並設定對應的資源（CPU/Memory）、服務帳戶、秘密金鑰（Secrets）與環境變數。

#### 為什麼需要這樣做？

這是 CI/CD 流程的最後一哩路，將應用程式實際上線。

#### 關鍵實作細節

- **Secrets 管理**：使用 `--set-secrets` 將 Secret Manager 中的金鑰掛載為環境變數（例如 `ELEVENLABS_API_KEY`）。
- **資源限制**：設定 `2 CPU` 與 `1Gi Memory` 以應付處理語音生成的需求。
- **地區設定**：使用 `us-central1` 以符合專案預設區域並享有較低成本。

```yaml
- name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
  id: "deploy"
  entrypoint: "gcloud"
  args:
    - "run"
    - "deploy"
    - "elevendops"
    - "--image"
    - "${_REGION}-docker.pkg.dev/${PROJECT_ID}/elevendops/app:${SHORT_SHA}"
    - "--region"
    - "${_REGION}"
    # ... 其他設定 ...
    - "--set-secrets"
    - "ELEVENLABS_API_KEY=elevenlabs-api-key:latest,GOOGLE_API_KEY=google-api-key:latest,LANGSMITH_API_KEY=langsmith-api-key:latest"
```

## 常見問題 Q&A

### Q1：`cloudbuild.yaml` 裡的 `${PROJECT_ID}` 跟 `${SHORT_SHA}` 是哪來的？

**答：** 這些是 Cloud Build 的預設變數。`PROJECT_ID` 會根據您執行的專案自動帶入，而 `SHORT_SHA` 則是觸發建置的 Git commit hash 的前七碼，非常適合用來做版本標示。

### Q2：為什麼部署步驟要用 `waitFor: ['push']`？

**答：** 預設情況下，Cloud Build 的步驟是循序執行的。但在複雜的設定中，明確標示依賴關係（依序執行或併行執行）可以確保邏輯正確，例如部署前映像檔必須已經存在於儲存庫中。

## 重點整理

| 階段       | 目的                     | 關鍵指令            |
| ---------- | ------------------------ | ------------------- |
| **Build**  | 建立 Docker 映像檔       | `docker build`      |
| **Push**   | 儲存至 Artifact Registry | `docker push`       |
| **Deploy** | 更新 Cloud Run 服務      | `gcloud run deploy` |

---

## 參考程式碼來源

本文件中的配置參考自以下專案檔案：

| 檔案路徑                                         | 說明                             |
| ------------------------------------------------ | -------------------------------- |
| [cloudbuild.yaml](../../cloudbuild.yaml)         | 專案的主 CI/CD 設定檔            |
| [Dockerfile.cloudrun](../../Dockerfile.cloudrun) | 專供雲端部署使用的 Docker 定義檔 |

---

[⬅️ 返回 Google Cloud Build 索引](./index.md)
