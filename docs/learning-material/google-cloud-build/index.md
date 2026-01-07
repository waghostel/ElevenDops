# Google Cloud Build 學習教材

## 概述

Google Cloud Build 是一個受管理且無伺服器的 CI/CD 平台，可讓您在 Google Cloud 基礎架構上建置、測試及部署軟體。在本專案 ElevenDops 中，我們使用 Cloud Build 來實作自動化部署流程，將程式碼打包成 Docker 映像檔並部署至 Cloud Run。

## 文件目錄

| 文件                                                                                     | 說明                                                                  |
| ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [01--basics-and-concepts.md](./01--basics-and-concepts.md)                               | 介紹 Cloud Build 的基本概念、核心元件與運作原理。                     |
| [02--project-application.md](./02--project-application.md)                               | 詳細解析 ElevenDops 專案中的 `cloudbuild.yaml` 設定與自動化部署流程。 |
| [03--troubleshooting-and-best-practices.md](./03--troubleshooting-and-best-practices.md) | 常見錯誤排查、權限設定與建置最佳實踐。                                |

## 學習路徑建議

1. **初學者**：建議從 [01--basics-and-concepts.md](./01--basics-and-concepts.md) 開始，建立基礎認知。
2. **開發維護者**：直接查閱 [02--project-application.md](./02--project-application.md) 以了解專案目前的 CI/CD 實作細節。
3. **遇到問題時**：請參考 [03--troubleshooting-and-best-practices.md](./03--troubleshooting-and-best-practices.md) 進行除錯。

## 相關資源

- [Google Cloud Build 官方文件](https://cloud.google.com/build/docs)
- [專案架構文件](../../structure.md)
- [Cloud Run 部署手冊](../cloud-run-deployment/index.md)
