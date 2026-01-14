# WebSocket Drain Timeout 學習教材

## 概述

本教材說明如何使用「Drain Timeout」模式解決 WebSocket 通訊中的無限等待問題。此模式特別適用於需要收集完整回應但又要避免被 ping 事件卡住的場景。

## 文件目錄

| 文件                                                           | 說明                                                         |
| -------------------------------------------------------------- | ------------------------------------------------------------ |
| [01--problem-analysis.md](./01--problem-analysis.md)           | 分析 WebSocket 無限等待問題的根本原因，包含實際日誌範例。    |
| [02--drain-timeout-pattern.md](./02--drain-timeout-pattern.md) | 詳細說明 Drain Timeout 模式的設計原理與實作步驟。            |
| [03--implementation-guide.md](./03--implementation-guide.md)   | 完整的程式碼實作範例，包含 Python async/await 與 WebSocket。 |
| [04--testing-verification.md](./04--testing-verification.md)   | 測試策略與驗證方法，確保 Drain Timeout 正確運作。            |

## 學習路徑建議

1. 首先閱讀 [01--problem-analysis.md](./01--problem-analysis.md) 了解問題背景
2. 接著參考 [02--drain-timeout-pattern.md](./02--drain-timeout-pattern.md) 學習解決方案
3. 透過 [03--implementation-guide.md](./03--implementation-guide.md) 進行實作練習
4. 最後使用 [04--testing-verification.md](./04--testing-verification.md) 驗證實作正確性

## 相關資源

- [ElevenLabs Conversational AI WebSocket API](../../elevenlabs-api/guide--conversational-ai.md)
- [Patient Test 頁面實作](../../../streamlit_app/pages/5_Patient_Test.py)
- [ElevenLabs Service 實作](../../../backend/services/elevenlabs_service.py)

---

[⬅️ 返回學習教材總覽](../index.md)
