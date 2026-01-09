# Firebase 本地測試學習教材

## 概述

本教材旨在協助開發者了解如何在本地環境中測試 Firebase Firestore 資料庫連線。涵蓋了使用 Emulator 進行快速開發測試，以及連線真實 Firebase 專案進行驗收測試的完整流程。

通過本教材，您將學會如何配置環境變數、啟動模擬器、以及使用 Python 腳本驗證資料庫的 CRUD 操作。

## 文件目錄

| 文件                                                                     | 說明                                                                           |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| [01--overview-and-setup.md](./01--overview-and-setup.md)                 | 介紹 Emulator 與真實環境的差異，以及如何設定 `.env` 與 Docker 來建置測試環境。 |
| [02--execution-and-verification.md](./02--execution-and-verification.md) | 詳細說明如何執行驗證腳本、整合測試，以及如何進行手動驗證。                     |

## 學習路徑建議

1. **初次設定**：請先閱讀 [01--overview-and-setup.md](./01--overview-and-setup.md) 了解基礎概念並完成環境配置。
2. **驗證測試**：設定完成後，參考 [02--execution-and-verification.md](./02--execution-and-verification.md) 執行 `Verify` 腳本確認連線成功。
3. **日常開發**：在日常開發中，建議保持 `USE_FIRESTORE_EMULATOR=True` 以加快開發速度並節省成本。

## 相關資源

- [Google Firebase Emulator Suite](https://firebase.google.com/docs/emulator-suite)
- [專案實作計畫 (Implementation Plan)](../../../.gemini/antigravity/brain/f05560b3-bce2-4757-9f71-5418cf709fa7/implementation_plan--testing-firebase-locally.md)
- [驗證腳本 (verify_firestore_connectivity.py)](../../../tests/verify_firestore_connectivity.py)

---

[⬅️ 返回學習教材總覽](../index.md)
