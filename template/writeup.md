# {Category} #{Number}: {Title}
 
> {Source}: [Title](URL)
>
> 解題日期：YYYY-MM-DD
> 難度：Apprentice / Practitioner
> 分類：{Category}
 
---
 
## TL;DR
 

 
## 1. 漏洞本質（Why）
- Root cause：
- 觸發條件：
- 為什麼這段程式碼會出問題：

## 2. 攻擊者視角（How）
### 偵察
- 發現點：{哪個參數／endpoint，怎麼判斷有漏洞}

### 重現步驟
1. 
2. 
3. 

### 關鍵 Payload
\`\`\`http
{Request/Response 片段}
\`\`\`

### 結果
- 取得：

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
