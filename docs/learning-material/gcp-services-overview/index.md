# GCP 服務總覽學習教材

## 概述

本教材涵蓋 ElevenDops 專案使用的 Google Cloud Platform (GCP) 服務。從資料儲存、容器部署、密鑰管理到本地開發環境設定，提供完整的學習路徑。

## 文件目錄

| 文件                                                             | 說明                                                  |
| ---------------------------------------------------------------- | ----------------------------------------------------- |
| [01--introduction.md](./01--introduction.md)                     | GCP 服務總覽與架構圖，適合初次了解專案架構的讀者。    |
| [02--data-and-storage.md](./02--data-and-storage.md)             | Firestore 與 Cloud Storage 深入介紹，包含程式碼範例。 |
| [03--deployment-and-secrets.md](./03--deployment-and-secrets.md) | Cloud Run 部署流程與 Secret Manager 密鑰管理實務。    |
| [04--local-development.md](./04--local-development.md)           | Firebase Emulator 與 fake-gcs-server 的設定與使用。   |

## 學習路徑建議

1. 先閱讀 [01--introduction.md](./01--introduction.md) 建立整體架構概念。
2. 若您負責後端開發，重點閱讀 [02--data-and-storage.md](./02--data-and-storage.md)。
3. 若您負責 DevOps 或部署，重點閱讀 [03--deployment-and-secrets.md](./03--deployment-and-secrets.md)。
4. 所有開發者都應熟悉 [04--local-development.md](./04--local-development.md) 的本地環境設定。

## 相關資源

- [本專案：遷移至真實 GCP 服務指南](../../development-guide/guide--migrate-to-real-gcp.md)
- [Google Cloud Run 官方文件](https://cloud.google.com/run/docs)
- [Firestore 官方文件](https://firebase.google.com/docs/firestore)
- [Cloud Storage 官方文件](https://cloud.google.com/storage/docs)
- [Secret Manager 官方文件](https://cloud.google.com/secret-manager/docs)
