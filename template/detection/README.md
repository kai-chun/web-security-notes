# Detection

這個 lab 的「藍隊視角」：假設攻擊已經發生，防禦方要怎麼**從 log / 流量看見它**。

與 `exploits/`（紅隊：怎麼打）成對存在，形成 purple team 閉環——
偵測規則要能抓到 `exploits/` 裡那支 PoC 產生的流量。

## 內容

- `*.yml` — [Sigma](https://github.com/SigmaHQ/sigma) 格式偵測規則（log-based，跨語言）
- `sample-logs/` —（可選）攻擊發生時的 log 樣本，用來驗證規則命中

## Log source

- Python app：`{說明 log 從哪來、長什麼樣}`
- Go app：`{說明 log 從哪來、長什麼樣}`

## 誤報邊界

`{為什麼不能只用最粗的字串比對？正常流量會不會誤觸？如何收斂}`

## 驗證方式

```
1. 跑 exploits/ 的 PoC 打 vulnerable_app
2. 收集 log
3. 用規則比對，確認命中；再用正常登入流量確認不誤報
```
