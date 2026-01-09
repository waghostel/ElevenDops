# Firestore 版本 (Editions) 學習教材

## 概述

Google Cloud 在 2024 年推出了 Firestore 的全新版本劃分。本教材旨在幫助開發者理解 **Standard (標準版)** 與 **Enterprise (企業版)** 之間的技術差異、計費邏輯以及如何根據專案需求做出最佳選擇。

## 文件目錄

| 文件                                                         | 說明                                                                               |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| [01--edition-comparison.md](./01--edition-comparison.md)     | 深入比較 Standard 與 Enterprise 的功能、限制（如 1MB vs 4MB）以及 MongoDB 相容性。 |
| [02--pricing-models.md](./02--pricing-models.md)             | 詳細解析次數計費 (Count-based) 與單位計費 (Unit-based) 的差異，並介紹免費額度。    |
| [03--setup-configurations.md](./03--setup-configurations.md) | 解釋 Native mode 與安全性規則 (Security Rules) 的設定邏輯與安全選擇。              |

## 學習路徑建議

1. **技術選型**：首先閱讀 [01--edition-comparison.md](./01--edition-comparison.md) 確認專案是否需要 Enterprise 的進階功能。
2. **預算評估**：參考 [02--pricing-models.md](./02--pricing-models.md) 了解營運成本。
3. **初始部署**：閱讀 [03--setup-configurations.md](./03--setup-configurations.md) 學習如何在建立資料庫時做出最安全的設定。

## 相關資源

- [Google Cloud Firestore 官方文件](https://cloud.google.com/firestore)
- [Firebase 部落格：Enterprise 版介紹](https://firebase.google.com/blog)

---

[⬅️ 返回學習教材總覽](../index.md)
