# Error Reporting 與警報

## 關鍵字

- **Error Reporting**：自動偵測與分組應用程式錯誤。
- **Alerting Policy**：觸發通知的條件規則。
- **Notification Channel**：警報發送的目的地（Email, Slack, PagerDuty）。

## 學習目標

完成本章節後，您將能夠：

1. 啟用與查看 Error Reporting
2. 建立警報策略
3. 設定通知管道

## 步驟說明

### 步驟 1：理解 Error Reporting

#### 我們在做什麼？

Error Reporting 會自動掃描日誌中的 Exception，分組相同錯誤，追蹤發生頻率。

#### 為什麼需要這樣做？

- 自動偵測：不需手動設定規則
- 智慧分組：相同錯誤只顯示一次，顯示發生次數
- 時間軸：追蹤錯誤何時開始、何時解決

#### 支援的格式

Error Reporting 會自動辨識以下格式：

```python
# 自動辨識 Python Traceback
import logging

try:
    1 / 0
except Exception as e:
    logging.exception("發生錯誤")  # 會記錄完整 Traceback
```

### 步驟 2：查看 Error Reporting 儀表板

#### 我們在做什麼？

在 GCP Console 查看錯誤清單與詳細資訊。

#### 導航路徑

1. 打開 GCP Console
2. 搜尋 "Error Reporting"
3. 選擇你的專案
4. 查看錯誤列表

#### 儀表板資訊

```mermaid
graph TD
    A[Error Reporting Dashboard]
    A --> B[錯誤列表]
    A --> C[單一錯誤詳情]

    B --> B1[錯誤訊息]
    B --> B2[發生次數]
    B --> B3[受影響使用者]
    B --> B4[首次/最後發生時間]

    C --> C1[完整 Stack Trace]
    C --> C2[時間軸圖表]
    C --> C3[相關日誌連結]
```

### 步驟 3：建立警報策略

#### 我們在做什麼？

設定條件，當錯誤發生時自動發送通知。

#### 使用 Monitoring API 建立

```bash
# 建立警報策略 (使用 gcloud)
gcloud alpha monitoring policies create \
    --display-name="High Error Rate Alert" \
    --condition-display-name="Error count > 10 in 5 min" \
    --condition-filter="resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/log_entry_count\" AND metric.labels.severity=\"ERROR\"" \
    --condition-threshold-value=10 \
    --condition-threshold-duration=300s \
    --notification-channels=projects/my-project/notificationChannels/123456
```

#### 使用 Console (建議初學者)

1. 前往 Monitoring > Alerting
2. 點擊 "Create Policy"
3. 設定條件：
   - Resource: Cloud Run Revision
   - Metric: logging/log_entry_count
   - Filter: severity="ERROR"
   - Threshold: > 10
4. 選擇通知管道
5. 儲存

### 步驟 4：設定通知管道

#### 我們在做什麼？

設定警報要發送到哪裡。

#### 支援的管道

| 管道          | 適用情境     |
| ------------- | ------------ |
| **Email**     | 一般通知     |
| **Slack**     | 團隊即時通知 |
| **PagerDuty** | On-call 輪值 |
| **Webhook**   | 自訂整合     |

#### 設定 Slack 通知

```bash
# 1. 先在 Slack 建立 Incoming Webhook

# 2. 在 GCP 建立通知管道
gcloud alpha monitoring channels create \
    --display-name="Slack - Dev Team" \
    --type=slack \
    --channel-labels=channel_name="#alerts" \
    --channel-labels=auth_token="xoxb-your-slack-token"
```

#### 流程圖

```mermaid
sequenceDiagram
    participant App as 應用程式
    participant CL as Cloud Logging
    participant ER as Error Reporting
    participant M as Monitoring
    participant S as Slack

    App->>CL: 記錄 Exception
    CL->>ER: 轉發錯誤日誌
    ER->>M: 觸發警報條件
    M->>S: 發送通知
```

## 常見問題 Q&A

### Q1：Error Reporting 需要額外費用嗎？

**答：** Error Reporting 本身免費，但底層使用的 Cloud Logging 儲存會計費。

### Q2：如何避免警報疲勞？

**答：**

- 設定合理的閾值
- 使用通知靜音 (Snooze) 功能
- 針對不同嚴重程度設定不同管道

## 重點整理

| 概念                     | 說明         | 設定方式           |
| ------------------------ | ------------ | ------------------ |
| **Error Reporting**      | 自動偵測錯誤 | 自動啟用           |
| **Alerting Policy**      | 警報觸發條件 | Monitoring Console |
| **Notification Channel** | 通知目的地   | 預先設定           |

---

## 參考程式碼來源

| 檔案路徑          | 說明                   |
| ----------------- | ---------------------- |
| `backend/main.py` | Exception Handler 設定 |

---

[⬅️ 返回 GCP Monitoring & Logging 索引](./index.md)
