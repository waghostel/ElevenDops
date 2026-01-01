# Streamlit 動態 Key 模式 學習教材

## 概述

本教材說明如何使用動態 Key 模式解決 Streamlit 元件資料不更新的問題。這是開發 Streamlit 應用程式時常見的陷阱，尤其在使用第三方元件或 `@st.fragment` 時。

## 文件目錄

| 文件                                             | 說明                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| [01--introduction.md](./01--introduction.md)     | 介紹動態 Key 模式的基本概念，說明為什麼靜態 Key 會導致資料過時問題。 |
| [02--implementation.md](./02--implementation.md) | 詳細說明實作步驟，包含完整程式碼範例與最佳實踐。                     |

## 學習路徑建議

1. 首先閱讀 [01--introduction.md](./01--introduction.md) 了解問題成因與解決概念
2. 接著參考 [02--implementation.md](./02--implementation.md) 學習實際應用方式

## 相關資源

- [Streamlit 官方文件 - Widget State](https://docs.streamlit.io/develop/concepts/architecture/widget-behavior)
- [Streamlit Fragments 說明](https://docs.streamlit.io/develop/concepts/architecture/fragments)
