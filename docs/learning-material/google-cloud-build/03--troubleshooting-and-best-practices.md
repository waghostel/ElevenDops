# Cloud Build 常見問題與最佳實踐

## 關鍵字

- **Build Triggers (觸發條件)**：設定何時自動執行建置（例如推送程式碼到 `main` 分支）。
- **IAM Permissions (權限管理)**：Cloud Build 執行時所需的服務帳戶權限。
- **Build Logs (建置日誌)**：排查錯誤時最重要的資訊來源。
- **Caching (快取)**：加速建置過程的技術。

## 學習目標

完成本章節後，您將能夠：

1. 學會如何查看並分析建置失敗的日誌。
2. 了解如何設定自動化觸發器。
3. 掌握 Cloud Build 的權限配置要點（特別是部署至 Cloud Run 時）。

## 除錯與問題排查

### 1. 檢視建置日誌

#### 我們在做什麼？

當建置狀態顯示為「失敗」時，點擊進入該次建置詳情，查看每個步驟的 Console 輸出。

#### 為什麼需要這樣做？

日誌會告訴您是在哪一個步驟失敗。例如：是程式碼噴錯？還是 `docker build` 失敗？或是部署時權限不足？

---

### 2. 常見錯誤：權限不足 (Permission Denied)

#### 我們在做什麼？

在 Google Cloud Console 的「IAM 與管理」中，確保 Cloud Build 服務帳戶（格式通常為 `[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`）擁有必要的角色。

#### 常見角色需求：

- **Cloud Run Admin**：執行部署。
- **Service Account User**：以特定服務帳戶執行 Cloud Run。
- **Secret Manager Secret Accessor**：讀取部署時所需的秘密金鑰。

---

### 3. 如何手動觸發建置

#### 我們在做什麼？

在開發階段，如果您不想每次修改都推送到 Git，可以使用 `gcloud` 指令手動提交建置工作。

#### 程式碼範例

```bash
# 在專案根目錄執行
gcloud builds submit --config cloudbuild.yaml .
```

## 最佳實踐建議

| 策略             | 說明                                            | 好處                             |
| ---------------- | ----------------------------------------------- | -------------------------------- |
| **使用特定標籤** | 避免只用 `latest`，應搭配 `SHORT_SHA`           | 部署失敗時可隨時回滾（Rollback） |
| **利用快取**     | 在 `steps` 中使用 `cacheFrom`                   | 顯著縮短 `docker build` 的時間   |
| **最小權限原則** | 服務帳戶只給予必要的 IAM 角色                   | 提升系統安全性                   |
| **分散建置**     | 前後端若可以分開建置，則不要併在一個超大的 Step | 提高可維護性                     |

## 常見問題 Q&A

### Q1：我的建置等了很久都沒開始，為什麼？

**答：** 可能是因為配額限制（Quota）或正在排隊。Cloud Build 預設會有並行建置的次數限制。此外，如果您的 `cloudbuild.yaml` 設定了錯誤的執行器，也可能導致超時。

### Q2：如何在建置過程中執行單元測試？

**答：** 在 `build` 步驟之前，增加一個步驟執行測試。如果測試失敗，Cloud Build 會立即停止，不會進行後續的部署，這就是 CI/CD 的保護機制。

```yaml
- name: "python:3.11"
  entrypoint: "bash"
  args: ["-c", "pip install -r requirements.txt && pytest"]
```

## 延伸閱讀

- [Cloud Build 的 IAM 權限設定](https://cloud.google.com/build/docs/securing-builds/configure-access-for-cloud-build-service-account)
- [如何管理建置觸發條件](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)
