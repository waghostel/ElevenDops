# Secret Manager 學習教材

## 概述

本教材介紹 Google Cloud Secret Manager 的使用方式。Secret Manager 是管理敏感資訊（如 API 金鑰、資料庫密碼）的安全服務，避免將秘密直接寫入程式碼或環境變數檔案。

## 文件目錄

| 文件                                                           | 說明                                                       |
| -------------------------------------------------------------- | ---------------------------------------------------------- |
| [01--introduction.md](./01--introduction.md)                   | Secret Manager 的核心概念與優勢，以及與環境變數的比較。    |
| [02--cloud-run-integration.md](./02--cloud-run-integration.md) | 如何在 Cloud Run 中安全地存取 Secrets。                    |
| [03--local-development.md](./03--local-development.md)         | 本地開發時如何使用 `.env` 作為 Secret Manager 的替代方案。 |

## 學習路徑建議

1. 首先閱讀 [01--introduction.md](./01--introduction.md) 了解為何需要 Secret Manager。
2. 部署到雲端時參考 [02--cloud-run-integration.md](./02--cloud-run-integration.md)。
3. 本地開發時參考 [03--local-development.md](./03--local-development.md) 設定環境。

## 相關資源

- [Secret Manager 官方文件](https://cloud.google.com/secret-manager/docs)
- [本專案環境變數說明](../../backend/config.py)
