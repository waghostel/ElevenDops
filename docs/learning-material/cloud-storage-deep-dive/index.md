# Cloud Storage (GCS) 深度解析學習教材

## 概述

本教材深入介紹 Google Cloud Storage 的進階功能與最佳實務。涵蓋 Bucket 配置、Signed URLs 安全存取機制、CORS 設定，以及成本優化策略。

## 文件目錄

| 文件                                                                 | 說明                                           |
| -------------------------------------------------------------------- | ---------------------------------------------- |
| [01--bucket-configuration.md](./01--bucket-configuration.md)         | Bucket 建立、生命週期管理與 CORS 配置。        |
| [02--signed-urls-and-security.md](./02--signed-urls-and-security.md) | Signed URLs 的原理與實作，安全地分享私有物件。 |
| [03--cost-optimization.md](./03--cost-optimization.md)               | Storage Class 選擇與成本優化策略。             |

## 學習路徑建議

1. 首先閱讀 [01--bucket-configuration.md](./01--bucket-configuration.md) 了解基礎配置。
2. 接著參考 [02--signed-urls-and-security.md](./02--signed-urls-and-security.md) 實作安全存取機制。
3. 最後閱讀 [03--cost-optimization.md](./03--cost-optimization.md) 優化儲存成本。

## 相關資源

- [Cloud Storage 官方文件](https://cloud.google.com/storage/docs)
- [本專案 Storage 服務實作](../../backend/services/storage_service.py)
