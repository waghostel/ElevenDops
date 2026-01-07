# GitHub Actions 工作流學習教材

## 概述

本教材旨在介紹如何利用 GitHub Actions 提升 ElevenDops 的開發品質與自動化程度。雖然我們的部署已經交由 Cloud Build 負責，但 GitHub Actions 在「程式碼品質門檻」與「文件自動化」方面仍扮演著不可或缺的角色。

## 文件目錄

| 文件                                                           | 說明                                                   |
| -------------------------------------------------------------- | ------------------------------------------------------ |
| [01--pr-unit-testing.md](./01--pr-unit-testing.md)             | 學習如何在 PR 階段自動執行 pytest，確保邏輯正確。      |
| [02--code-quality-linting.md](./02--code-quality-linting.md)   | 掌握 oxlint 與 eslint 的自動化配置，維持代碼潔癖。     |
| [03--automated-docs-update.md](./03--automated-docs-update.md) | 實作「文檔即代碼」，讓 GitHub 自行更新並維護技術文件。 |

## 學習路徑建議

1. **基礎防線**：首先閱讀 [01--pr-unit-testing.md](./01--pr-unit-testing.md)，這是保護 `main` 分支最基本的手段。
2. **開發規範**：參考 [02--code-quality-linting.md](./02--code-quality-linting.md) 讓工具幫您把關代碼風格。
3. **極致自動化**：最後查閱 [03--automated-docs-update.md](./03--automated-docs-update.md) 學習如何讓 GitHub Actions 幫您寫作業（維護文件）。

## 相關資源

- [GitHub Actions 官方手冊](https://docs.github.com/en/actions)
- [ElevenDops 部署策略教材](../cloud-run-deployment-strategy/index.md)
- [專案技術規範 (System Prompt Reference)](../../.kiro/steering/tech.md)
