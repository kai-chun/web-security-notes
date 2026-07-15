# SQL Injection #01: SQL injection vulnerability allowing login bypass
 
> PortSwigger Lab: [SQL injection vulnerability allowing login bypass](https://portswigger.net/web-security/sql-injection/lab-login-bypass)
>
> 解題日期：2026-04-29
> 難度：Apprentice
> 分類：SQL Injection
 
---
 
## TL;DR

登入表單把使用者輸入直接串進 SQL 字串，用 `administrator'--` 或 `' OR 1=1--` 當 username 把密碼檢查註解掉，繞過認證以 administrator 身份登入。

## 1. 漏洞本質（Why）

- **Root cause**：登入查詢用字串拼接（f-string / `+`）組 SQL，username/password 沒有經過 parameterized query 處理，使用者輸入會直接成為 SQL 語法的一部分。
- **觸發條件**：
  - 後端用字串拼接組 SQL
  - 錯誤訊息或登入結果可被觀察
- **為什麼這段程式碼會出問題**：
  ```python
  query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
  ```
  輸入 `administrator'--` 後，query 變成：
  ```sql
  SELECT * FROM users WHERE username = 'administrator'--' AND password = '...'
  ```
  `--` 之後全部被當成 SQL 註解，等同於：
  ```sql
  SELECT * FROM users WHERE username = 'administrator'
  ```
  密碼檢查整段消失，只要 username 存在就回傳該 row，登入成功。

## 2. 攻擊者視角（How）

### 偵察
- **發現點**：登入表單 username/password 欄位
- **判斷方式**：
  - 輸入單引號 `'` → 回傳 DB error（`Internal error`）→ 確定有 SQLi
  - 輸入 `' OR 1=1--` → 不報錯且能登入 → 確認可被注入

### 重現步驟
1. 在 username 欄位輸入 `'`，password 隨意 → 看到 SQL 錯誤訊息，確認注入點
2. username 改成 `administrator'--`，password 隨意 → 以 administrator 身份登入成功
3.（替代）username 用 `' OR 1=1--` → 登入為查詢回傳的第一個 user（依資料庫順序，通常也是 administrator）

### 關鍵 Payload
```
Username: administrator'--
Password: x
```

對應實際 SQL：
```sql
SELECT * FROM users WHERE username = 'administrator'--' AND password = 'x'
```

### 結果
- 取得：administrator 帳號的 session，完成 lab
- 影響等級：認證繞過 → 視該帳號權限可橫向擴展（資料外洩、權限提升等）

## 3. 防禦者視角（Fix）

- **正確寫法 — Parameterized Query / Prepared Statement**

  把使用者輸入交給 DB driver 當「資料」處理，而不是讓它變成 SQL 語法的一部分。

  ```python
  query = "SELECT * FROM users WHERE username = ? AND password = ?"
  user = conn.execute(query, (username, password)).fetchone()
  ```

  關鍵不是「`?` 這個符號」，而是 SQL template 在 driver 裡跟參數是**分開傳輸/分開解析**的——template 先送給 DB engine 編譯成 prepared plan，參數再 bind 進去；參數值無論長什麼樣都不會被當成 SQL token，`administrator'--` 整串只是個普通字串。

- **縱深防禦（不取代 #1，只是縮小爆炸半徑）**
  - **通用錯誤訊息**：不要把 code error 直接回給 client。攻擊者靠錯誤訊息推敲 schema 是 blind SQLi 之前的標準偵察動作。隱藏 Server-side log 細節，client 只能看到 `Login failed`。
  - **登入語意統一**：username 不存在 vs 密碼錯誤都回 `Invalid credentials`，避免成為帳號列舉（user enumeration）的副作用注入點。


## 4. 延伸與反思
- **變形題**：
- **相關真實案例**：
- **我這次卡住的點**：
- **下次要記得**：

