# Artifact Registry 學習教材

## 概述

Artifact Registry 是 Google Cloud 的通用軟體產物管理服務，用於儲存和管理容器映像檔、語言套件及其他建置產物。在 ElevenDops 專案中，我們使用 Artifact Registry 來儲存 Cloud Run 部署所需的 Docker 映像檔。

## 文件目錄

| 文件                                                           | 說明                                                       |
| -------------------------------------------------------------- | ---------------------------------------------------------- |
| [01--introduction.md](./01--introduction.md)                   | Artifact Registry 基礎概念、與 Container Registry 的比較。 |
| [02--repository-management.md](./02--repository-management.md) | 儲存庫建立、權限設定與映像檔管理。                         |
| [03--cleanup-policies.md](./03--cleanup-policies.md)           | 清理策略設定，控制儲存成本與版本管理。                     |

## 學習路徑建議

1. 首先閱讀 [01--introduction.md](./01--introduction.md) 了解 Artifact Registry 的基本概念與架構。
2. 接著參考 [02--repository-management.md](./02--repository-management.md) 學習如何建立和管理儲存庫。
3. 最後閱讀 [03--cleanup-policies.md](./03--cleanup-policies.md) 了解如何設定清理策略以控制成本。

## 相關資源

- [Google Cloud Artifact Registry 官方文件](https://cloud.google.com/artifact-registry/docs)
- [本專案：Cloud Build 學習教材](../google-cloud-build/index.md)
- [本專案：Cloud Run 部署策略](../cloud-run-deployment-strategy/index.md)

---

[⬅️ 返回學習教材總覽](../index.md)
