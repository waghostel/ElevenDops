# ElevenDops 資料儲存架構

## 概述

本文件說明 ElevenDops 系統中病患對話、逐字稿和音檔的儲存策略。系統採用混合儲存方案：Firestore 儲存結構化資料（逐字稿、文本內容），Google Cloud Storage (GCS) 儲存二進位檔案（音檔）。

---

## 病患對話資訊產生流程

### 1. 對話開始
- 病患在 Streamlit 前端輸入文字問題
- 系統建立一個 `patient_session`（患者會話）

### 2. 對話進行
- 後端透過 ElevenLabs Conversational AI API 處理病患的問題
- 系統生成 AI 回應
- 使用 TTS（Text-to-Speech）生成音頻回應

### 3. 訊息累積
每條訊息會記錄：
```json
{
    "role": "patient" 或 "agent",
    "content": "訊息內容",
    "timestamp": "時間戳記",
    "is_answered": true/false
}
```

### 4. 對話結束時儲存
當對話結束，系統會自動分析並儲存到 `/conversations/{conversation_id}` 集合：

```json
{
    "conversation_id": "唯一識別碼",
    "patient_id": "病患 ID",
    "agent_id": "AI 助手 ID",
    "agent_name": "助手名稱",
    "requires_attention": "是否需要醫生關注（自動判斷）",
    "main_concerns": ["主要關切事項"],
    "messages": [
        {
            "role": "patient",
            "content": "完整逐字稿",
            "timestamp": "時間戳記",
            "is_answered": true
        }
    ],
    "answered_questions": ["已回答的問題清單"],
    "unanswered_questions": ["未回答的問題清單"],
    "duration_seconds": "對話時長",
    "created_at": "建立時間"
}
```

### 5. 自動分析
系統會自動：
- 識別病患提出的問題
- 判斷 AI 是否有回答
- 分類為「已回答」或「未回答」
- 提取主要關切事項
- 判斷是否需要醫生關注（`requires_attention`）

### 6. 醫生審查
醫生可以在「Conversation Logs」頁面查看：
- 所有對話記錄
- 篩選未回答的問題
- 標記需要關注的對話
- 查看完整對話詳情

---

## Firestore 儲存策略

### ✅ 會完整儲存的資訊

#### 1. 對話逐字稿（完整儲存）

在 `/conversations/{conversation_id}` 中的 `messages` 陣列：

```json
"messages": [
    {
        "role": "patient",
        "content": "手術後多久可以洗臉？",
        "timestamp": "Timestamp",
        "is_answered": true
    },
    {
        "role": "agent",
        "content": "一般建議術後一週...",
        "timestamp": "Timestamp",
        "is_answered": null
    }
]
```

**特點**：
- 完整保存病患的每個問題
- 完整保存 AI 的每個回應
- 包含時間戳記和回答狀態

#### 2. 教育音檔的逐字稿（完整儲存）

在 `/audio_files/{audio_id}` 中：

```json
{
    "audio_id": "uuid-string",
    "knowledge_id": "uuid-string",
    "voice_id": "voice_xxx",
    "script": "衛教講稿內容...",
    "audio_url": "http://localhost:4443/storage/v1/b/...",
    "duration_seconds": 120.5,
    "created_at": "Timestamp"
}
```

**特點**：
- 完整保存醫生上傳的逐字稿
- 儲存音檔的 URL 參考
- 記錄音檔時長

#### 3. 知識文件內容（完整儲存）

在 `/knowledge_documents/{doc_id}` 中：

```json
{
    "knowledge_id": "uuid-string",
    "doctor_id": "default_doctor",
    "disease_name": "白內障",
    "document_type": "faq",
    "raw_content": "# 白內障常見問題...",
    "sync_status": "pending",
    "elevenlabs_document_id": null,
    "structured_sections": {
        "Introduction": "...",
        "FAQ": "..."
    },
    "created_at": "Timestamp"
}
```

**特點**：
- 完整保存原始文件內容
- 保存結構化的章節資訊
- 追蹤與 ElevenLabs 的同步狀態

### ❌ 不會儲存在 Firestore 的

#### 音檔二進位資料
- 音檔二進位資料 **不儲存在 Firestore**
- 只儲存 `audio_url` 指向 GCS 中的實際音檔
- **原因**：Firestore 不適合儲存大型二進位檔案，會增加成本和降低效能

---

## 儲存架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    ElevenDops 儲存架構                       │
└─────────────────────────────────────────────────────────────┘

Firestore (結構化資料)
├── /conversations/{id}
│   ├── messages: [
│   │   {
│   │       role: "patient",
│   │       content: "完整逐字稿",
│   │       timestamp: Timestamp,
│   │       is_answered: boolean
│   │   }
│   │]
│   ├── answered_questions: [...]
│   ├── unanswered_questions: [...]
│   └── requires_attention: boolean
│
├── /audio_files/{id}
│   ├── script: "完整逐字稿"
│   ├── audio_url: "指向 GCS 的 URL"
│   └── duration_seconds: number
│
├── /knowledge_documents/{id}
│   ├── raw_content: "完整文件內容"
│   ├── structured_sections: {...}
│   └── sync_status: string
│
└── /agents/{id}
    ├── name: string
    ├── knowledge_ids: [...]
    └── elevenlabs_agent_id: string

Google Cloud Storage (二進位檔案)
└── audio/
    ├── education_audio_001.mp3
    ├── education_audio_002.mp3
    ├── conversation_response_001.mp3
    ├── conversation_response_002.mp3
    └── ...
```

---

## 具體使用場景

### 場景 1：病患對話

```
病患問題: "手術後多久可以洗臉？"
    ↓
Firestore 儲存:
  /conversations/conv_123
    messages[0]: {
      role: "patient",
      content: "手術後多久可以洗臉？"  ✅ 完整逐字稿
    }
    
AI 回應: "一般建議術後一週..."
    ↓
Firestore 儲存:
  /conversations/conv_123
    messages[1]: {
      role: "agent",
      content: "一般建議術後一週..."  ✅ 完整逐字稿
    }

TTS 生成音檔
    ↓
GCS 儲存: audio/response_001.mp3  ✅ 音檔本身
Firestore 儲存: 
  /audio_files/audio_001
    audio_url: "https://storage.googleapis.com/bucket/audio/response_001.mp3"
```

### 場景 2：教育音檔

```
醫生上傳逐字稿: "白內障是..."
    ↓
Firestore 儲存:
  /audio_files/audio_456
    script: "白內障是..."  ✅ 完整逐字稿

ElevenLabs TTS 生成音檔
    ↓
GCS 儲存: audio/education_001.mp3  ✅ 音檔本身
Firestore 儲存: 
  /audio_files/audio_456
    audio_url: "https://storage.googleapis.com/bucket/audio/education_001.mp3"
```

### 場景 3：醫生查看對話記錄

```
醫生訪問 Conversation Logs 頁面
    ↓
後端查詢 Firestore:
  /conversations
    ├── 篩選 requires_attention = true
    ├── 篩選日期範圍
    └── 排序 created_at 降序
    ↓
返回對話摘要:
  {
    conversation_id: "conv_123",
    patient_id: "patient_001",
    agent_name: "白內障衛教助理",
    main_concerns: ["術後照護", "用藥問題"],
    requires_attention: true,
    created_at: "2024-12-19T10:30:00Z"
  }
    ↓
醫生點擊查看詳情
    ↓
後端查詢 Firestore:
  /conversations/conv_123
    ↓
返回完整對話:
  {
    messages: [
      {role: "patient", content: "手術後多久可以洗臉？"},
      {role: "agent", content: "一般建議術後一週..."}
    ],
    answered_questions: ["手術後多久可以洗臉？"],
    unanswered_questions: ["可以開車嗎？"]
  }
```

---

## 儲存位置總結表

| 項目 | 儲存位置 | 完整儲存 | 說明 |
|------|--------|--------|------|
| 對話逐字稿 | Firestore | ✅ 是 | `/conversations/{id}/messages` |
| 教育音檔逐字稿 | Firestore | ✅ 是 | `/audio_files/{id}/script` |
| 知識文件內容 | Firestore | ✅ 是 | `/knowledge_documents/{id}/raw_content` |
| 音檔二進位資料 | GCS | ✅ 是 | `audio/` 資料夾 |
| 音檔 URL 參考 | Firestore | ✅ 是 | `/audio_files/{id}/audio_url` |
| 對話分析結果 | Firestore | ✅ 是 | `/conversations/{id}/answered_questions` 等 |

---

## 設計原則

1. **文本資料在 Firestore**：所有結構化文字資料（逐字稿、內容、分析結果）儲存在 Firestore，便於查詢和分析

2. **二進位檔案在 GCS**：音檔等大型二進位檔案儲存在 GCS，降低成本和提高效能

3. **URL 參考連結**：Firestore 中只保存指向 GCS 的 URL 參考，實現鬆散耦合

4. **完整審計追蹤**：所有對話和內容都完整保存，便於醫生審查和系統分析

5. **隱私和安全**：敏感的對話內容完整保存在 Firestore，可以設定適當的存取控制

---

## 實施時程

根據 Phase 2 Implementation Roadmap，這些功能在 MVP1 中實施：

- **Spec 2**（2 天）：Firestore Data Service - 實現資料持久化
- **Spec 3**（1 天）：Storage Service - 實現 GCS 整合
- **Spec 7**（3 天）：Patient Conversation - 實現對話功能
- **Spec 8**（1 天）：Conversation Logs Integration - 實現對話查詢

---

## 相關文件

- [Phase 2 Implementation Roadmap](../user-need/phase2-IMPLEMENTATION_ROADMAP.md)
- [Firestore Data Service Specification](.kiro/specs/firestore-data-service/design.md)
- [Storage Service Specification](.kiro/specs/storage-service/design.md)
