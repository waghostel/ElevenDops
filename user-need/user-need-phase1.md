
# ElevenDops 系統需求規格書 - Phase 1

## 0. 使用者需求概述

### 0.1 系統目標
建構一個結合 ElevenLabs 語音技術的智能醫療助理系統，旨在解決醫生與病患之間的衛教溝通問題，提升醫療服務效率與品質。

### 0.2 核心問題定義
- 醫生需要重複向不同病患解說相同的基礎醫療資訊
- 病患對於疾病相關資訊存在疑問，但缺乏即時諮詢管道
- 醫生無法有效掌握病患的疑問重點，影響看診效率

### 0.3 主要功能需求

#### 0.3.1 衛教音檔錄製功能
**需求描述：** 系統應提供針對特定疾病的基礎衛教音檔錄製與管理功能。

**使用情境：** 醫生可以為常見疾病（如白內障手術術後照護）錄製標準化衛教說明，病患可直接點選收聽相關音檔，獲得基礎醫療資訊。

**預期效益：** 減少醫生重複解說時間，提供病患24小時可存取的衛教資源。

#### 0.3.2 語音對話諮詢功能
**需求描述：** 系統應具備語音對話能力，能夠回答病患的基礎醫學問題。

**使用情境：** 病患可透過語音與系統互動，詢問疾病相關的基礎問題，系統基於醫療知識庫提供適當回應。

**預期效益：** 協助病患釐清基礎醫學資訊，減少醫生處理重複性問題的時間負擔。

#### 0.3.3 問題收集與分析功能
**需求描述：** 系統應收集並分析病患提出但無法回答的問題，提供醫生參考。

**使用情境：** 當病患詢問超出系統知識範圍的問題時，系統應記錄該問題。醫生在看診前可查看病患曾提出的問題清單，了解需要額外說明的重點。

**預期效益：** 提升看診效率，確保醫生能針對病患真正關心的問題進行深入說明。

### 0.4 目標使用者
- **主要使用者：** 醫療機構的執業醫師
- **次要使用者：** 接受醫療服務的病患
- **系統管理者：** 醫療機構的資訊技術人員

### 0.5 成功指標
- 減少醫生重複解說基礎資訊的時間比例
- 提升病患對疾病認知的滿意度
- 增加醫生對病患疑問的掌握程度
- 系統使用率與使用者接受度

---

## 1. 技術架構

### 1.1 核心技術組件
- **Cloud Run**: 容器化部署平台
- **Firestore**: 主要資料庫，作為系統資料來源
- **ElevenLabs Knowledge Base**: 知識庫同步副本
- **Streamlit**: 醫生端與病患端最小可行產品(MVP)使用者介面
- **Backend API**: 後端應用程式介面，支援未來 Next.js/TypeScript 整合

### 1.2 系統架構原則

#### 1.2.1 責任分離
系統採用分層架構設計，明確區分前端展示層與後端邏輯層的職責範圍。

#### 1.2.2 Streamlit 職責範圍

**負責功能:**
- 醫生操作流程使用者介面
- 病患測試使用者介面  
- 後端API呼叫
- 結果展示（音檔、Agent ID、對話記錄）

**不負責功能:**
- 直接操作 ElevenLabs API
- 直接執行 Firestore CRUD 操作
- 直接處理 LLM 提示詞
- 商業邏輯判斷與處理

#### 1.2.3 架構設計考量
即使在 Phase 1 階段將 API 功能與 Streamlit 置於同一程式庫中，程式結構仍須保持模組化分離設計，以利後續系統擴展。

---

## 2. 系統架構設計

### 2.1 應用程式結構
系統採用單一 Streamlit 應用程式架構，透過側邊欄進行角色切換，支援醫生端與病患端功能。

### 2.2 目錄結構規劃

```
📦 streamlit_app/
 ├─ app.py                          # 主應用程式入口
 ├─ pages/                          # 頁面模組
 │   ├─ 1_Doctor_Dashboard.py       # 醫生儀表板
 │   ├─ 2_Upload_Knowledge.py       # 知識上傳功能
 │   ├─ 3_Education_Audio.py        # 衛教音檔管理
 │   ├─ 4_Agent_Setup.py            # 智能代理設定
 │   ├─ 5_Patient_Test.py           # 病患測試介面
 │   └─ 6_Conversation_Logs.py      # 對話記錄查詢
 └─ services/                       # 服務層
     ├─ backend_api.py              # 後端API服務（支援未來Next.js整合）
     ├─ elevenlabs.py               # ElevenLabs整合服務
     └─ firestore.py                # Firestore資料庫服務
```

---

## 3. 醫生端功能需求

### 3.1 醫生儀表板 (Doctor Dashboard)

#### 3.1.1 功能目標
提供醫生系統狀態總覽，實現快速狀態監控與管理。

#### 3.1.2 顯示內容需求
- 已上傳衛教文件統計
- 已建立智能代理數量
- 已產生衛教音檔統計
- 最近病患測試活動時間

#### 3.1.3 技術實作要求
- 資料來源：Firestore 資料庫摘要資訊
- 避免直接呼叫 ElevenLabs API
- 實作即時資料更新機制

---

### 3.2 知識上傳功能 (Upload Knowledge)

#### 3.2.1 使用者操作流程
1. 上傳 Markdown 或 TXT 格式文件
2. 填寫文件基本資訊：
   - 疾病名稱
   - 文件類型（常見問題/術後照護/注意事項）
3. 執行「儲存並同步」操作

#### 3.2.2 後端處理流程

**Firestore 資料儲存：**
- knowledge_id：知識文件唯一識別碼
- doctor_id：醫生識別碼
- raw_markdown：原始文件內容
- structured_sections：結構化章節資料
- created_at：建立時間戳記

**ElevenLabs Knowledge Base 同步：**
- document_id：文件識別碼
- agent_id：智能代理識別碼

#### 3.2.3 資料架構設計原則
- Firestore 作為主要資料來源
- ElevenLabs Knowledge Base 僅儲存參考資料
- Firestore 維護 elevenlabs_document_id 對應關係

---

### 3.3 衛教音檔製作功能 (Education Audio)

#### 3.3.1 使用者操作流程
1. 選擇已上傳的衛教資料
2. 執行「產生衛教講稿預覽」功能
3. 編輯並確認講稿內容
4. 執行「產生語音」功能

#### 3.3.2 後端處理流程
```
Firestore 知識資料 →
LLM 講稿生成 →
醫生確認審核 →
ElevenLabs TTS 轉換 →
GCS Storage 儲存 →
Firestore 音檔元資料更新
```

#### 3.3.3 使用者介面顯示需求
- 講稿預覽文字區域
- 音檔播放控制元件
- 音檔 URL 顯示

#### 3.3.4 醫療合規要求
系統必須實作醫生確認機制，確保所有衛教內容經過專業醫療人員審核後方可發布，以符合醫療資訊合規標準。

---

### 3.4 智能代理設定功能 (Agent Setup)

#### 3.4.1 可設定項目 (MVP階段)
- 智能代理名稱
- 關聯知識庫（支援多選）
- 語音模型選擇
- 回答風格設定選項：
  - 穩定專業型
  - 親切友善型
  - 衛教導向型

#### 3.4.2 後端功能實作

**create_or_update_agent() 函式需求：**
- system_prompt：系統提示詞設定
- knowledge_base_document_ids：知識庫文件識別碼清單
- voice_id：語音模型識別碼
- data_collection_schema：資料收集架構定義

#### 3.4.3 Firestore 資料儲存需求
- agent_id：智能代理唯一識別碼
- linked_knowledge_ids：關聯知識文件識別碼清單
- voice_id：語音模型識別碼
- created_at：建立時間戳記

---

## 4. 病患端功能需求

### 4.1 功能定位
病患端介面作為系統驗證與體驗測試平台，非正式產品使用者介面。

### 4.2 病患測試頁面 (Patient Test Page)

#### 4.2.1 使用者功能需求
- 病患識別碼輸入
- 疾病類型/智能代理選擇
- 衛教音檔播放功能
- 智能代理語音對話功能

#### 4.2.2 技術實作規範

**Phase 1 階段技術限制：**
- 支援簡化語音串流處理
- 支援文字輸入搭配語音輸出模式

**對話結束後處理流程：**
- 呼叫 ElevenLabs webhook 處理器
- 對話資料儲存至 Firestore 資料庫

---

### 4.3 對話記錄查詢功能 (Conversation Logs)

#### 4.3.1 顯示內容需求
- 病患識別碼
- 提問記錄（已回答/未回答狀態）
- 智能代理回答摘要
- 醫生介入需求標記

#### 4.3.2 功能重要性
此功能為系統價值展示的核心模組，提供醫療服務品質監控與改善依據。

---

## 5. 部署架構與技術規範

### 5.1 Cloud Run 容器架構 (Phase 1)

```
Cloud Run Service
 ├─ Streamlit Application        # 前端應用程式
 ├─ Backend API (FastAPI)        # 後端API服務
 ├─ Firestore Client            # 資料庫客戶端
 └─ ElevenLabs Client           # ElevenLabs整合客戶端
```

### 5.2 API 介面設計規範

為確保未來系統擴展性，API 介面設計須遵循 RESTful 原則：

```
POST /api/knowledge              # 知識資料管理
POST /api/audio                  # 音檔處理
POST /api/agent                  # 智能代理管理
POST /api/patient/session        # 病患會話管理
GET  /api/patient/{id}/summary   # 病患資料摘要查詢
```

此設計確保未來 Next.js 前端框架可無縫整合現有 API 服務。

---

## 6. ElevenLabs API 整合實作規劃

### 6.1 API 整合架構概述

基於 ElevenLabs 平台的四大核心組件，本系統將整合以下技術模組：

1. **Knowledge Base API** - 醫療知識庫管理
2. **Agents API** - 智能醫療助理建立與配置
3. **Text-to-Speech API** - 衛教音檔生成
4. **Conversational AI WebSocket** - 即時語音對話

### 6.2 知識庫管理實作 (Knowledge Base Integration)

#### 6.2.1 API 端點與功能對應

**醫生上傳衛教資料流程：**
```python
# 1. 建立知識庫文件 (對應 Upload Knowledge 功能)
knowledge_base_document = client.conversational_ai.knowledge_base.documents.create_from_text(
    text=markdown_content,  # 來自 Firestore 的 raw_markdown
    name=f"{disease_name}_{document_type}",  # 疾病名稱_文件類型
)

# 2. 儲存文件 ID 至 Firestore
firestore_data = {
    "knowledge_id": knowledge_id,
    "elevenlabs_document_id": knowledge_base_document.id,
    "doctor_id": doctor_id,
    "disease_name": disease_name,
    "document_type": document_type,
    "sync_status": "completed"
}
```

#### 6.2.2 知識庫同步策略

**資料流向設計：**
- **主要資料源**: Firestore (raw_markdown, structured_sections)
- **ElevenLabs 副本**: 僅儲存 Agent 查詢所需的處理後內容
- **同步觸發**: 醫生執行「儲存並同步」操作時

**錯誤處理機制：**
- 同步失敗時保留 Firestore 原始資料
- 實作重試機制與狀態追蹤
- 提供手動重新同步功能

### 6.3 智能代理建立與配置 (Agents API Integration)

#### 6.3.1 Agent 建立流程實作

**create_or_update_agent() 函式實作：**
```python
def create_or_update_agent(agent_config):
    # 1. 準備系統提示詞 (基於回答風格設定)
    system_prompts = {
        "professional": "你是一位專業的醫療助理，請以準確、客觀的方式回答病患問題...",
        "friendly": "你是一位親切的醫療助理，請以溫暖、易懂的方式協助病患...",
        "educational": "你是一位衛教專員，請重點提供教育性的醫療資訊..."
    }
    
    # 2. 建立或更新 Agent
    agent = client.conversational_ai.agents.create_or_update(
        agent_id=agent_config.get("agent_id"),
        conversation_config={
            "agent": {
                "prompt": {
                    "system": system_prompts[agent_config["answer_style"]],
                    "knowledge_base": [
                        {
                            "type": "text",
                            "id": doc_id,
                            "name": doc_name
                        } for doc_id, doc_name in agent_config["knowledge_documents"]
                    ]
                }
            }
        },
        voice_id=agent_config["voice_id"]
    )
    
    return agent
```

#### 6.3.2 資料收集架構設定

**醫療資訊擷取配置：**
```python
data_collection_schema = [
    {
        "identifier": "patient_main_concern",
        "data_type": "string",
        "description": "病患主要關心的問題或症狀"
    },
    {
        "identifier": "question_category",
        "data_type": "string", 
        "description": "問題分類：術後照護/藥物相關/症狀詢問/其他"
    },
    {
        "identifier": "requires_doctor_attention",
        "data_type": "boolean",
        "description": "是否需要醫生進一步關注"
    },
    {
        "identifier": "patient_satisfaction",
        "data_type": "integer",
        "description": "病患對回答的滿意度 (1-5分)"
    }
]
```

### 6.4 衛教音檔生成實作 (Text-to-Speech Integration)

#### 6.4.1 TTS API 整合流程

**衛教音檔製作流程：**
```python
def generate_education_audio(script_content, voice_id, disease_name):
    # 1. 使用 TTS API 生成音檔
    audio_response = client.text_to_speech.convert(
        voice_id=voice_id,
        output_format="mp3_44100_128",  # 高品質音檔格式
        text=script_content,
        model_id="eleven_multilingual_v2",  # 支援中文
        text_normalization="auto"  # 自動文字正規化
    )
    
    # 2. 上傳至 GCS Storage
    audio_url = upload_to_gcs(audio_response, f"education_audio/{disease_name}")
    
    # 3. 更新 Firestore 元資料
    audio_metadata = {
        "audio_url": audio_url,
        "voice_id": voice_id,
        "script_content": script_content,
        "duration_seconds": calculate_duration(audio_response),
        "created_at": datetime.now()
    }
    
    return audio_metadata
```

#### 6.4.2 串流音檔支援 (未來擴展)

**即時音檔生成 (Phase 2 考量)：**
```python
# 支援長篇衛教內容的串流生成
def stream_education_audio(script_content, voice_id):
    return client.text_to_speech.stream(
        voice_id=voice_id,
        output_format="mp3_44100_128",
        text=script_content,
        model_id="eleven_multilingual_v2",
        optimize_streaming_latency=2  # 強化延遲優化
    )
```

### 6.5 即時語音對話實作 (Conversational AI WebSocket)

#### 6.5.1 WebSocket 連線管理

**病患對話連線流程：**
```python
# 1. 取得簽名 URL (安全性考量)
def get_signed_conversation_url(agent_id, patient_id):
    response = requests.get(
        f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
        params={"agent_id": agent_id},
        headers={"xi-api-key": api_key}
    )
    return response.json()["signed_url"]

# 2. 建立 WebSocket 連線
async def start_patient_conversation(agent_id, patient_id):
    signed_url = get_signed_conversation_url(agent_id, patient_id)
    
    # 使用簽名 URL 建立安全連線
    websocket = await websockets.connect(signed_url)
    
    # 發送病患上下文資訊
    context_update = {
        "type": "contextual_update",
        "text": f"病患ID: {patient_id}, 開始諮詢會話"
    }
    await websocket.send(json.dumps(context_update))
    
    return websocket
```

#### 6.5.2 對話事件處理

**即時對話管理：**
```python
async def handle_conversation_events(websocket, patient_id):
    async for message in websocket:
        event = json.loads(message)
        
        if event["type"] == "agent_response":
            # 儲存 Agent 回應至 Firestore
            save_conversation_turn(
                patient_id=patient_id,
                role="agent", 
                message=event["message"],
                timestamp=event["time_in_call_secs"]
            )
            
        elif event["type"] == "user_transcript":
            # 儲存病患問題至 Firestore
            save_conversation_turn(
                patient_id=patient_id,
                role="user",
                message=event["message"], 
                timestamp=event["time_in_call_secs"]
            )
```

### 6.6 對話資料收集與分析 (Data Collection Integration)

#### 6.6.1 對話結束後處理

**Webhook 事件處理：**
```python
def process_conversation_webhook(conversation_data):
    conversation_id = conversation_data["conversation_id"]
    
    # 1. 取得完整對話記錄
    conversation_details = client.conversational_ai.conversations.get(
        conversation_id=conversation_id
    )
    
    # 2. 擷取結構化資料
    extracted_data = conversation_details.get("analysis", {})
    
    # 3. 儲存至 Firestore 供醫生查詢
    conversation_summary = {
        "patient_id": extract_patient_id(conversation_data),
        "agent_id": conversation_data["agent_id"],
        "transcript": conversation_details["transcript"],
        "extracted_data": extracted_data,
        "requires_doctor_attention": extracted_data.get("requires_doctor_attention", False),
        "main_concerns": extracted_data.get("patient_main_concern", ""),
        "conversation_duration": conversation_details["metadata"]["call_duration_secs"],
        "created_at": datetime.now()
    }
    
    return save_conversation_summary(conversation_summary)
```

#### 6.6.2 醫生端資料查詢

**對話記錄查詢 API：**
```python
def get_patient_conversation_summary(patient_id, doctor_id):
    # 從 Firestore 查詢病患對話記錄
    conversations = firestore_client.collection("conversations")\
        .where("patient_id", "==", patient_id)\
        .where("doctor_id", "==", doctor_id)\
        .order_by("created_at", direction="DESCENDING")\
        .get()
    
    summary = {
        "answered_questions": [],
        "unanswered_questions": [],
        "requires_attention": [],
        "satisfaction_scores": []
    }
    
    for conv in conversations:
        data = conv.to_dict()
        if data.get("requires_doctor_attention"):
            summary["requires_attention"].append(data)
        # 其他分類邏輯...
    
    return summary
```

### 6.7 認證與安全性實作 (Authentication Integration)

#### 6.7.1 API 金鑰管理

**環境變數配置：**
```python
import os
from elevenlabs import ElevenLabs

# 安全的 API 金鑰管理
client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    base_url="https://api.elevenlabs.io"
)
```

#### 6.7.2 簽名 URL 安全機制

**病患端存取控制：**
- 使用簽名 URL 避免暴露 API 金鑰
- 15分鐘自動過期機制
- 病患 ID 與會話綁定驗證

### 6.8 錯誤處理與監控

#### 6.8.1 API 呼叫錯誤處理

**重試機制與降級策略：**
```python
import backoff
from elevenlabs.exceptions import ElevenLabsError

@backoff.on_exception(backoff.expo, ElevenLabsError, max_tries=3)
def robust_api_call(api_function, *args, **kwargs):
    try:
        return api_function(*args, **kwargs)
    except ElevenLabsError as e:
        # 記錄錯誤並實作降級策略
        log_api_error(e)
        if "quota_exceeded" in str(e):
            return handle_quota_exceeded()
        raise
```

#### 6.8.2 使用量監控

**API 使用量追蹤：**
- 整合 Usage Analytics API 監控系統使用狀況
- 實作用量警告機制
- 成本控制與預算管理

### 6.9 Phase 1 實作優先順序

#### 6.9.1 核心功能實作順序
1. **Knowledge Base API** - 醫療知識上傳與同步
2. **Agents API** - 基礎智能代理建立
3. **TTS API** - 衛教音檔生成
4. **WebSocket API** - 簡化版語音對話 (文字輸入/語音輸出)
5. **Data Collection** - 對話記錄與分析

#### 6.9.2 技術債務管理
- 預留完整 WebSocket 語音串流實作空間
- 保持 API 介面設計的擴展性
- 確保所有 ElevenLabs 整合模組可獨立測試與部署

---

## 7. Phase 1 設計原則總結

### 7.1 核心設計原則
- **Firestore**: 系統主要資料庫
- **ElevenLabs Knowledge Base**: 智能代理專用資料副本
- **Streamlit**: 使用者介面層，不包含業務邏輯
- **Backend API**: 核心產品邏輯層
- **架構擴展性**: 所有模組設計支援未來 React/Next.js 框架整合

### 7.2 ElevenLabs 整合策略
- **API 封裝**: 所有 ElevenLabs API 呼叫封裝於 services/elevenlabs.py
- **錯誤處理**: 實作完整的重試機制與降級策略  
- **安全性**: 使用簽名 URL 與環境變數管理敏感資訊
- **監控**: 整合使用量追蹤與成本控制機制

### 7.3 系統發展策略
Phase 1 階段採用 MVP 開發模式，確保核心功能完整性的同時，為後續系統擴展預留充分的技術彈性與整合能力。透過完整的 ElevenLabs API 整合，系統將具備企業級的語音 AI 能力，為醫療衛教服務提供創新的解決方案。

