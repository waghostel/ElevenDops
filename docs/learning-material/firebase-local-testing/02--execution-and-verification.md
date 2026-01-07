# 執行與驗證

## 關鍵字

- **Verification Script**：驗證腳本，用於自動化檢查系統狀態的小型程式。
- **Integration Test**：整合測試，測試模組與模組、或模組與外部系統（如資料庫）之間的協作。

## 學習目標

完成本章節後，您將能夠：

1. 使用提供的驗證腳本測試資料庫連線。
2. 執行整合測試以確保功能正常。
3. 進行簡單的手動驗證。

## 步驟說明

### 步驟 1：執行驗證腳本

#### 我們在做什麼？

執行一個專門編寫的 Python 腳本 `verify_firestore_connectivity.py`，它會嘗試進行 CRUD（建立、讀取、更新、刪除）操作，以快速確認資料庫是否正常運作。

#### 為什麼需要這樣做？

在執行完整的應用程式或複雜的測試套件之前，先用一個簡單的腳本確認基礎連線，可以幫助我們快速排除環境設定問題。

#### 程式碼範例

```python
# 範例：如何執行驗證腳本
# 設定環境變數以確保連線到 Emulator (如果正在使用 Emulator)
$env:TEST_AGAINST_EMULATOR="true"

# 使用 uv 執行腳本
uv run python tests/verify_firestore_connectivity.py
```

**預期輸出結果：**

```text
--- Firestore Connectivity Verification ---
Using Firestore Emulator at: localhost:8080
Attempting to create document...
Successfully created document...
Attempting to retrieve document...
Successfully retrieved and verified document content!
Attempting to delete document...
Successfully deleted document.

--- Verification Successful! ---
```

### 步驟 2：執行整合測試 (Integration Tests)

#### 我們在做什麼？

執行專案中既有的整合測試套件，這些測試會更全面地檢查資料服務的各個屬性與功能。

#### 為什麼需要這樣做？

單一腳本只能驗證「能通」，整合測試則能驗證「功能正確」，例如資料格式是否正確、查詢過濾是否生效等。

#### 程式碼範例

```powershell
# 執行標記為 integration 的測試
# 並明確指定使用 Emulator 模式
$env:TEST_AGAINST_EMULATOR="true"
uv run pytest tests/test_firestore_data_service_props.py -m integration
```

### 步驟 3：手動驗證 (Emulator UI)

#### 我們在做什麼？

透過瀏覽器查看 Firestore Emulator 的圖形化介面 (UI)，直接觀察資料的變化。

#### 為什麼需要這樣做？

有時候自動化測試通過了，但我們還是希望能親眼看到資料長什麼樣子，這對於除錯非常有幫助。

#### 操作說明

1. 確保 Emulator 正在運行 (`docker-compose up`)。
2. 開啟瀏覽器，前往 `http://localhost:4000` (預設 UI Port)。
3. 點選 **Firestore** 頁籤。
4. 您應該能看到 `knowledge_documents` 或 `conversations` 等集合。
5. 當您執行驗證腳本時，您可以在介面上即時看到資料的產生與消失。

> **注意**：如果您使用的是精簡版的 Emulator 映像檔（如我們 `docker-compose.dev.yml` 設定的），可能不包含 UI 介面。此時請依賴日誌與腳本驗證。

## 常見問題 Q&A

### Q1：驗證腳本執行失敗，顯示 Connection Refused 怎麼辦？

**答：** 這通常代表 Emulator 沒有啟動。請請檢查：

1. 是否已執行 `docker-compose up -d`？
2. `docker ps` 是否看得到 `firestore-emulator` 容器？
3. 埠號 `8080` 是否被防火牆或其他程式佔用？

### Q2：測試真實 Firebase 時，可以直接用這個腳本嗎？

**答：** **可以，但請小心**。
若要在真實環境執行：

1. 設定 `.env` 中的 `USE_FIRESTORE_EMULATOR=False`。
2. 移除 `$env:TEST_AGAINST_EMULATOR="true"` 環境變數（或設為 "false"）。
3. 執行 `uv run python tests/verify_firestore_connectivity.py`。
4. **警告**：這會在您的真實資料庫產生測試數據（雖然腳本會嘗試刪除，但若中途失敗可能會殘留）。

## 重點整理

| 方法         | 指令/工具                                 | 適用時機                 |
| :----------- | :---------------------------------------- | :----------------------- |
| **快速驗證** | `python verify_firestore_connectivity.py` | 環境架設後的第一次確認   |
| **完整驗證** | `pytest -m integration`                   | 開發功能後，確保邏輯正確 |
| **視覺驗證** | Emulator UI / Firebase Console            | 除錯、檢查資料結構       |

## 延伸閱讀

- [Pytest 官方文件](https://docs.pytest.org/)
- [Tenacity Retry Library (用於處理連線不穩)](https://tenacity.readthedocs.io/)
