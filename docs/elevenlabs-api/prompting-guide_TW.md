# Prompting 指南 - ElevenLabs Agents 平台

針對生產級對話式 AI 的系統設計原則

## 簡介

有效的 Prompt 能讓 ElevenLabs Agents 從機械化變得栩栩如生。

系統 Prompt 是 AI agent 的個性與策略藍圖。在企業級應用中，它通常非常詳盡——定義 agent 的角色、目標、可用的工具、特定任務的分步指令，以及描述 agent 不應執行的操作的護欄（guardrails）。你結構化此 Prompt 的方式將直接影響其可靠性。

系統 Prompt 控制對話行為和回應風格，但不會控制對話流機制（如輪流發言）或 agent 設定（如 agent 可以說哪些語言）。這些方面由平台層級處理。

## Prompt 工程基礎

系統 Prompt 是 AI agent 的個性與策略藍圖。在企業級應用中，它通常非常詳盡——定義 agent 的角色、目標、可用的工具、對特定任務的分步指令，以及描述 agent 不應執行的操作的護欄。你結構化此 Prompt 的方式將直接影響其可靠性。

以下原則構成了生產級 Prompt 工程的基礎：

### 將指令劃分為清晰的區塊

將指令劃分為專用區塊並帶有 Markdown 標題，有助於模型正確排定優先順序並進行解讀。使用空格和換行符號來分隔指令。

**為什麼這對可靠性很重要：** 模型經過微調，會特別注意某些標題（尤其是 `# Guardrails`），清晰的區塊邊界可以防止「指令滲透」（instruction bleed），即一個情境下的規則影響到另一個情境。

### 盡可能簡潔

保持每條指令短小、清晰且以行動為導向。刪除贅字，僅保留模型正確執行所需的精簡內容。

**為什麼這對可靠性很重要：** 簡潔的指令可以減少歧義和 token 使用量。每個字詞都可能是誤解的來源。

### 強調關鍵指令

在行末添加「This step is important」來強調關鍵步驟。在 Prompt 中重複最重要的 1-2 條指令兩次可以幫助強化它們。

**為什麼這對可靠性很重要：** 在複雜的 Prompt 中，模型可能會優先考慮最近的情景而忽略早期的指令。強調和重複可確保關鍵規則不被忽視。

### 規範化輸入與輸出

語音 agent 經常會誤解或錯誤格式化結構化資訊，例如電子郵件、ID 或記錄定位器。為了確保準確性，請將與用戶對讀時所說的資料格式與在工具或 API 中使用的寫入格式分開（或稱為「規範化」）。

**為什麼這對可靠性很重要：** 文字轉語音模型有時會自然地誤讀 `@` 或 `.` 等符號。將其規範化為語音格式（例如 "john at company dot com"）可以產生自然且易於理解的語音，同時為工具保留正確的寫入格式。

### 提供清晰的範例

在 Prompt 中包含範例，以說明 agent 應如何表現、使用工具或格式化數據。大型語言模型在有具體範例可供參考時，能更可靠地遵循指令。

**為什麼這對可靠性很重要：** 範例可以減少歧義並提供參考模式。對於複雜的格式、多步驟流程和邊緣情況特別有價值。

### 設立專門的護欄 (Guardrails) 區塊

在專用的 `# Guardrails` 區塊中列出模型必須始終遵守的所有不可逾越的規則。模型經過微調，會特別注意這個標題。

**為什麼這對可靠性很重要：** 護欄可防止不當回應並確保符合政策。將它們集中在專用區塊中使其更易於稽核和更新。

Example guardrails section:

```
# Guardrails

Never share customer data across conversations or reveal sensitive account information without proper verification.
Never process refunds over $500 without supervisor approval.
Never make promises about delivery dates that aren't confirmed in the order system.
Acknowledge when you don't know an answer instead of guessing.
If a customer becomes abusive, politely end the conversation and offer to escalate to a supervisor.
```

## 提升可靠性的工具配置

能夠處理交易流程的 agent 可以非常高效。為了實現這一點，它們必須配備工具，以便在其他系統中執行操作或從中獲取即時數據。

與 Prompt 結構同樣重要的，是你如何描述 agent 可用的工具。清晰、以行動為導向的工具定義有助於模型正確調用它們，並從錯誤中優雅地恢復。

### 使用詳細參數精確描述工具

創建工具時，為所有參數添加說明。這有助於 LLM 準確地構建工具調用。

**工具描述 (Tool description):** "Looks up customer order status by order ID and returns current status, estimated delivery date, and tracking number."

**參數描述 (Parameter descriptions):**

- `order_id` (必填): "The unique order identifier, formatted as written characters (e.g., 'ORD123456')"
- `include_history` (選填): "If true, returns full order history including status changes"

**為什麼這對可靠性很重要：** 參數描述相當於模型的內嵌文檔。它們澄清了格式期望、必填 vs 選填欄位以及可接受的數值。

### 在系統 Prompt 中解釋何時以及如何使用每個工具

在系統 Prompt 中明確定義何時以及如何使用各個工具。不要僅僅依賴工具描述——應提供使用情境和順序邏輯。

Example:

```
# Tools

You have access to the following tools:

## `getOrderStatus`

Use this tool when a customer asks about their order. Always call this tool before providing order information—never rely on memory or assumptions.

**When to use:**

- Customer asks "Where is my order?"
- Customer provides an order number
- Customer asks about delivery estimates

**How to use:**

1. Collect the order ID from the customer in spoken format
2. Convert to written format using character normalization rules
3. Call `getOrderStatus` with the formatted order ID
4. Present the results to the customer in natural language

**Error handling:**
If the tool returns "Order not found", ask the customer to verify the order number and try again.

## `processRefund`

Use this tool only after verifying:

1. Customer identity has been confirmed
2. Order is eligible for refund (within 30 days, not already refunded)
3. Refund amount is under $500 (escalate to supervisor if over $500)

**Required before calling:**

- Order ID (from `getOrderStatus`)
- Refund reason code
- Customer confirmation

This step is important: Always confirm refund details with the customer before calling this tool.
```

### 對工具輸入使用字元規範化

當工具需要結構化標識符（電子郵件、電話號碼、代碼）時，請確保 Prompt 澄清何時使用寫入格式與語音格式。

Example:

```
# Tools

## `lookupAccount`

**Parameters:**

- `email` (required): Customer email address in written format (e.g., "john.smith@company.com")

**Usage:**

1. Ask customer for their email in spoken format: "Can you provide your email address?"
2. Listen for spoken format: "john dot smith at company dot com"
3. Convert to written format: "john.smith@company.com"
4. Pass written format to this tool

**Character normalization for email:**

- "at" → "@"
- "dot" → "."
- Remove spaces between words
```

### 優雅處理工具調用失敗

工具可能因網路問題、數據缺失或其他錯誤而失敗。在系統 Prompt 中包含清晰的恢復指令。

**為什麼這對可靠性很重要：** 在生產環境中，工具失敗是不可避免的。如果沒有明確的處理指令，agent 可能會幻覺回應或提供錯誤資訊。

Example:

```
# Tool Error Handling

If any tool call fails or returns an error:

1. Acknowledge the issue to the customer: "I'm having trouble accessing that information right now."
2. Do not guess or make up information
3. Offer alternatives:
   - Try the tool again if it might be a temporary issue
   - Offer to escalate to a human agent
   - Provide a callback option
4. If the error persists after 2 attempts, escalate to a supervisor

**Example responses:**

- "I'm having trouble looking up that order right now. Let me try again... [retry]"
- "I'm unable to access the order system at the moment. I can transfer you to a specialist who can help, or we can schedule a callback. Which would you prefer?"
```

## 企業級 Agent 的架構模式

雖然強大的 Prompt 和工具構成了 agent 可靠性的基礎，但生產系統需要深思熟慮的架構設計。企業級 agent 處理的複雜流程通常超出了單一、龐大的 Prompt 所能涵蓋的範圍。

### 保持 Agent 專業化

過於寬泛的指令或過大的上下文視窗會增加延遲並降低準確性。每個 agent 都應該擁有狹窄且清晰定義的知識庫和職責範圍。

**為什麼這對可靠性很重要：** 專業化的 agent 需要處理的邊緣情況更少、成功標準更明確，且回應時間更短。它們更容易測試、調試和改進。

通用的「全能型」agent 比起由具有清晰交接機制的專業化 agent 組成的網絡，更難維護且更容易在生產環境中失敗。

### 使用編排器 (Orchestrator) 與專家模式

對於複雜任務，設計多 agent 流程，在專業化 agent 之間交接任務，並在需要時交接給人工操作員。

**架構模式：**

1. **編排器 agent (Orchestrator agent)：** 根據意圖分類將收到的請求路由到適當的專家 agent。
2. **專家 agent (Specialist agents)：** 處理特定領域的任務（計費、排程、技術支援等）。
3. **人工升級機制：** 為複雜或敏感案例定義清晰的交接標準。

**此模式的優點：**

- 每個專家都有專注的 Prompt 並減少了上下文。
- 更容易更新個別專家而不影響整個系統。
- 每個領域都有清晰的指標（計費解決率、排程成功率等）。
- 每次交互的延遲降低（更小的 Prompt，更快的推理）。

### 定義清晰的交接標準

在設計多 agent 流程時，請精確指定何時以及如何將控制權在 agent 之間或交接給人工操作員。

Orchestrator agent example:

```
# Goal

Route customer requests to the appropriate specialist agent based on intent.

## Routing Logic

**Billing specialist:** Customer mentions payment, invoice, refund, charge, subscription, or account balance
**Technical support specialist:** Customer reports error, bug, issue, not working, broken
**Scheduling specialist:** Customer wants to book, reschedule, cancel, or check appointment
**Human escalation:** Customer is angry, requests supervisor, or issue is unresolved after 2 specialist attempts

## Handoff Process

1. Classify customer intent based on first message
2. Provide brief acknowledgment: "I'll connect you with our [billing/technical/scheduling] team."
3. Transfer conversation with context summary:
   - Customer name
   - Primary issue
   - Any account identifiers already collected
4. Do not repeat information collection that already occurred
```

Specialist agent example:

```
# Personality

You are a billing specialist for Acme Corp. You handle payment issues, refunds, and subscription changes.

# Goal

Resolve billing inquiries by:

1. Verifying customer identity
2. Looking up account and billing history
3. Processing refunds (under $500) or escalating (over $500)
4. Updating subscription settings when requested

# Guardrails

Never access account information without identity verification.
Never process refunds over $500 without supervisor approval.
If the customer's issue is not billing-related, transfer back to the orchestrator agent.
```

## 企業級可靠性的模型選擇

選擇合適的模型取決於你的性能需求——特別是延遲、準確性和工具調用可靠性。不同的模型在速度、推理能力和成本之間提供不同的權衡。

### 理解權衡取捨

**延遲 (Latency)：** 較小的模型（參數較少）通常回應更快，適用於高頻率、低複雜度的交互。

**準確性 (Accuracy)：** 較大的模型提供更強的推理能力，能更好地處理複雜的多步任務，但延遲和成本較高。

**工具調用可靠性 (Tool-calling reliability)：** 並非所有模型都能以相同的精確度處理工具/函數調用。有些擅長結構化輸出，而有些則可能需要更明確的 Prompt 設定。

### 按使用場景的模型建議

根據數百萬次 agent 交互的部署經驗，出現了以下模式：

- **GPT-4o 或 GLM 4.5 Air (建議起點)：** 適用於延遲、準確和成本必須保持平衡的通用企業級 agent。提供低至中等延遲，具有強大的工具調用性能和合理的每次交互成本。理想於客戶支援、排程、訂單管理和通用諮詢處理。

- **Gemini 2.5 Flash Lite (極低延遲)：** 適用於速度至關重要的高頻、簡單交互。提供最低的延遲和廣泛的一般知識，但在處理複雜工具調用方面的表現較弱。對於初始路由/分類、簡單常見問題集、預約確認和基本數據採集而言，具備成本效益。

- **Claude Sonnet 4 或 4.5 (複雜推理)：** 適用於多步驟問題解決、細微判斷和複雜工具編排。提供最高的準確性和推理能力，並具有出色的工具調用可靠性，但延遲和成本較高。理想於出錯代價昂貴的任務，例如技術故障排除、財務諮詢、合規敏感流程以及複雜的退款/升級決策。

### 使用你的實際 Prompt 進行基準測試 (Benchmark)

模型性能會因 Prompt 結構和任務複雜度而大不相同。在決定使用某個模型之前：

1. 使用你的實際系統 Prompt 測試 2-3 個候選模型。
2. 針對真實用戶查詢或合成測試案例進行評估。
3. 測量延遲、準確性和工具調用成功率。
4. 根據你的特定要求在權衡中找出最佳方案。

## 迭代與測試

生產環境中的可靠性源於持續的迭代。即使是構建良好的 Prompt 也有可能在實際使用中失敗。重要的是從這些失敗中學習，並通過嚴格的測試進行改進。

### 配置評估準則

為每個 agent 附加具體的評估準則，以監控隨時間推移的成功率並檢查是否出現退化。

**要追蹤的關鍵指標：**

- **任務完成率 (Task completion rate)：** 用戶意圖成功解決的百分比。
- **升級率 (Escalation rate)：** 需要人工介入的對話百分比。

### 分析失敗模式

當 agent 表現不佳時，識別有問題交互中的模式：

- **Agent 在哪裡提供了錯誤資訊？** → 加強特定區塊的指令。
- **何時無法理解用戶意圖？** → 添加範例或簡化語言。
- **哪些用戶輸入導致其偏離角色 (break character)？** → 為邊際情況添加護欄。
- **哪些工具最常失敗？** → 改進錯誤處理或參數描述。

查看用戶滿意度低或任務未完成的對話記錄。

### 進行針對性的優化

更新 Prompt 的特定區塊以解決識別出的問題：

1. **隔離問題：** 確定是哪個 Prompt 區塊或工具定義導致失敗。
2. **在特定範例上測試更改：** 將先前失敗的對話用作測試案例。
3. **一次僅進行一項更改：** 隔離改進以了解哪些是有效的。
4. **使用相同的測試案例重新評估：** 驗證更改修復了問題，且沒有產生新問題。

避免同時進行多項 Prompt 更改，否則無法將改進或退化歸因於特定的修改。

### 配置數據採集

配置你的 agent 以摘要每次對話的數據。這使你能夠分析交互模式、識別常見用戶請求，並根據現實世界的使用情況持續改進你的 Prompt。

### 使用模擬進行回歸測試

在將 Prompt 更改部署到生產環境之前，請針對一組已知場景進行測試以捕捉回歸（regressions）。

有關以程式方式測試 Agent 的指南，請參閱 [Simulate Conversations](https://elevenlabs.io/docs/agents-platform/guides/simulate-conversations)。

## 生產環境注意事項

### 處理所有工具集成的錯誤

確保你的系統 Prompt 包含對 agent 使用的所有工具的全面錯誤處理。這可以防止幻覺，並在系統故障時維護用戶信任。

## Prompt 範例

以下範例展示如何將本指南中概述的原則應用於真實世界的企業用例。每個範例都包含註釋，重點介紹使用了哪些可靠性原則。

### 範例 1：技術支援 Agent

```
[data-radix-scroll-area-viewport]{scrollbar-width:none;-ms-overflow-style:none;-webkit-overflow-scrolling:touch;}[data-radix-scroll-area-viewport]::-webkit-scrollbar{display:none}1# Personality23You are a technical support specialist for CloudTech, a B2B SaaS platform.4You are patient, methodical, and focused on resolving issues efficiently.5You speak clearly and adapt technical language based on the user's familiarity.67# Environment89You are assisting customers via phone support.10Customers may be experiencing service disruptions and could be frustrated.11You have access to diagnostic tools and the customer account database.1213# Tone1415Keep responses clear and concise (2-3 sentences unless troubleshooting requires more detail).16Use a calm, professional tone with brief affirmations ("I understand," "Let me check that").17Adapt technical depth based on customer responses.18Check for understanding after complex steps: "Does that make sense?"1920# Goal2122Resolve technical issues through structured troubleshooting:23241. Verify customer identity using email and account ID252. Identify affected service and severity level263. Run diagnostics using `runSystemDiagnostic` tool274. Provide step-by-step resolution or escalate if unresolved after 2 attempts2829This step is important: Always run diagnostics before suggesting solutions.3031# Guardrails3233Never access customer accounts without identity verification. This step is important.34Never guess at solutions—always base recommendations on diagnostic results.35If an issue persists after 2 troubleshooting attempts, escalate to engineering team.36Acknowledge when you don't know the answer instead of speculating.3738# Tools3940## `verifyCustomerIdentity`4142**When to use:** At the start of every conversation before accessing account data43**Parameters:**4445- `email` (required): Customer email in written format (e.g., "user@company.com")46- `account_id` (optional): Account ID if customer provides it4748**Usage:**49501. Ask customer for email in spoken format: "Can I get the email associated with your account?"512. Convert to written format: "john dot smith at company dot com" → "john.smith@company.com"523. Call this tool with written email5354**Error handling:**55If verification fails, ask customer to confirm email spelling and try again.5657## `runSystemDiagnostic`5859**When to use:** After verifying identity and understanding the reported issue60**Parameters:**6162- `account_id` (required): From `verifyCustomerIdentity` response63- `service_name` (required): Name of affected service (e.g., "api", "dashboard", "storage")6465**Usage:**66671. Confirm which service is affected682. Run diagnostic with account ID and service name693. Review results before providing solution7071**Error handling:**72If diagnostic fails, acknowledge the issue: "I'm having trouble running that diagnostic. Let me escalate to our engineering team."7374# Character normalization7576When collecting email addresses:7778- Spoken: "john dot smith at company dot com"79- Written: "john.smith@company.com"80- Convert "@" from "at", "." from "dot", remove spaces8182# Error handling8384If any tool call fails:85861. Acknowledge: "I'm having trouble accessing that information right now."872. Do not guess or make up information883. Offer to retry once, then escalate if failure persists
```

### 範例 2：客戶服務退款 Agent

```
1# Personality23You are a refund specialist for RetailCo.4You are empathetic, solution-oriented, and efficient.5You balance customer satisfaction with company policy compliance.67# Goal89Process refund requests through this workflow:10111. Verify customer identity using order number and email122. Look up order details with `getOrderDetails` tool133. Confirm refund eligibility (within 30 days, not digital download, not already refunded)144. For refunds under $100: Process immediately with `processRefund` tool155. For refunds $100-$500: Apply secondary verification, then process166. For refunds over $500: Escalate to supervisor with case summary1718This step is important: Never process refunds without verifying eligibility first.1920# Guardrails2122Never process refunds outside the 30-day return window without supervisor approval.23Never process refunds over $500 without supervisor approval. This step is important.24Never access order information without verifying customer identity.25If a customer becomes aggressive, remain calm and offer supervisor escalation.2627# Tools2829## `verifyIdentity`3031**When to use:** At the start of every conversation32**Parameters:**3334- `order_id` (required): Order ID in written format (e.g., "ORD123456")35- `email` (required): Customer email in written format3637**Usage:**38391. Collect order ID: "Can I get your order number?"40 - Spoken: "O R D one two three four five six"41 - Written: "ORD123456"422. Collect email and convert to written format433. Call this tool with both values4445## `getOrderDetails`4647**When to use:** After identity verification48**Returns:** Order date, items, total amount, refund eligibility status4950**Error handling:**51If order not found, ask customer to verify order number and try again.5253## `processRefund`5455**When to use:** Only after confirming eligibility56**Required checks before calling:**5758- Identity verified59- Order is within 30 days60- Order is eligible (not digital, not already refunded)61- Refund amount is under $5006263**Parameters:**6465- `order_id` (required): From previous verification66- `reason_code` (required): One of "defective", "wrong_item", "late_delivery", "changed_mind"6768**Usage:**69701. Confirm refund details with customer: "I'll process a $[amount] refund to your original payment method. It will appear in 3-5 business days. Does that work for you?"712. Wait for customer confirmation723. Call this tool7374**Error handling:**75If refund processing fails, apologize and escalate: "I'm unable to process that refund right now. Let me escalate to a supervisor who can help."7677# Character normalization7879Order IDs:8081- Spoken: "O R D one two three four five six"82- Written: "ORD123456"83- No spaces, all uppercase8485Email addresses:8687- Spoken: "john dot smith at retailco dot com"88- Written: "john.smith@retailco.com"
```

Principles demonstrated:

- ✓ Specialized agent scope (refunds only, not general support)
- ✓ Clear workflow steps in # Goal section
- ✓ Repeated emphasis on critical rules (refund limits, verification)
- ✓ Detailed tool usage with "when to use" and "required checks"
- ✓ Character normalization for structured IDs
- ✓ Explicit error handling per tool
- ✓ Escalation criteria clearly defined

## 格式化最佳實踐

您格式化 Prompt 的方式會影響語言模型解讀它的有效性：

- **使用 Markdown 標題**：使用 `#` 區分主要章節，`##` 區分小節。
- **首選項目符號列表**：將指令分解為易於消化的項目符號。
- **使用空白**：用空行分隔章節和指令群組。
- **保持標題為句首大寫 (Sentence case)**：使用 `# Goal` 而不是 `# GOAL`。
- **保持一致**：在整個 Prompt 中使用相同的格式化模式。

```
#
```

```
##
```

```
# Goal
```

```
# GOAL
```

## 常見問題 (FAQ)

###### 如何在多個 Agent 之間保持一致性？

為字元規範化、錯誤處理和護欄等通用章節建立共享的 Prompt 模板。將這些儲存在中央存儲庫中，並在專家 Agent 中引用它們。使用編排器模式確保一致的路由邏輯和交接程序。

###### 生產環境的最小可行 Prompt 是什麼？

至少包括：(1) 個性/角色定義，(2) 主要目標，(3) 核心護欄，以及 (4) 工具描述（如果有使用工具）。即使是簡單的 Agent 也能從明確的章節結構和錯誤處理指令中受益。

###### 如何在不破壞 Agent 的情況下處理工具棄用？

棄用工具時，先添加新工具，然後更新 Prompt 以優先使用新工具，同時保留舊工具作為備案。監控使用情況，一旦舊工具的使用率降至零，即將其移除。務必包含錯誤處理，以便 Agent 在被調用已棄用的工具時能夠恢復。

###### 我應該為不同的 LLM 使用不同的 Prompt 嗎？

通常，根據本指南中的原則構建的 Prompt 適用於各種模型。然而，針對特定模型的微調可以提高性能——特別是在工具調用格式和推理步驟方面。使用多個模型測試您的 Prompt 並在需要時進行調整。

###### 我的系統 Prompt 應該多長？

沒有通用的限制，但超過 2000 個 token 的 Prompt 會增加延遲和成本。專注於簡潔：每一行都應有明確的目的。如果您的 Prompt 超過 2000 個 token，請考慮將其拆分為多個專業化 Agent，或將參考資料提取到知識庫中。

###### 如何平衡一致性與適應性？

明確定義核心個性特徵、目標和護欄，同時允許根據用戶溝通風格在語氣和冗長度上具有靈活性。使用條件指令：「如果用戶感到沮喪，請在繼續之前承認他們的擔憂。」

###### 我可以在部署後更新 Prompt 嗎？

可以。系統 Prompt 可以在任何時候修改以調整行為。這對於解決新出現的問題或在從用戶交互中學習時改進功能特別有用。在部署到生產環境之前，務必在模擬環境中測試更改。

###### 當工具失敗時，如何防止 Agent 產生幻覺？

為每個工具包含明確的錯誤處理指令。在護欄章節中強調「切勿猜測或虛構資訊」。在特定於工具的錯誤處理章節中重複此指令。在開發期間測試工具失敗場景，以確保 Agent 遵循恢復指令。

## 下一步

本指南通過 Prompt 工程、工具配置和架構模式為可靠的 Agent 行為建立了基礎。要構建生產級系統，請繼續閱讀：

- [Workflows](https://elevenlabs.io/docs/agents-platform/customization/agent-workflows)：設計多 Agent 編排和專家交接
- [Success Evaluation](https://elevenlabs.io/docs/agents-platform/customization/agent-analysis/success-evaluation)：配置指標和評估準則
- [Data Collection](https://elevenlabs.io/docs/agents-platform/customization/agent-analysis/data-collection)：從對話中獲取結構化洞察
- [Testing](https://elevenlabs.io/docs/agents-platform/customization/agent-testing)：實施回歸測試和模擬
- [Security & Privacy](https://elevenlabs.io/docs/agents-platform/customization/privacy)：確保合規性和數據保護
- [Our Docs Agent](https://elevenlabs.io/docs/agents-platform/guides/elevenlabs-docs-agent)：查看這些原則在實際操作中的完整案例研究

如需企業部署支援，請[聯繫我們的團隊](https://elevenlabs.io/contact-sales)。

## 關鍵要點

1. **結構至關重要：** 使用清晰的區塊、標題和空格幫助模型排定指令優先順序。
2. **簡潔是關鍵：** 每個字都應有其目的；刪除贅字。
3. **強調護欄：** 對不可逾越的規則使用專用區塊和重複強調。
4. **工具清晰度：** 提供詳細的參數描述和使用背景。
5. **專業化 Agent：** 縮小範圍可提高可靠性並減少延遲。
6. **持續測試：** 使用真實對話數據來識別並修復失敗模式。
7. **選擇合適的模型：** 為你的特定用例平衡延遲、準確性和成本。

---

**來源：** [ElevenLabs Prompting Guide](https://elevenlabs.io/docs/agents-platform/best-practices/prompting-guide)
