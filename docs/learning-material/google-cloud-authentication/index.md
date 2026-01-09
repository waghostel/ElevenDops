# Google Cloud Authentication (GCP 身分驗證) 學習教材

## 概述

身分驗證是雲端開發中最關鍵的一環。本教材旨在幫助開發者理解 Google Cloud 的身分驗證機制，特別是如何透過 Application Default Credentials (ADC) 安全地在本地環境與雲端環境之間切換，而不需要暴露敏感的金鑰檔案。

## 文件目錄

| 文件                                                                                           | 說明                                                 |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| [01--introduction-to-adc.md](./01--introduction-to-adc.md)                                     | 深度介紹 ADC 的核心概念與運作原理。                  |
| [02--setting-up-local-adc.md](./02--setting-up-local-adc.md)                                   | 實作教學：如何在本地開發環境配置與使用 ADC。         |
| [03--advanced-concepts-and-troubleshooting.md](./03--advanced-concepts-and-troubleshooting.md) | 進階概念（服務帳戶 vs 個人帳戶）與常見問題排除。     |
| [04--adc-authorization-and-integration.md](./04--adc-authorization-and-integration.md)         | 授權指南與實戰整合：Owner vs Member 流程及指令解析。 |

## 學習路徑建議

1. 首先閱讀 [01--introduction-to-adc.md](./01--introduction-to-adc.md) 了解為何 Google 推薦使用 ADC。
2. 按照 [02--setting-up-local-adc.md](./02--setting-up-local-adc.md) 的步驟在本地機器上完成設定。
3. 若遇到權限或 Docker 環境問題，請參考 [03--advanced-concepts-and-troubleshooting.md](./03--advanced-concepts-and-troubleshooting.md)。

## 相關資源

- [官方實戰手冊：對應用程式進行驗證](https://cloud.google.com/docs/authentication/application-default-credentials)
- [ElevenDops 遷移指南](../../development-guide/guide--migrate-to-real-gcp.md)

---

[⬅️ 返回學習教材總覽](../index.md)
