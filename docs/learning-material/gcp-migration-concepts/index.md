# GCP 遷移與基礎概念學習教材

## 概述

本教材旨在協助開發者理解從「本地模擬器開發」遷移至「真實 Google Cloud Platform (GCP) 服務」所需的背景知識與關鍵概念。涵蓋基礎架構、身分驗證機制以及資料儲存模型的差異。

## 文件目錄

| 文件                                                                   | 說明                                                                |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [01--core-infrastructure.md](./01--core-infrastructure.md)             | 介紹 GCP 專案、帳單與 API 的基礎架構概念。                          |
| [02--authentication-mechanisms.md](./02--authentication-mechanisms.md) | 深入解析應用程式預設憑證 (ADC) 與 IAM 權限管理。                    |
| [03--data-persistence-models.md](./03--data-persistence-models.md)     | 比較模擬器與真實服務在資料保存上的差異，以及 Firestore/GCS 的結構。 |

## 學習路徑建議

1. **基礎認知**：閱讀 [01--core-infrastructure.md](./01--core-infrastructure.md) 了解為何需要建立 Project 與 Billing。
2. **安全實作**：閱讀 [02--authentication-mechanisms.md](./02--authentication-mechanisms.md) 學習如何在不洩漏金鑰的情況下進行本地開發。
3. **資料管理**：閱讀 [03--data-persistence-models.md](./03--data-persistence-models.md) 理解資料庫遷移後的行為變化。

## 相關資源

- [ElevenDops Migration Guide](../../development-guide/guide--migrate-to-real-gcp.md)
- [Google Cloud Documentation](https://cloud.google.com/docs)

---

[⬅️ 返回學習教材總覽](../index.md)
