# Firebase Security Rules 學習教材

## 概述

本教材介紹 Firebase Security Rules 的撰寫與測試方法。Security Rules 是保護 Firestore 與 Cloud Storage 資料的第一道防線，確保只有授權的使用者能存取特定資源。

## 文件目錄

| 文件                                                           | 說明                                                               |
| -------------------------------------------------------------- | ------------------------------------------------------------------ |
| [01--rules-fundamentals.md](./01--rules-fundamentals.md)       | Security Rules 的語法與基本概念，包含 `match` 與 `allow` 規則。    |
| [02--role-based-access.md](./02--role-based-access.md)         | 實作角色型存取控制 (RBAC)，根據使用者權限控制資料存取。            |
| [03--testing-with-emulator.md](./03--testing-with-emulator.md) | 使用 Firebase Emulator 測試 Security Rules，避免部署後才發現問題。 |

## 學習路徑建議

1. 首先閱讀 [01--rules-fundamentals.md](./01--rules-fundamentals.md) 了解基本語法。
2. 接著參考 [02--role-based-access.md](./02--role-based-access.md) 設計符合需求的權限模型。
3. 最後閱讀 [03--testing-with-emulator.md](./03--testing-with-emulator.md) 學習測試方法。

## 相關資源

- [Firebase Security Rules 官方文件](https://firebase.google.com/docs/rules)
- [Security Rules 線上測試工具](https://firebase.google.com/docs/rules/simulator)

---

[⬅️ 返回學習教材總覽](../index.md)
