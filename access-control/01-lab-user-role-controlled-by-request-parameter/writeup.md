# Access Control #01: User role controlled by request parameter

> {Source}: [User role controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter)
>
> 解題日期：2026-08-14
> 難度：Practitioner
> 分類：Access Control

---

## TL;DR

## 1. 漏洞本質（Why）

- Root cause：誤信使用者端傳入的參數 (Cookie - Admin field)，沒有在後端做權限檢查。
- 觸發條件：將 Cookie 中的 Admin 欄位改成 true，後端就會認為使用者是管理員。
- 為什麼這段程式碼會出問題：

## 2. 攻擊者視角（How）

### 偵察

- 發現點：登入一般使用者帳號後，發現 Cookie 中有一個 Admin 欄位，值為 false。

### 重現步驟

1. 登入一般使用者帳號，發現 Cookie 中有一個 Admin 欄位，值為 false
2. 修改角色 Cookie Admin 欄位為 true
3. 確定已拿取到 admin 權限，進入 /admin 頁面，看到 admin 專屬內容
4. 透過 admin 權限，刪除目標使用者

### 關鍵 Payload

\`\`\`http
curl --location 'https://0a9c00020477ac1980bd26b500fa00f7.web-security-academy.net/admin' \
--header 'Cookie: Admin=true; session=eWUek6j1Bcvf03Mq1r0irSoSmh1S8LeP'
\`\`\`

### 結果

- 取得：admin 權限，刪除目標使用者

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
