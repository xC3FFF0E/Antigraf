<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Antigraf 圖示：綠色底色上戴月桂冠的側臉銅版畫">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.zh.md">简体中文</a> ·
  <b>繁體中文</b> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt.md">Português</a>
</p>

<p align="center">
  <b>源自希臘語 <i>antígrafo</i>（αντίγραφο）：回應原件的複製品。</b><br>
  給 AI 編程智能體的複製、克隆與調研技能。<br>
  它先研究來源，再建立你自己的版本，
  並用可以重複執行的命令<b>證明</b>兩者有多接近。
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="46 scripts, no installs" src="https://img.shields.io/badge/scripts-46%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">

  <img alt="Antigraf skill" src="https://img.shields.io/badge/skill-antigraf-1f883d?style=flat-square">
  <img alt="License: Apache-2.0 or MIT" src="https://img.shields.io/badge/license-Apache--2.0%20or%20MIT-2d81ff?style=flat-square">
</p>

<p align="center">
  <a href="#運作方式">運作方式</a> ·
<a href="#四項工作">四項工作</a> ·
<a href="#與眾不同之處">與眾不同之處</a> ·
<a href="#各部分在哪裡">各部分在哪裡</a> ·
<a href="#安裝">安裝</a> ·
<a href="#使用方法">使用方法</a> ·
<a href="#常見問題">常見問題</a> ·
<a href="#真實狀態">真實狀態</a> ·
<a href="#授權條款">授權條款</a> ·
<a href="#貢獻與安全">貢獻與安全</a> ·
<a href="#我們不越過的線">我們不越過的線</a>
</p>

<br>

Antigraf 以一份說明文件加一套小工具的形式，住在你的代理裡。它會走遍一個網站、手機應用或遊戲，把每個部分記錄成數字，建立你自己的版本，然後讓兩邊回答同一套檢查，直到沒有失敗，也沒有未知。

重點不是宣稱「看起來一樣」，而是指出仍然不同的那一行，以及顯示它的那條命令。

<br>

<b>直白地說：</b>Antigraf 是給 AI 編程智能體的 1:1 複製技能。用它克隆網站、複製網頁應用或遊戲、把設計重做成你自己的，或從介面到內部研究一個站點是怎麼搭起來的。它涵蓋整套頁面，不只是首頁：每條路由、每個區塊、控制項、展開後的狀態、動畫、手機版面、離線行為與 3D 場景，都各自與原站對比，並且在相符之前鎖住 100%。

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>研究任何東西</h3>
      頁面、螢幕、選單、控制項，以及點擊之後藏著的東西。每個數字都帶著它的來源，猜測無法冒充測量。
    </td>
    <td width="25%" valign="top">
      <h3>建立你自己的版本</h3>
      副本放在你的專案裡，用你選擇的技術組合。除了你有權使用的東西，原件不會隨之帶走任何內容。
    </td>
    <td width="25%" valign="top">
      <h3>驗證，而非猜測</h3>
      每一輪 27 項檢查在兩邊同時執行。沒有執行、或回答未知的檢查會阻止鎖定，絕不算通過。
    </td>
    <td width="25%" valign="top">
      <h3>面向代理</h3>
      一份技能檔案加普通腳本，任何模型、任何環境都能驅動同一套檢查。測量不需要 AI。
    </td>
  </tr>
</table>

<br>

## 運作方式

指定一個目標，選擇一項工作，然後分五個階段推進：

1. **研究**：走遍目標，打開點擊之後隱藏的內容，記錄成數字。
2. **計畫**：每個頁面、區塊、控制項、狀態和路徑各佔一行，並寫好判定它的檢查。
3. **建立**：先做前端。伺服器端部分只列出，不複製。
4. **比對**：同一套檢查在原件和你的副本上，反覆執行。
5. **打磨**：每一行失敗作為下一條建立指令返回，直到鎖定閉合。

## 四項工作

`/antigraf` 在做任何事之前只問一個問題。

| # | 工作 | 內容 |
|---|---|---|
| **1** | **複製** | 一比一複製。不再問任何問題，目標鎖定為 100%。 |
| **2** | **再造** | 作為你自己的版本複製。它會問你要改什麼：配色、品牌、圖示、文案。 |
| **3** | **改進** | 把目標與你的專案並排比較，指出對方更好的地方，並以簡短的下一步清單作結。 |
| **4** | **研究** | 唯讀，不執行任何東西，敏感資訊隱去。從前端到後端，它是用什麼做成的。 |

每項工作結束時都會給出按領域拆分的 1 至 100 的真實表格、拖住各領域的原因，以及接下來可選的方案。

## 與眾不同之處

| | **Antigraf** | 常見的複製技能 |
|---|---|---|
| 執行環境 | 任何環境、任何模型。只用 Python 3 與 Node 標準庫 | 綁定在某個代理迴圈 |
| 如何判定「完成」 | 27 項檢查，各有自己的結束碼，每輪全部執行 | 模型說看起來像 |
| 「未比較」 | 一律阻止鎖定 | 常被算作通過 |
| 你接受的差異 | 只能由你寫下，絕不會被悄悄抹掉 | 未被建模 |
| 大型任務 | 拆成分線，最多 3 個幫手，60 分鐘過期規則 | 單一長跑逐漸失準 |
| 對自身的說法 | 由真實執行記錄產生的進度區塊 | 頁面寫什麼就是什麼 |

不會用總分掩蓋哪一行失敗。圖片本身永遠不能通過任何檢查。較弱的模型，或看不見圖片的模型，絕不會降低標準，只會花得更少並如實說明。

## 各部分在哪裡

| 路徑 | 內容 |
|---|---|
| `skills/antigraf/SKILL.md` | 技能本體：任務、階段、層級、工作區、回合、規則 |
| `skills/antigraf/README.md` | 完整文件：檢查項目、容差、進度、目錄 |
| `skills/antigraf/references/` | 12 份指南：檢查項目、計畫、還原度、場景、交接、證據 |
| `skills/antigraf/scripts/` | 46 個工具：39 個 Python、7 個瀏覽器、1 份裝置清單 |
| `assets/` | 圖示，512 與 128 像素 |

這頁說明它承諾什麼，完整文件說明每項檢查的準確容差。

## 安裝

沒有套件管理器，沒有 `pip install`，沒有帳號。它只是一個檔案加普通腳本的資料夾。

**方式 1：複製資料夾（建議）**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

然後把 `Antigraf/skills/antigraf/` 移到你的代理讀取技能的目錄。名字不變，`SKILL.md` 仍在頂部，`references/` 與 `scripts/` 一併帶走。

| 環境 | 資料夾放在哪 |
|---|---|
| 專案自己的技能資料夾 | `<你的專案>/.claude/skills/antigraf/` |
| 整台機器的所有專案 | `~/.claude/skills/antigraf/` |
| 其他 | 你的環境讀取技能的目錄 |

**方式 2：無法放入資料夾時**

把 `skills/antigraf/SKILL.md` 的內容貼到代理的自訂指令欄。技能只靠這段文字執行、沒有工具，檢查由模型手工完成，最後的表格會說明哪些是這樣做。

**方式 3：不用代理**

這些工具就是普通腳本。

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

需要：**Python 3.8 或更新**（僅標準庫），瀏覽器工具需要 **Node 18 或更新**，走遍與點擊需要 Chromium 系瀏覽器（Edge 或 Chrome）。每一項都是可選的：缺了就降一級，並在最後的表格中說明，而不是猜測。

## 使用方法

一行就夠：

```
/antigraf https://example.com
```

由此分六步推進。

| 步驟 | 會發生什麼 |
|---|---|
| **1. 問工作** | 1 複製、2 再造、3 改進、4 研究。在你回答之前什麼都不複製。 |
| **2. 只問必須問的** | 複製不再追問。再造問要改什麼，改進問你的專案與真正目的，研究問深度與重點。 |
| **3. 寫下你能看見的計畫** | 最多七步，用你自己的話，其中一步標為「在此停下」，存到磁碟，別的模型可從同一步接上。 |
| **4. 研究、計畫、建立、測量** | 同一套檢查在原件和副本上反覆執行。 |
| **5. 關閉差距** | 失敗的行作為下一條建立指令返回；原先通過而現在失敗的行會標為回退。 |
| **6. 給出表格** | 八個領域，各按 100 計分，並指出拖住它的原因，然後給出選項。 |

最後的表格長這樣，由記錄計算得出，絕不是模型手打的：

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  -----------------------------------
Words & layout           100%     3     0        0
Design, icons             50%     1     1        0  failing: G4 contrast
Behaviour, flows           0%     0     0        5  not measured: G6, G7, G23, G24, G19
Phone & PWA                0%     0     1        1  failing: G14 tap targets
Motion & 3D               33%     1     0        2  not measured: G25, G26
Media & speed            100%     2     0        0
Sources, repairs          50%     2     0        2  not measured: G22, G16
Evidence, proof, pages    60%     3     1        1  failing: G12
```

沒有執行、或回答未知的檢查計為 **零分**，所以總分絕不會替副本說好話。每項工作都以這張表與三種提議結束：繼續推進、以簽署的豁免接受差異、或者停下。

鎖定只在 **100%** 時閉合：每一行通過、沒有任何未知、沒有無法解釋的差異。在此之前，表格會按檢查與行列出仍然敞開的項，例如 `G5 @1440 hero pad 16 12 -4 +-4`。

## 常見問題

**能複製整個站點，還是只有首頁？**
它會跟隨所有同站連結，把每個頁面記錄在三種寬度、手機與平板上。沒走到的頁面、沒按過的控制項都會記為「未探查」，並鎖住結果。你隨時看得到數量：找到的頁面與走過的頁面。

**會給我原站的原始碼嗎？**
不會。它測量原站，你用自己選的技術寫出自己的版本。交付的是你的程式碼，不是對方程式碼的翻版。

**看不見圖片的模型也能用嗎？**
可以。設計以數字傳遞：尺寸、顏色、間距、字級、可點擊範圍。圖片只用來對比，不用來學習，所以純文字的模型也能照測量值建構。

**它拒絕複製什麼？**
伺服器端邏輯、憑證、工作階段權杖、支付與帳務資料。遇到這類欄位會立即停止，並寫進 `HANDOVER.md`，讓你清楚知道自己要接上什麼。

**我怎麼知道它真的做到了？**
每項檢查都會寫一個帶退出碼的檔案，最後的表格由這些紀錄算出來。沒跑過的、或回答「未知」的，直接算零分。模型不能自己填分數。

**它能處理哪些類型的來源？**
網站與多頁網頁應用、手機優先的應用與 PWA 行為、帶播放器的串流介面、商店與目錄、文件站，以及包含繪製呼叫、著色器與運動的 3D 場景。

**執行它需要什麼？**
Python 3.8 以上（只用標準庫）、瀏覽器工具需要 Node 18 以上，以及 Chromium 系瀏覽器。不用安裝套件，不用帳號，不用金鑰。

## 真實狀態

這裡刻意顯示兩個不同的數字：得分是各道檢查對一對真實原版與副本給出的結果，已證明的數量是通過全部檢查的配對數量。決定工具是否完成的是第二個。

**能力靠量測，不靠宣稱。** 下面每一道檢查都存在並可執行。真正通過的，與某一對目標的得分分開計數。

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 54.6% out of 100 - the three-page test pair (round 2)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 50% | 1 | 1 | 0 | failing: G4 |
| Behaviour, flows | 20% | 1 | 4 | 0 | failing: G6, G7, G23, G19 |
| Phone & PWA | 50% | 1 | 1 | 0 | failing: G18 |
| Motion & 3D | 33% | 1 | 2 | 0 | failing: G25, G26 |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Sources, repairs | 50% | 2 | 1 | 1 | failing: G16 |
| Evidence, proof, pages | 40% | 2 | 3 | 0 | failing: G1, G11, G12 |
| **Total** | **54.6%** | 13 | 13 | 1 | 14 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### 逐項檢查的主張

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates  ·  0 proven on a real original-to-copy pair  ·  1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | measured | the three-page test pair round 2 |
| Icons and pictures, one partner each | G8, G17 | measured | the three-page test pair round 2 |
| Every page walked, planned and shipped | G11 | measured | the three-page test pair round 2 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | the three-page test pair round 2 |
| States: hover, focus, open, empty, error | G6 | measured | the three-page test pair round 2 |
| Motion: durations, easings, scroll | G13 | measured | the three-page test pair round 2 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | the three-page test pair round 2 |
| Speed and weight budgets | G15 | measured | the three-page test pair round 2 |
| Logic: same input, same answer, no secrets | G19 | measured | the three-page test pair round 2 |
| Defects found, and the copy repaired | G20, G21 | measured | the three-page test pair round 2 |
| 3D scene read as numbers | G25 | measured | the three-page test pair round 2 |
| 3D motion compared frame by frame | G26 | measured | the three-page test pair round 2 |
| Server seams listed for you to hook up | G16 | measured | the three-page test pair round 2 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | the three-page test pair round 2 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| the three-page test pair | unknown | round 2 | 13 of 27 | 13 | 0 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->



**測量的一半能用。建立的一半還沒有做出過通過全部檢查的副本。**

完整文件中的進度區塊由磁碟上的記錄寫成，從不手寫。目前是 27 項檢查，在真實的原件與副本組合上已證實的為 0。我們寧可給你一個零和原因，也不要一個百和謊言。

## 授權條款

兩種授權任選其一：**Apache License 2.0**（[LICENSE-APACHE](LICENSE-APACHE)）或 **MIT**（[LICENSE-MIT](LICENSE-MIT)）。簡要說明以及授權不涵蓋的範圍見 [LICENSE.md](LICENSE.md)。圖示與名稱歸本專案所有；只要註明是分支（fork），即可自由分叉。

## 貢獻與安全

如何提出變更，以及唯一重要的規則（新的檢查必須先展示失敗），在 [CONTRIBUTING.md](CONTRIBUTING.md)。如何私下回報漏洞，以及 Antigraf 保護你免於什麼、不保護什麼，在 [SECURITY.md](SECURITY.md)。

## 我們不越過的線

Antigraf 複製的是頁面在瀏覽器裡的外觀與行為。它**不複製**伺服器端邏輯、憑證、工作階段權杖、支付或會計資料；一旦發現形似這類欄位，它會停下並拒絕。這些內容會寫入 `HANDOVER.md`，讓你清楚知道該在自己的後端接上什麼，合法地、按你的條件進行。

**我們不縱容盜版、帳號共享、繞過付費牆、DRM 或登入、抓取私人資料，或在未經許可的情況下複製他人的內容、品牌或素材。** 請把 Antigraf 用在你擁有的、公開授權的、或你有權研究的東西上。你沒有權利的圖像、字型、標誌與文案，會被替換成你自己的；沒人清理的授權會一直阻止鎖定，直到你清理或替換為止。

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf。給 AI 編程智能體的複製、克隆與調研技能。</sub>
</p>
