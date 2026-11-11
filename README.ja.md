<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Antigraf のアイコン: 緑のタイルに月桂冠をかぶった横顔の版画">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <a href="README.md">English</a> ·
  <b>日本語</b> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.zh-hant.md">繁體中文</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt.md">Português</a>
</p>

<p align="center">
  <b>ギリシャ語の <i>antígrafo</i>（αντίγραφο）から。原本に応える複製。</b><br>
  AI コーディングエージェントのための複製・クローン・調査スキル。<br>
  元のサイトを調べ、あなた自身の版を作り、
  <b>どれだけ近いかを</b>再実行できるコマンドで証明します。
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="48 scripts, no installs" src="https://img.shields.io/badge/scripts-48%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">

  <img alt="Antigraf skill" src="https://img.shields.io/badge/skill-antigraf-1f883d?style=flat-square">
  <img alt="License: Apache-2.0 or MIT" src="https://img.shields.io/badge/license-Apache--2.0%20or%20MIT-2d81ff?style=flat-square">
</p>

<p align="center">
  <a href="#仕組み">仕組み</a> ·
<a href="#四つの仕事">四つの仕事</a> ·
<a href="#他と違うところ">他と違うところ</a> ·
<a href="#どこに何があるか">どこに何があるか</a> ·
<a href="#導入">導入</a> ·
<a href="#使い方">使い方</a> ·
<a href="#よくある質問">よくある質問</a> ·
<a href="#正直な現状">正直な現状</a> ·
<a href="#ライセンス">ライセンス</a> ·
<a href="#貢献とセキュリティ">貢献とセキュリティ</a> ·
<a href="#越えない線">越えない線</a>
</p>

<br>

Antigraf は、指示書と小さな道具一式としてあなたのエージェントの中に入ります。ウェブサイト、スマホアプリ、ゲームをたどり、そのすべての部分を数値として書き留め、あなたの版を作り、両側に同じチェックを答えさせます。何も失敗せず、何も「不明」でなくなるまで続けます。

言いたいのは「見た目が同じ」ではありません。まだ違う行と、それを示すコマンドを見せることです。

<br>

<b>平たく言えば:</b> Antigraf は AI コーディングエージェント向けの 1:1 複製スキルです。ウェブサイトをクローンし、ウェブアプリやゲームを複製し、デザインを作り直し、サイトがどう作られているかを表から裏まで調べられます。見るのは最初の 1 ページだけではありません。すべてのルート、区画、操作、開いた状態、アニメーション、スマホ表示、オフライン動作、3D シーンを、それぞれ原本と比べ、一致するまで 100% のロックを開けません。

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>何でも調べる</h3>
      ページ、画面、メニュー、操作、クリックの先にあるものまで。数値には出どころが付くので、推測が測定のふりをできません。
    </td>
    <td width="25%" valign="top">
      <h3>自分の版を作る</h3>
      あなたの複製は、あなたのプロジェクトの中に、あなたが選んだ構成で入ります。使う権利のあるもの以外は原本から持ち込みません。
    </td>
    <td width="25%" valign="top">
      <h3>推測ではなく検証</h3>
      27 のチェックが毎回両側で走ります。実行されなかった、または「不明」と答えたチェックはロックを止め、合格にはなりません。
    </td>
    <td width="25%" valign="top">
      <h3>エージェント対応</h3>
      スキルファイルと素のスクリプトだけ。どのモデル、どの環境でも同じチェックを動かせます。測定に AI は要りません。
    </td>
  </tr>
</table>

<br>

## 仕組み

対象を指定し、仕事を選ぶと、五つの段階で進みます。

1. **調べる:** 対象をたどり、押した先に隠れているものまで開き、数値として記録します。
2. **計画する:** ページ、区画、操作、状態、経路ごとに一行を書き、それぞれを判定するチェックを決めます。
3. **作る:** まず画面から作ります。サーバー側は名指しするだけで、コピーはしません。
4. **照合する:** 同じチェックを原本とあなたの複製の両方で、回を重ねて走らせます。
5. **磨く:** 失敗した行は次の指示として戻り、ロックが閉じるまで繰り返します。

## 四つの仕事

`/antigraf` は何よりも先に一つだけ質問します。

| # | 仕事 | 内容 |
|---|---|---|
| **1** | **複製** | 1:1 で複製します。それ以上は何も聞かず、目標を 100% で固定します。 |
| **2** | **再構成** | 自分の版として作ります。色、ブランド、アイコン、文章など、何を変えるか聞きます。 |
| **3** | **改善** | 対象とあなたのプロジェクトを並べ、相手が優れている点を示し、次にやることを短くまとめます。 |
| **4** | **研究** | 読むだけ。何も実行せず、機密は伏せます。表から裏まで、何で動いているか。 |

どの仕事も、最後に領域ごとの正直な 1〜100 の表と、足を引っ張っているもの、次に何をするかの選択肢を出します。

## 他と違うところ

| | **Antigraf** | よくある複製スキル |
|---|---|---|
| 動く場所 | どの環境、どのモデルでも。Python 3 と Node、標準ライブラリのみ | 特定のエージェントに縛られる |
| 「完了」の決め方 | 27 のチェック、それぞれ終了コード付き、毎回すべて実行 | モデルが「合ってる」と言う |
| 「比較していない」 | 常にロックを止める | 合格として数えられることが多い |
| 受け入れた差 | あなただけが書ける。黙って消えることはない | 想定されていない |
| 大きな仕事 | レーンに分割、補助は最大 3 つ、60 分で古い作業は捨てる | 長い一回の実行が少しずつずれる |
| 自己申告 | 実際の記録から生成される進捗表 | ページに書いてあること |

全体の一つの点数で、どの行が失敗したかを隠しません。画像だけでは何も合格しません。弱いモデルや画像を見られないモデルは基準を下げません。使う量を減らして、そう言います。

## どこに何があるか

| パス | 内容 |
|---|---|
| `skills/antigraf/SKILL.md` | スキル本体: 仕事、段階、階層、作業場所、ラウンド、規則 |
| `skills/antigraf/README.md` | 完全な文書: チェック、許容差、進捗、配置 |
| `skills/antigraf/references/` | 12 の手引き: チェック、計画、忠実度、シーン、引き継ぎ、証拠 |
| `skills/antigraf/scripts/` | 47 の道具: Python 40、ブラウザ 7、端末一覧 1 |
| `assets/` | アイコン（512 と 128 ピクセル） |

約束はこのページに、各チェックの正確な許容差は完全な文書に書いてあります。

## 導入

パッケージ管理も `pip install` もアカウントも要りません。文字と素のスクリプトのフォルダです。

**方法 1: フォルダをコピー（推奨）**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

`Antigraf/skills/antigraf/` を、あなたのエージェントがスキルを読み込む場所へ移します。名前も `SKILL.md` の位置もそのまま、`references/` と `scripts/` も一緒に運びます。

**方法 2: フォルダに入れられない場合**

`skills/antigraf/SKILL.md` の中身をエージェントのカスタム指示欄に貼ります。ツールなしのテキストだけで動き、チェックはモデルが手作業で行い、最後の表にそう書かれます。

**方法 3: エージェントなし**

道具は普通のスクリプトです。

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

必要なもの: **Python 3.8 以上**（標準ライブラリのみ）、ブラウザ道具には **Node 18 以上**、たどる・押すには Chromium 系ブラウザ（Edge か Chrome）。どれも任意です。欠けたら段階を下げ、推測せずに最後の表に書きます。

## 使い方

一行で足ります。

```
/antigraf https://example.com
```

そこから六つの段階で進みます。

| 段階 | 何が起きるか |
|---|---|
| **1 仕事を聞く** | 1 複製、2 再構成、3 改善、4 研究。答えるまで何も複製しません。 |
| **2 必要な分だけ聞く** | 複製はそれ以上聞きません。再構成は何を変えるか、改善はあなたのプロジェクトと本当の目的、研究は深さと重要な部分を聞きます。 |
| **3 見ながらの計画** | 七つまで、あなたの言葉で。一つに「ここで止まる」を付け、ディスクに保存するので別のモデルが同じ段階から続けられます。 |
| **4 調べる・計画する・作る・測る** | 同じチェックを原本と複製の両方で、回を重ねて走らせます。 |
| **5 差を閉じる** | 失敗した行は次の指示として戻り、以前は合格していた行が今は失敗すれば「後戻り」として示されます。 |
| **6 表を出す** | 九つの領域、それぞれ 100 点満点、足を引っ張るものを名指し。その後に選択肢。 |

最後の表はこうなります。記録から計算され、モデルが打ち込むことはありません。

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  -------------
Words & layout           100%     3     0        0
Design, icons            100%     2     0        0
Behaviour, flows          80%     4     1        0  failing: G24
Phone & PWA              100%     2     0        0
Motion & 3D              100%     3     0        0
Media & speed            100%     2     0        0
Accessibility            100%     1     0        0
Sources, repairs         100%     4     0        0
Evidence, proof, pages    80%     4     1        0  failing: G12

Pictures  none compared - both sides need a shot at the same width

TOTAL  94.8% of the work this mode promised
```

実行されなかった、または不明と答えたチェックは **0 点**です。だから合計が複製をよく見せることはありません。どの仕事も、この表と三つの提案で終わります。さらに押し込む、差を署名付きで受け入れる、止める。

ロックは **100%** でだけ閉じます。すべての行が合格し、不明がなく、説明のつかない差が残らないときです。それまでは、開いたままのものをチェックと行で示します（例: `G5 @1440 hero pad 16 12 -4 +-4`）。

## よくある質問

**サイト全体を複製できますか、それとも最初のページだけですか？**
同じサイト内のリンクをすべてたどり、各ページを 3 つの幅、スマホ、タブレットで記録します。たどり着けなかったページや、押されなかった操作は「未調査」として記録され、ロックを開けません。見つけたページ数と歩いたページ数はいつでも表示されます。

**原本のソースコードを渡してくれますか？**
いいえ。原本を測り、あなたが自分の技術で自分の版を作ります。届くのはあなたのコードで、相手のコードの写しではありません。

**画像を見られないモデルでも動きますか？**
はい。デザインは数値で受け渡します。大きさ、色、余白、書体、押せる範囲。画像は比べるために使い、覚えるためには使いません。文字だけのモデルでも測定から作れます。

**何を複製しませんか？**
サーバー側の処理、認証情報、セッション用トークン、決済、会計データです。その形の項目を見つけたら実行を止め、代わりに `HANDOVER.md` に書き出します。自分でつなぐべきものが分かるようにするためです。

**本当にうまくいったと、どう分かりますか？**
各チェックは終了コード付きのファイルを書き、最後の表はその記録から計算されます。走らなかった、または不明と答えたチェックは 0 点です。モデルが自分の点数を打つことはできません。

**どんな種類の元を扱えますか？**
ウェブサイトと複数ページのウェブアプリ、スマホ優先のアプリと PWA の動作、プレーヤー付きの配信画面、商店とカタログ、文書サイト、そして描画呼び出し・シェーダー・動きまで含む 3D シーンです。

**動かすには何が必要ですか？**
Python 3.8 以上（標準ライブラリのみ）、ブラウザ用の道具には Node 18 以上、そして Chromium 系ブラウザ。パッケージ導入も、アカウントも、鍵も要りません。

## 正直な現状

ここでは意図して二つの数字を示します。スコアは一つの実際の原本と複製のペアについてゲートが示す値で、証明済みの数はすべてのゲートを通過したペアの数です。道具が完成したかを決めるのは二つ目です。

**能力は主張ではなく測定です。** 以下のゲートはすべて存在し、実行されます。実際に合格したものは、一つのペアのスコアとは別に数えます。

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 94.8% out of 100 - the three-page test pair (round 7)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 100% | 2 | 0 | 0 | - |
| Behaviour, flows | 80% | 4 | 1 | 0 | failing: G24 |
| Phone & PWA | 100% | 2 | 0 | 0 | - |
| Motion & 3D | 100% | 3 | 0 | 0 | - |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Accessibility | 100% | 1 | 0 | 0 | - |
| Sources, repairs | 100% | 4 | 0 | 0 | - |
| Evidence, proof, pages | 80% | 4 | 1 | 0 | failing: G12 |
| **Total** | **94.8%** | 25 | 2 | 0 | 2 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### ゲートごとの主張

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates  ·  0 proven on a real original-to-copy pair  ·  1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | measured | the three-page test pair round 7 |
| Icons and pictures, one partner each | G8, G17 | measured | the three-page test pair round 7 |
| Every page walked, planned and shipped | G11 | measured | the three-page test pair round 7 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | the three-page test pair round 7 |
| States: hover, focus, open, empty, error | G6 | measured | the three-page test pair round 7 |
| Motion: durations, easings, scroll | G13 | measured | the three-page test pair round 7 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | the three-page test pair round 7 |
| Speed and weight budgets | G15 | measured | the three-page test pair round 7 |
| Logic: same input, same answer, no secrets | G19 | measured | the three-page test pair round 7 |
| Defects found, and the copy repaired | G20, G21 | measured | the three-page test pair round 7 |
| 3D scene read as numbers | G25 | measured | the three-page test pair round 7 |
| 3D motion compared frame by frame | G26 | measured | the three-page test pair round 7 |
| Server seams listed for you to hook up | G16 | measured | the three-page test pair round 7 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | the three-page test pair round 7 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| the three-page test pair | unknown | round 7 | 25 of 27 | 2 | 0 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->



**測る側は動きます。作る側は、まだ全チェックを通る複製を一度も生んでいません。**

完全版の進捗欄はディスク上の記録から書かれ、手で書くことはありません。現在は 27 のチェック、本物の原本と複製の組で証明済み 0。百点と嘘より、零点と理由を見せたいからです。

## ライセンス

**Apache License 2.0**（[LICENSE-APACHE](LICENSE-APACHE)）または **MIT**（[LICENSE-MIT](LICENSE-MIT)）のどちらかを選べます。短い説明と、ライセンスが及ばない範囲は [LICENSE.md](LICENSE.md) にあります。アイコンと名称はプロジェクトに属します。フォークは、フォークであると明記すれば問題ありません。

## 貢献とセキュリティ

変更を提案する方法と、大切な唯一のルール（新しいチェックは、まず失敗することを示さなければならない）は [CONTRIBUTING.md](CONTRIBUTING.md) にあります。脅威を非公開で報せる方法、および Antigraf が守るものと守らないものは [SECURITY.md](SECURITY.md) にあります。

## 越えない線

Antigraf が複製するのは、ページの見た目と、ブラウザ上での振る舞いです。サーバー側のロジック、認証情報、セッショントークン、決済や会計のデータは**複製しません**。それららしい項目を見つけると止まり、拒否します。代わりに `HANDOVER.md` に書き出し、あなた自身のバックエンドに何を繋ぐべきかを法的に、あなたの条件で示します。

**海賊版、アカウント共有、課金・DRM・ログインの回避、私的データの収集、権利のないコンテンツ・ブランド・素材の複製を、私たちは認めません。** 自分が持つもの、公然と許諾されたもの、調べる許可があるものに使ってください。権利のない画像・フォント・ロゴ・文章はあなた自身のものに置き換え、誰も確認していないライセンスは、確認するか差し替えるまでロックを止めます。

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf。AI コーディングエージェントのための複製・クローン・調査スキル。</sub>
</p>
