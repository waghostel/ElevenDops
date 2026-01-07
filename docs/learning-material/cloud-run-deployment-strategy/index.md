# ElevenDops Cloud Run 部署策略學習教材

## 概述

本教材旨在協助開發者理解 ElevenDops 在 Google Cloud Platform (GCP) 上的部署架構與自動化流程。我們採用了現代化的單一容器 (Single-Container) 模式，結合 Cloud Build 實現極簡化且安全的 CI/CD 體驗。

## 文件目錄

| 文件                                                                           | 說明                                                                    |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| [01--single-container-architecture.md](./01--single-container-architecture.md) | 深入探討 FastAPI 與 Streamlit 如何在同一個容器中並存共舞。              |
| [02--cicd-pipeline-automation.md](./02--cicd-pipeline-automation.md)           | 解析從 GitHub 推送代碼到 Cloud Run 服務發布的自動化奧秘。               |
| [03--security-and-scaling.md](./03--security-and-scaling.md)                   | 學習如何透過非根用戶、Secret Manager 與自動縮放提升系統的安全性與效能。 |

## 學習路徑建議

1. **基礎概念**：首先閱讀 [01--single-container-architecture.md](./01--single-container-architecture.md) 了解系統運行的實體結構。
2. **自動化流程**：接著參考 [02--cicd-pipeline-automation.md](./02--cicd-pipeline-automation.md) 掌握開發工作流。
3. **安全進階**：最後查閱 [03--security-and-scaling.md](./03--security-and-scaling.md) 確保您的部署符合生產環境的安全標準。

## 相關資源

- [部署首頁文件](../../docs/cloud-run-deployment/index.md)
- [CI/CD Pipeline 詳細指南](../../docs/cloud-run-deployment/guide--cicd-pipeline.md)
- [GCP Cloud Run 官方文件](https://cloud.google.com/run/docs)
