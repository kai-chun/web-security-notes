# Detection — SQLi Login Bypass

藍隊視角：有人用 `administrator'--` / `' OR 1=1--` 打登入表單時，防禦方**從 log 怎麼看見**。
與 [`../exploits/`](../exploits) 成對——這裡的規則要抓得到那支 PoC 打出來的流量。

## Log source

兩支 vulnerable app 都會輸出同一行（[go main.go:71](../vulnerable_app/go/main.go#L71)、
[python main.py:61](../vulnerable_app/python/main.py#L61)）：

```
[DEBUG] Executing: SELECT id, username FROM users WHERE username = 'administrator'--' AND password = 'x'
```

注入的 payload 直接內嵌在被執行的 SQL 裡，所以這行是最強的偵測訊號。

> ⚠️ 現實中你**不會**把完整 SQL 印進 log（那本身是資訊洩漏）。
> 真正上線的偵測點是 **WAF / access log 的 request body**，見 `sqli-login-bypass-http.yml`。
> 這裡兩條都給，是為了對照「有應用層 log」vs「只有 HTTP 層」兩種現實。

## 兩條規則

| 檔案 | 打哪一層 | 適用情境 |
|------|----------|----------|
| `sqli-login-bypass-app.yml`  | 應用 debug log（完整 SQL） | 開發 / 本 lab 可直接命中 |
| `sqli-login-bypass-http.yml` | HTTP request body（表單欄位） | 貼近上線環境的 WAF/access log |

## 誤報邊界（為什麼不能只 grep 單引號）

- 只比對 `'` → 任何名字含撇號的人（`O'Brien`）都會誤觸 → 不可用
- 收斂靠**組合特徵**：SQL 註解序列 `'--`、`' OR `、`' AND `、`UNION SELECT`、`1=1`，
  且**出現在 username/password 這種本不該有 SQL 語法的欄位**
- 密碼欄位理論上可以是任意字元 → 對 password 欄位要放寬、或改看「登入成功 + username 含 SQL meta 字元」的關聯

## 驗證方式

```
1. docker compose --profile go up            # 或 --profile py
2. 跑 exploits/ 的 PoC（或手動送 administrator'--）
3. 收集 app log，用 sqli-login-bypass-app.yml 比對 → 應命中
4. 用正常帳密登入一次 → 應「不」命中（確認不誤報）
```
