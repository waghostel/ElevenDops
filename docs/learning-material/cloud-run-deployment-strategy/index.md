# ElevenDops Cloud Run 部署策略學習教材

## 概述

本教材旨在協助開發者理解 ElevenDops 在 Google Cloud Platform (GCP) 上的部署架構與自動化流程。我們採用了現代化的單一容器 (Single-Container) 模式，結合 Cloud Build 實現極簡化且安全的 CI/CD 體驗。

## 文件目錄

| 文件                                                                             | 說明                                                                    |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [01--single-container-architecture.md](./01--single-container-architecture.md)   | 深入探討 FastAPI 與 Streamlit 如何在同一個容器中並存共舞。              |
| [02--cicd-pipeline-automation.md](./02--cicd-pipeline-automation.md)             | 解析從 GitHub 推送代碼到 Cloud Run 服務發布的自動化奧秘。               |
| [03--security-and-scaling.md](./03--security-and-scaling.md)                     | 學習如何透過非根用戶、Secret Manager 與自動縮放提升系統的安全性與效能。 |
| [04--multi-frontend-architecture.md](./04--multi-frontend-architecture.md)       | 使用 Nginx 反向代理在單一容器中運行多個前端（React + Streamlit）。      |
| [05--cors-configuration.md](./05--cors-configuration.md)                         | CORS 跨域設定與安全配置，避免常見安全漏洞。                             |
| [06--docker-container-structure.md](./06--docker-container-structure.md)         | 使用 Mermaid 圖解剖析生產環境 Docker 容器的內部結構與啟動流程。         |
| [07--application-security-headers.md](./07--application-security-headers.md)     | 應用程式層級的安全 Headers、XSRF 防護與速率限制實作。                   |
| [08--environment-variable-injection.md](./08--environment-variable-injection.md) | 環境變數注入機制，涵蓋 Secret Manager 與 Cloud Build 整合。             |
| [09--entrypoint-script-explained.md](./09--entrypoint-script-explained.md)       | 詳解 start.sh 進入點腳本：進程管理、健康檢查與優雅關閉機制。            |

## 學習路徑建議

1. **基礎概念**：首先閱讀 [01--single-container-architecture.md](./01--single-container-architecture.md) 了解系統運行的實體結構。
2. **自動化流程**：接著參考 [02--cicd-pipeline-automation.md](./02--cicd-pipeline-automation.md) 掌握開發工作流。
3. **安全進階**：查閱 [03--security-and-scaling.md](./03--security-and-scaling.md) 確保您的部署符合生產環境的安全標準。
4. **進階架構**：參考 [04--multi-frontend-architecture.md](./04--multi-frontend-architecture.md) 學習多前端部署策略。
5. **API 安全**：閱讀 [05--cors-configuration.md](./05--cors-configuration.md) 了解跨域設定與安全實踐。
6. **容器解密**：深入 [06--docker-container-structure.md](./06--docker-container-structure.md) 了解黑盒子裡的運作細節。
7. **應用安全**：閱讀 [07--application-security-headers.md](./07--application-security-headers.md) 學習應用程式層的安全強化。
8. **環境變數**：參考 [08--environment-variable-injection.md](./08--environment-variable-injection.md) 了解執行時注入敏感資訊的最佳實踐。
9. **進入點腳本**：最後閱讀 [09--entrypoint-script-explained.md](./09--entrypoint-script-explained.md) 理解容器啟動後的進程管理機制。

## 相關資源

- [部署首頁文件](../../docs/cloud-run-deployment/index.md)
- [CI/CD Pipeline 詳細指南](../../docs/cloud-run-deployment/guide--cicd-pipeline.md)
- [GCP Cloud Run 官方文件](https://cloud.google.com/run/docs)

---

[⬅️ 返回學習教材總覽](../index.md)
