# Detection

藍隊視角：有人透過 tracking cookie 注入攻擊，防禦方如何從 log 看見相對應的流量。

與 [../exploits/](../exploits) 成對存在，偵測規則要能抓到 `exploits/` 裡那支 PoC 產生的流量。

## Log source

兩支 vuln app 都會印出 debug SQL
- Python app：[python main.py:72](../vulnerable_app/python/main.py#L72)
- Go app：[go main.go](../vulnerable_app/go/main.go)、

```
[DEBUG] Executing: SELECT tracking_id FROM tracked_users WHERE tracking_id = 'TFYz...' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a'
```

> 現實中不會把完整 SQL 印進 log，blind-conditional-responses-app.yml 是用來模擬應用層的 log，真正的外部偵測點是 blind-conditional-responses-http.yml。
> 這裡兩條都給，是為了對照「有應用層 log」vs「只有 HTTP 層」兩種現實。

## 兩條規則

| 檔案 | 打哪一層 | 適用情境 |
|-----|----------|----------|
| blind-conditional-responses-app.yml | 應用 debug log (完整 SQL | 開發 / 本 lab 可直接命中) |
| blind-conditional-responses-http.yml | HTTP 請求的 Cookie header(cs-cookie) | 貼近上線 access log |

## 誤報邊界

合法 cookie 的 `tracking_id` 不可能含 `' AND ` / `(SELECT ...)` 這種 SQL 結構，所以誤報風險低。

## 驗證方式

```
1. docker compose --profile py up -d --build
2. 跑 exploits/exploit.py（或手動 curl --cookie "TrackingId=...' AND '1'='1"）
3. 收 app log，用 blind-conditional-responses-app.yml 比對 → 應命中
4. 收 http log，用 blind-conditional-responses-http.yml 比對 → 應命中
5. 送一次正常 cookie（合法 tracking_id）→ 應「不」命中
```
