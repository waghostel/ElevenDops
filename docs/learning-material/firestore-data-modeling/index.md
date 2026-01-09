# Firestore 資料建模學習教材

## 概述

本教材旨在協助開發者理解如何在 Firestore 中設計高效的資料結構。涵蓋 Collection/Document 設計原則、複合索引與查詢優化，以及交易與批次寫入的最佳實務。

## 文件目錄

| 文件                                                                 | 說明                                                                                     |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [01--document-structure.md](./01--document-structure.md)             | Collection 與 Document 的結構設計，包含子集合 (Subcollection) 的使用時機與反正規化策略。 |
| [02--query-and-indexes.md](./02--query-and-indexes.md)               | Firestore 查詢限制與複合索引的建立方式，提升查詢效能的技巧。                             |
| [03--transactions-and-batches.md](./03--transactions-and-batches.md) | 交易 (Transaction) 與批次寫入 (Batch Write) 的差異與使用情境。                           |

## 學習路徑建議

1. 首先閱讀 [01--document-structure.md](./01--document-structure.md) 建立資料結構設計思維。
2. 接著參考 [02--query-and-indexes.md](./02--query-and-indexes.md) 了解查詢優化。
3. 最後閱讀 [03--transactions-and-batches.md](./03--transactions-and-batches.md) 處理複雜寫入操作。

## 相關資源

- [Firestore 官方資料建模指南](https://firebase.google.com/docs/firestore/data-model)
- [本專案 Firestore 服務實作](../../backend/services/firestore_data_service.py)

---

[⬅️ 返回學習教材總覽](../index.md)
