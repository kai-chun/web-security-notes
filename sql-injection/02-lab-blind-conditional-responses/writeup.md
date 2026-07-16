# SQL Injection #02: Blind SQL injection with conditional responses
 
> PortSwigger Lab: [Blind SQL injection with conditional responses](https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses)
>
> 解題日期：2026-05-10
> 難度：Practitioner
> 分類：SQL Injection
 
---
 
## TL;DR

頁面使用追蹤 cookie 進行分析，並執行一個包含該 cookie 值的 SQL 查詢。這個 SQL 查詢不會回傳結果，也不會顯示任何錯誤訊息。但如果查詢成功，頁面上會顯示 "Welcome back" 訊息。透過這個 Blind SQL 注入漏洞取得資料庫中 users Table 的 username 和 password 的欄位值。

 
## 1. 漏洞本質（Why）
- **Root cause**：SQL 查詢沒有參數化，直接拼進查詢字串，導致攻擊者輸入的內容被當成 SQL 語法解析。
- **觸發條件**：
  - 具有可以控制的 input 跑進 SQL: `TrackingId` cookie 值被拿去查資料庫
  - 輸入沒有被處理過或是參數化
  - 可以從 "Welcome back" 訊息推測結果
- **為什麼這段程式碼會出問題**：
  ```python
  query = f"SELECT * FROM trackedUsers WHERE trackingId = 'abc123'"
  ```
  在後方加上 `' AND '1'='1` 便可代入任意查詢條件，並搭配 boolean 判斷來攻擊。

## 2. 攻擊者視角（How）
### 偵察
- 發現點：cookie query

### 重現步驟
1. cookie query 可以用來做 blind SQLi
2. 確認 ' and '1'='1' 可用 => 可以用來得知 true/false
3. 確認 users table 存在
4. 確認 username = administrator 存在
5. 用暴力法找出 length(password) 長度
6. 用暴力法找出 password 每個字元的值

### 關鍵 Payload
\`\`\`http
Cookie: TrackingId=TFYzlWqLrDp413AF' AND (SELECT SUBSTRING(password,n,1) from users)='a' ; session=vzZ9wJUBr2lLmAwIQTtYOxjGbnhBFUaX
\`\`\`

### 結果
- 取得：密碼

## 3. 防禦者視角（Fix）
- 正確寫法：
\`\`\`{language}
{修補後的程式碼}
\`\`\`
- 縱深防禦：{WAF / CSP / 最小權限 / 參數化查詢 ...}
- 常見錯誤修法（為什麼擋不住）：

## 4. 偵測者視角（Detect）
> 假設攻擊已發生，防禦方怎麼從 log / 流量看見它。規則放 [`detection/`](detection)，要抓得到 [`exploits/`](exploits) 的 PoC。
- Log source：{攻擊在哪一層留下痕跡、長什麼樣}
- 偵測特徵：{哪些字串 / 行為組合是訊號}
- 誤報邊界：{為什麼不能只用最粗的比對、如何收斂}
- 規則：{對標 Sigma，連到 detection/ 裡的檔案}

## 5. 延伸與反思
- 變形題：
- 相關 CVE / 真實案例：
- 我這次卡住的點：
- 下次要記得：
