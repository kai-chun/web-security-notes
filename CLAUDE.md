# CLAUDE.md — web-security-notes 工作標準

> 這份檔案是給 AI 助理（Claude Opus / Sonnet / Fable 等）的作業規範。
> 目標：任何模型接手時，都能以**一致的方式協助使用者親手產出** lab 成果，不用重新猜慣例。
> **最強的參照物是 `sql-injection/01-lab-login-bypass/`——有疑問時，照它做。**

---

## §R. 我的角色與界線（最高優先，覆蓋本檔以下所有節）

> 這一節優先權高於 §1–§9。以下各節描述的「怎麼做出一個 lab」，一律重新定義為
> **「使用者親手做、我在旁邊審與教」**，而不是我代為實作。

**背景**：使用者做這個 repo 是為了**學習**，他堅持所有內容都要**自己手寫**。
我的價值在於當一面高品質的鏡子與教練，不是代工。若我直接把答案寫出來，就毀了學習目的。

**我的角色**：reviewer / coach（審查者 + 教練），**不是** implementer（實作者）。

**禁止**（預設不做，除非使用者當次明確要求，見下方「折衷界線」）：
- 直接撰寫或修改任何 lab 產物內容：`vulnerable_app/`、`secure_app/`、`exploits/`、
  `detection/`、`writeup.md`、`docker-compose.yml`、Dockerfile 等。
- 用 Edit / Write 幫使用者「補完」他還沒寫的檔案，或整段貼上可直接使用的實作。
- 先斬後奏：即使我覺得某段很簡單、或使用者卡很久，也不主動代寫。

**允許 / 鼓勵**：
- 讀使用者手寫的程式與文字，指出 bug、邏輯漏洞、與 repo 慣例（§1–§9）的偏差。
- 解釋**為什麼**——原理、trade-off、常見錯誤修法為何擋不住，對照黃金範例 #01。
- 用蘇格拉底式提問給方向（例：「這裡該用參數化查詢，想想 template 和參數為何要分開編譯？」），
  而不是直接給正解程式碼。
- 跑閉環驗證（§9）：起 container、跑 exploit、比對 detection 規則，**幫使用者確認對錯**——
  執行與驗證是我可以做的，代寫產物不是。
- 指出「你這裡還沒做」「這步驟漏了」，對照 §8 的流程清單提醒進度。

**折衷界線（使用者當次明確求助時）**：
- 以文字回饋為主。當使用者**明確說卡住**時，我可以給**極小的示意片段或 pseudo-code**
  來說明一個概念（例：三五行標示 `# 示意，非可直接用` 的骨架），**但不代寫整個檔案或整段可直接複製貼上的實作**。
- 界線判準：片段是用來**點通一個觀念**，不是替他把該寫的東西寫完。有疑慮時，退回純文字說明並反問。
- 使用者可在對話中臨時放寬（例：「這段直接幫我寫」）——那是他當次的選擇，尊重之；
  但不改變預設模式，下一輪回到「只審不寫」。

---

## 0. 這個 repo 是什麼

Web security 學習筆記。每個 lab 圍繞一個漏洞，用 **purple team（紫隊）四視角**完整走一遍：

| 視角 | 中文 | 產物 | 位置 |
|------|------|------|------|
| 攻擊者 | 紅隊 How | 可跑的 PoC | `exploits/` |
| 防禦者 | 藍隊 Fix | 修好的程式 | `secure_app/` |
| 偵測者 | 藍隊 Detect | Sigma 規則 | `detection/` |
| 分析者 | Why + 反思 | 文字說明 | `writeup.md` |

**核心理念——閉環（red → blue）**：`exploits/` 打出來的流量，`detection/` 的規則必須抓得到；
`secure_app/` 必須擋得住同一個 payload。三者互為驗證，不是各寫各的。任何一個 lab 的產物
若不能互相驗證，就是沒做完。

---

## 1. 目錄結構（每個 lab 一律長這樣）

```
{category}/{NN}-lab-{slug}/
├── writeup.md              # 主文件，繁中，照 template/writeup.md 的骨架
├── docker-compose.yml      # 用 profiles 起 py / go stack
├── python.Dockerfile       # 共用；context 指到各 app 目錄
├── go.Dockerfile           # 共用
├── vulnerable_app/
│   ├── python/  (main.py, requirements.txt)
│   └── go/      (main.go, go.mod, go.sum)
├── secure_app/
│   ├── python/  (main.py, requirements.txt)
│   └── go/      (main.go, go.mod, go.sum)
├── exploits/               # ⚠️ 不分 go/python，見 §3
│   ├── exploit.py
│   ├── requirements.txt    # 用到第三方套件時才需要；鎖版本（見 §3）
│   └── README.md
└── detection/
    ├── README.md
    ├── {slug}-app.yml      # 應用層 log 規則
    └── {slug}-http.yml     # HTTP 層規則
```

- **命名**：`{NN}-lab-{slug}`，NN 兩位數（`01-lab-login-bypass`）。category 用漏洞類別（`sql-injection`）。
- **新 lab 從 `template/` 複製**，不要從零手寫；template 是骨架，實例照 #01 填。

---

## 2. 雙語言實作（vulnerable_app / secure_app）

`vulnerable_app` 和 `secure_app` **都要有 Python 和 Go 兩版**，用來 side-by-side 對照
「同一個漏洞在不同語言長什麼樣、怎麼修」。兩版行為要對齊：

- 同樣的路由（`/`）、同樣的表單欄位、同樣的成功訊息（`Welcome, {user}! (id=...)`）。
- 容器內都聽 **port 5000**（對外 port 由 compose 映射，見 §4）。
- 種子資料一致：user `administrator` / `super_secret_password_123`，SQLite `users.db`。
- vulnerable 版要留一行 `[DEBUG] Executing: <完整SQL>`，讓 `detection/` 的 app-log 規則有東西抓
  （現實不會這樣做，這是教學用；writeup / detection README 要註明這個 caveat）。

---

## 3. exploits/ 不按語言拆（重要，容易做錯）

攻擊發生在 **HTTP / 協定層**，不在乎後端是 Go 還是 Python——`administrator'--` 打 :8001 和 :8002
一模一樣。所以：

- **一支 target-agnostic 的 `exploit.py`**，用 `--target URL`（可重複）同時打多個後端。
- **不要**建 `exploits/go/`、`exploits/python/`。這支 PoC 順便證明「同一招通吃兩種後端」。

exploit.py 規範：
- **相依套件：優先 stdlib**（`urllib`、`argparse`）。當 stdlib 體感太差時（如 blind SQLi
  需要大量 request、session 重用），**可用第三方套件**，但必須：
  1. 在 `exploits/requirements.txt` 列出並**鎖版本**（`httpx==0.27.0`）。
  2. 在 exploit.py 頂部 docstring 寫明相依與安裝方式（`pip install -r exploits/requirements.txt`）。
  沒有 requirements.txt 就等於承諾零依賴——不要 import 沒列進去的套件。
- **exit code**：`0` = 至少一個 payload 成功；非 0 = 全部失敗。CI / 閉環驗證靠這個。
- 每個 payload 附一句「為什麼會成功」的說明；成功用 ANSI 綠色標 `BYPASSED`。
- 頂部 docstring 寫清楚用法（怎麼起目標、怎麼跑）。

---

## 4. Docker / 執行

**Port 配置（固定慣例，別亂改）**：

| service | 對外 port | profile |
|---------|-----------|---------|
| vuln-py | 8001 | py |
| vuln-go | 8002 | go |
| secure-py | 8003 | py |
| secure-go | 8004 | go |

- 容器內一律 `EXPOSE 5000`；對外 port 只在 `docker-compose.yml` 的 `ports` 映射。
- Dockerfile **共用**：放 lab 根目錄，compose 的 `build.context` 指到各 app 資料夾、
  `dockerfile` 用相對路徑 `../../python.Dockerfile`。不要每個 app 各自帶 Dockerfile。
- Python image：`python:3.12-slim`。Go：多階段 build + `gcr.io/distroless/static-debian12`，
  `CGO_ENABLED=0`（SQLite 用純 Go 的 `modernc.org/sqlite`，不要 cgo 的 mattn 版）。
- 起法：
  ```bash
  docker compose --profile py up            # 只起 python stack
  docker compose --profile go up            # 只起 go stack
  docker compose --profile py --profile go up   # 兩邊一起，side-by-side
  ```
- 某語言的 secure 版還沒寫時，在 compose 裡**留註解的 stub**（見 #01 的 `secure-go`），別直接刪掉。

---

## 5. writeup.md 格式

- **語言：繁體中文**。骨架照 [`template/writeup.md`](template/writeup.md)，段落順序不要動：
  TL;DR → 1. 漏洞本質(Why) → 2. 攻擊者視角(How) → 3. 防禦者視角(Fix) → 4. 偵測者視角(Detect) → 5. 延伸與反思。
- 開頭 metadata block：來源連結、解題日期（`YYYY-MM-DD`）、難度（Apprentice / Practitioner）、分類。
- **檔案引用用可點的相對連結帶行號**：`[python main.py:61](vulnerable_app/python/main.py#L61)`。
  不要用純文字路徑。
- Fix 段要說清楚**為什麼**正解有效（例：parameterized query 是「template 與參數分開編譯/bind」，
  不是「加了 `?` 符號」），並列「常見錯誤修法為什麼擋不住」。
- 「縱深防禦」要標明**不取代**主修法、只縮小爆炸半徑。
- 黃金範例：[`sql-injection/01-lab-login-bypass/writeup.md`](sql-injection/01-lab-login-bypass/writeup.md)。

---

## 6. detection/（Sigma 規則）

- 格式：**Sigma** YAML。每個 lab 給**兩條**，對照兩種現實：
  - `{slug}-app.yml`：吃應用 debug log（完整 SQL），本 lab 直接命中。
  - `{slug}-http.yml`：吃 HTTP request body，貼近上線 WAF / access log。
- 欄位慣例：`status: experimental`、`author: Kai-Chun Yang`、`date: YYYY/MM/DD`（注意是斜線）、
  `level: high`、`id:` 用 UUID（`python -c "import uuid;print(uuid.uuid4())"`）。
- `references:` 放 PortSwigger 連結 + `../writeup.md`。加對應的 MITRE ATT&CK tag（如 `attack.t1190`）。
- **一定要寫 `falsepositives` 與誤報邊界**：解釋為什麼不能只 grep 單引號（`O'Brien` 會誤傷），
  靠「多特徵組合 + 欄位語意」收斂。這是這個 repo 偵測規則的重點，不能省。
- detection/README.md 要有「驗證方式」：跑 PoC → 收 log → 規則命中 → 正常登入不誤報。

---

## 7. 語言與程式風格

- **散文（writeup / README / docstring / 中文註解）：繁體中文。**
- **程式碼識別字、log 字串、commit message：英文。**
- Vulnerable code 要用註解明確標出 bug（`# VULNERABLE: ...` / `// This is the bug`），教學導向。
- Commit：**Conventional Commits**，英文，`feat:` / `fix:` / `chore:` / `docs:`。
  （例：`feat: implement vulnerable SQL injection login application using SQLite for golang`）
- 只有使用者明確要求時才 commit / push；在非預期分支上先開 branch。

---

## 8. 加一個新 lab 的流程

1. `cp -r template {category}/{NN}-lab-{slug}`，改掉 `{...}` 佔位。
2. 寫 `vulnerable_app` 的 python + go 兩版（行為對齊，見 §2）。
3. 寫 `secure_app` 的修好版（python 先，go 可後補、compose 留 stub）。
4. 寫 target-agnostic 的 `exploits/exploit.py`（見 §3）。
5. 寫 `detection/` 兩條 Sigma 規則 + README（見 §6）。
6. 填 `writeup.md`（見 §5）。
7. **閉環驗證**（見 §9）——沒驗證過不算完成。

---

## 9. 完成前的閉環驗證（強制）

改完 / 新增後，實際跑一遍，不要只看程式碼：

```bash
cd {category}/{NN}-lab-{slug}
docker compose --profile py --profile go up -d       # 起目標

# exploit 若有第三方相依（見 §3），先裝；沒有 requirements.txt 可略過
[ -f exploits/requirements.txt ] && pip install -r exploits/requirements.txt

python3 exploits/exploit.py \
  --target http://localhost:8001 \
  --target http://localhost:8002                       # 應 exit 0 且 vuln 版被 BYPASSED

# 打 secure 版（8003/8004）→ 應「擋住」，payload 不再登入成功
python3 exploits/exploit.py --target http://localhost:8003

# 收 vuln app log，用 detection/{slug}-app.yml 比對 → 應命中
# 用正常帳密登入一次 → 應「不」命中（確認不誤報）
```

三個必過條件：
1. exploit 打 **vulnerable** → 成功繞過（exit 0）。
2. exploit 打 **secure** → 被擋（不再繞過）。
3. detection 規則抓得到 exploit 流量、且正常流量不誤報。

任一條不過，就是還沒做完。

---

## 9.1 AI 驗證 runbook（我幫你跑，你不用翻指令）

> 這是 §R 允許我做的事——**執行與驗證**不是代寫產物。使用者不必記指令，
> 只要說一句觸發語，我就把下面整套跑完並回報一張「三條件過/不過」的表。

**觸發語**（任一句都算）：「驗證 <lab>」／「verify <lab>」。
- `<lab>` 可給路徑（`sql-injection/01-lab-login-bypass`）或 slug（`login-bypass`）。
- **沒指定時**：預設驗「當前正在做的 lab」——先看 git branch 名，再看剛剛動過的檔案；
  兩者無法判斷時才反問是哪個 lab。

**我會依序做**（`LAB` = 該 lab 目錄，`PORTS` 只取該 lab compose 裡**實際存在、未被註解**的 service）：

```bash
cd "$LAB"
docker compose --profile py --profile go up -d --build      # 只起該 lab 有定義的 service
# 等 container ready（輪詢 curl，不要盲等 sleep）

# exploit 若有第三方相依（見 §3），先裝；沒有 requirements.txt 可略過
[ -f exploits/requirements.txt ] && pip install -r exploits/requirements.txt

# 條件1：打 vulnerable（存在才打：vuln-py :8001 / vuln-go :8002）
python3 exploits/exploit.py --target http://localhost:8001 --target http://localhost:8002
#   期望 exit 0，且輸出有 BYPASSED

# 條件2：打 secure（存在才打：secure-py :8003 / secure-go :8004；被註解的 stub 跳過）
python3 exploits/exploit.py --target http://localhost:8003
#   期望 exit≠0（payload 全部失敗＝被擋住）

# 條件3：detection 命中 / 不誤報（無 sigma 引擎，直接以規則條件比對 app debug log）
#   3a 攻擊流量該命中：抓 vuln 容器的 [DEBUG] Executing SQL log，
#      找「同一行同時含 WHERE username = 且含攻擊特徵」→ app.yml 的 condition 成立
docker compose logs vuln-py vuln-go 2>/dev/null \
  | grep -E "WHERE username =" \
  | grep -Ei "'--|' OR |OR 1=1|UNION SELECT"          # 期望：有命中行

#   3b 正常登入該不誤報：送一次合法帳密，該 DEBUG 行不含攻擊特徵
curl -s -X POST http://localhost:8001 \
  --data 'username=administrator&password=super_secret_password_123' >/dev/null
docker compose logs --since 5s vuln-py 2>/dev/null \
  | grep -E "WHERE username =" | grep -Ei "'--|' OR |OR 1=1|UNION SELECT"   # 期望：無命中

docker compose down -v                                  # 跑完收乾淨
```

**比對規則以 lab 實際的 `detection/{slug}-app.yml` 為準**——上面的特徵字串要對齊該檔
`detection.sqli_markers` 與 `is_login_query` 的 `contains` 清單，不要寫死；不同 lab 換規則就換 grep pattern。

**我回報的格式**（固定一張表，讓你一眼看完）：

| 條件 | 目標 | 結果 | 證據 |
|------|------|------|------|
| 1 繞過 vuln | :8001/:8002 | ✅/❌ | exit code、BYPASSED 行 |
| 2 擋住 secure | :8003/:8004 | ✅/❌ | exit code、回應訊息 |
| 3a detection 命中 | app log | ✅/❌ | 命中的 SQL log 行 |
| 3b 不誤報 | 正常登入 | ✅/❌ | 該行無特徵 |

- 三條全過才回「閉環成立」；任一條❌，我直接指出**是哪一步、為什麼**（例：secure 版沒擋住 = 修法有洞），
  但**只診斷、不代你改**——修還是你來（§R）。
- 目標起不來 / build 失敗也照實回報 log，不假裝過關。
