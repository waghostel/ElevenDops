# Firestore 成本優化策略 (Cost Optimization)

## 關鍵字

- **Caching (快取)**：將資料暫存在記憶體中，減少對資料庫的請求。
- **Debouncing (防抖)**：延遲執行寫入，直到使用者停止操作一段時間。
- **Denormalization (去正規化)**：以空間換取金錢，合併文件以減少讀取次數。
- **Index Exemptions (索引豁免)**：關閉特定欄位的索引以降低寫入成本。

## 學習目標

完成本章節後，您將能夠：

1. 透過快取機制降低讀取 (Reads) 費用。
2. 透過寫入控制降低寫入 (Writes) 費用。
3. 透過資料結構優化，在不影響效能的情況下節省營運預算。

## 核心策略說明

### 1. 利用前端快取與狀態管理 (Caching & State Management)

頻繁的畫面跳轉往往會觸發重複的讀取，這在 Standard Edition 這種按次計費的模式下非常昂貴。

- **使用 TanStack Query (React Query)**：設定適當的 `staleTime`（例如 5 分鐘）。當使用者短時間內重複瀏覽相同資料時，程式會直接從記憶體快取中讀取，而不會觸發 Firestore 的 `getDoc()`。
- **本地快取機制 (Persistence)**：開啟 Firestore SDK 的離線存取功能。SDK 會優先從本地 IndexedDB 讀取資料，只有在資料有變動或快取失效時才向雲端請求。

### 2. 寫入優化：防抖與節流 (Debouncing & Throttling)

如果你的應用程式有「即時儲存」功能（例如編輯醫事文件或草稿），應避免每打一個字就送出一次更新。

- **Debounce 寫入**：等到使用者停止輸入（例如 2 秒後）再執行寫入操作。
- **批次處理 (Batch Writes)**：如果需要同時更新多個文件，使用 `writeBatch()`。這能減少網絡往返並優化 Enterprise 版的寫入單位分配。

### 3. 資料結構去正規化 (Denormalization)

在 NoSQL 資料庫中，我們應以空間換取金錢。

- **合併小型文件**：如果你有許多小型設定檔，與其分 10 次讀取，不如將它們合併成一個大型文件（Standard 限制 1MB）。
- **冗餘欄位**：例如在「文章」文件中直接存儲「作者姓名」，而不是每次讀文章後還要再去讀「使用者」集合。

### 4. 善用聚合查詢 (Aggregation Queries)

如果您只需要計算總數（如病歷數量），絕對不要把所有文件抓下來。

- **使用 count()**：在 Standard 版中，每 1000 個匹配的文件僅收費 1 次讀取。
- **Enterprise 優勢**：聚合查詢按掃描位元組計費，對大型資料集的統計通常比 Standard 更划算。

### 5. 精確的分頁與索引優化

- **禁用 Offset**：永遠使用 `startAfter()` 游標分頁。
- **索引豁免 (Index Exemptions)**：對於不需要搜尋的高頻率寫入欄位（如長字串），手動在 GCP 控制台關閉索引。這能直接降低寫入時產生的「索引扇出 (Index Fanout)」成本。

## 優化策略總結表

| 方法                 | 節省對象      | 實作難度 | 核心邏輯                             |
| :------------------- | :------------ | :------- | :----------------------------------- |
| **TanStack Query**   | 讀取 (Reads)  | 低       | 將資料保留在記憶體，避免重複請求。   |
| **Debounce**         | 寫入 (Writes) | 中       | 減少高頻率的更新操作。               |
| **Data Flattening**  | 讀取 (Reads)  | 高       | 將多個小文件合併為大文件，一次讀完。 |
| **Index Exemptions** | 寫入 (Writes) | 中       | 減少寫入時連帶產生的隱形成本。       |

## 常見問題 Q&A

### Q1：合併文件會不會讓讀取變慢？

**答：** 只要文件總大小在幾百 KB 內，網路傳輸時間的增加通常可以忽略，但能幫你省下 10 倍的讀取費用。

## 延伸閱讀

- [Optimize Firestore Costs](https://firebase.google.com/docs/firestore/storage-size)
