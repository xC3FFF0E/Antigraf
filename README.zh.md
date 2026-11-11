<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Antigraf 图标：绿色底色上戴月桂冠的侧脸铜版画">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <b>简体中文</b> ·
  <a href="README.zh-hant.md">繁體中文</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt.md">Português</a>
</p>

<p align="center">
  <b>源自希腊语 <i>antígrafo</i>（αντίγραφο）：回应原件的复制品。</b><br>
  面向 AI 编程智能体的复制、克隆与调研技能。<br>
  它先研究源站，再建立你自己的版本，
  并用可以重复运行的命令<b>证明</b>两者有多接近。
</p>

<p align="center">
  <img alt="27 gates" src="https://img.shields.io/badge/gates-27-2d81ff?style=flat-square">
  <img alt="46 scripts, no installs" src="https://img.shields.io/badge/scripts-46%2C%20no%20installs-2d81ff?style=flat-square">
  <img alt="4 jobs" src="https://img.shields.io/badge/jobs-clone%20%C2%B7%20recreate%20%C2%B7%20improve%20%C2%B7%20study-2d81ff?style=flat-square">
  <img alt="Any model" src="https://img.shields.io/badge/works%20with-any%20model%20%C2%B7%20any%20harness-3a3a3a?style=flat-square">
  <img alt="Proven on 0 real pairs" src="https://img.shields.io/badge/proven%20on-0%20real%20pairs-d69e2e?style=flat-square">

  <img alt="Antigraf skill" src="https://img.shields.io/badge/skill-antigraf-1f883d?style=flat-square">
</p>

<p align="center">
  <a href="#工作方式">工作方式</a> ·
  <a href="#四项工作">四项工作</a> ·
  <a href="#与众不同之处">与众不同之处</a> ·
  <a href="#安装">使用方法</a> ·
  <a href="#使用方法">常见问题</a> ·
  <a href="#常见问题">真实状态</a> ·
  <a href="#真实状态">我们不越过的线</a>
</p>

<br>

Antigraf 以一份说明文件加一套小工具的形式，住在你的智能体里。它会走遍一个网站、手机应用或游戏，把每个部分记录成数字，构建你自己的版本，然后让两边回答同一套检查，直到没有失败，也没有未知。

重点不是宣称“看起来一样”，而是指出仍然不同的那一行，以及显示它的那条命令。

<br>

<b>直白地说：</b>Antigraf 是面向 AI 编程智能体的 1:1 复制技能。用它克隆网站、复制网页应用或游戏、把设计重做成你自己的，或从界面到内部研究一个站点是怎么搭起来的。它覆盖整套页面，而不只是首页：每条路由、每个区块、控件、展开后的状态、动画、手机布局、离线行为与 3D 场景，都各自与原站对比，并且都在匹配之前锁住 100%。

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>研究任何东西</h3>
      页面、屏幕、菜单、控件，以及点击之后藏着的东西。每个数字都带着它的来源，猜测无法冒充测量。
    </td>
    <td width="25%" valign="top">
      <h3>构建你自己的版本</h3>
      副本放在你的项目里，用你选择的技术栈。除了你有权使用的东西，原件不会随之带走任何内容。
    </td>
    <td width="25%" valign="top">
      <h3>验证，而非猜测</h3>
      每一轮 27 项检查在两边同时运行。没有运行、或回答未知的检查会阻止锁定，绝不算通过。
    </td>
    <td width="25%" valign="top">
      <h3>面向智能体</h3>
      一份技能文件加普通脚本，任何模型、任何环境都能驱动同一套检查。测量不需要 AI。
    </td>
  </tr>
</table>

<br>

## 工作方式

指定一个目标，选择一项工作，然后分五个阶段推进：

1. **研究**：走遍目标，打开点击之后隐藏的内容，记录成数字。
2. **计划**：每个页面、区块、控件、状态和路径各占一行，并写好判定它的检查。
3. **构建**：先做前端。服务端部分只列出，不复制。
4. **对照**：同一套检查在原件和你的副本上，反复运行。
5. **打磨**：每一行失败作为下一条构建指令返回，直到锁定闭合。

## 四项工作

`/antigraf` 在做任何事之前只问一个问题。

| # | 工作 | 内容 |
|---|---|---|
| **1** | **克隆** | 一比一复制。不再问任何问题，目标锁定为 100%。 |
| **2** | **再造** | 作为你自己的版本复制。它会问你改什么：配色、品牌、图标、文案。 |
| **3** | **改进** | 把目标与你的项目并排比较，指出对方更好的地方，并以简短的下一步清单收尾。 |
| **4** | **研究** | 只读，不执行任何东西，敏感信息隐去。从前端到后端，它是用什么做成的。 |

每项工作结束时都会给出按领域拆分的 1 至 100 的真实表格、拖住各领域的原因，以及接下来可选的方案。

## 与众不同之处

| | **Antigraf** | 常见的克隆技能 |
|---|---|---|
| 运行环境 | 任何环境、任何模型。只用 Python 3 与 Node 标准库 | 绑定在某个智能体循环 |
| 如何判定“完成” | 27 项检查，各有自己的退出码，每轮全部运行 | 模型说看着像 |
| “未比较” | 一律阻止锁定 | 常被算作通过 |
| 你接受的差异 | 只能由你写下，绝不会被悄悄抹掉 | 未被建模 |
| 大型任务 | 拆成分线，最多 3 个帮手，60 分钟过期规则 | 单一长跑逐渐失准 |
| 对自身的说法 | 由真实运行记录生成的进度块 | 页面写什么就是什么 |

不会用总分掩盖哪一行失败。图片本身永远不能通过任何检查。较弱的模型，或看不见图片的模型，绝不会降低标准，只会花得更少并如实说明。

## 各部分在哪里

| 路径 | 内容 |
|---|---|
| `skills/antigraf/SKILL.md` | 技能本体：任务、阶段、层级、工作区、回合、规则 |
| `skills/antigraf/README.md` | 完整文档：检查项、容差、进度、目录 |
| `skills/antigraf/references/` | 12 份指南：检查项、计划、还原度、场景、交接、证据 |
| `skills/antigraf/scripts/` | 46 个工具：39 个 Python、7 个浏览器、1 个设备清单 |
| `assets/` | 图标，512 与 128 像素 |

这页讲它承诺什么，完整文档讲每项检查的准确容差。

## 安装

没有包管理器，没有 `pip install`，没有账号。它只是一个文件加普通脚本的文件夹。

**方式 1：复制文件夹（推荐）**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

然后把 `Antigraf/skills/antigraf/` 移到你的智能体读取技能的目录。名字不变，`SKILL.md` 仍在顶部，`references/` 与 `scripts/` 一并带走。

**方式 2：无法放入文件夹时**

把 `skills/antigraf/SKILL.md` 的内容粘贴到智能体的自定义指令栏。技能只靠这段文字运行、没有工具，检查由模型手工完成，最后的表格会说明哪些是这样做。

**方式 3：不用智能体**

这些工具就是普通脚本。

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

需要：**Python 3.8 或更新**（仅标准库），浏览器工具需要 **Node 18 或更新**，走遍与点击需要 Chromium 系浏览器（Edge 或 Chrome）。每一项都是可选的：缺了就降一级，并在最后的表格中说明，而不是猜测。

## 使用方法

一行就够：

```
/antigraf https://example.com
```

由此分六步推进。

| 步骤 | 会发生什么 |
|---|---|
| **1. 问工作** | 1 克隆、2 再造、3 改进、4 研究。在你回答之前什么都不复制。 |
| **2. 只问必须问的** | 克隆不再追问。再造问要改什么，改进问你的项目与真正目的，研究问深度与重点。 |
| **3. 写下你能看见的计划** | 最多七步，用你自己的话，其中一步标为“在此停下”，存到磁盘，别的模型可从同一步接上。 |
| **4. 研究、计划、构建、测量** | 同一套检查在原件和副本上反复运行。 |
| **5. 关闭差距** | 失败的行作为下一条构建指令返回；原先通过而现在失败的行会标为回退。 |
| **6. 给出表格** | 八个领域，各按 100 计分，并指出拖住它的原因，然后给出选项。 |

最后的表格长这样，由记录计算得出，绝不是模型手打的：

```
Area                    Score  pass  fail  unknown  What holds it
----------------------  -----  ----  ----  -------  -----------------------------------
Words & layout           100%     3     0        0
Design, icons             50%     1     1        0  failing: G4 contrast
Behaviour, flows           0%     0     0        5  not measured: G6, G7, G23, G24, G19
```

没有运行、或回答未知的检查计为 **零分**，所以总分绝不会替副本说好话。每项工作都以这张表与三种提议结束：继续推进、以签署的豁免接受差异、或者停下。

锁定只在 **100%** 时闭合：每一行通过、没有任何未知、没有无法解释的差异。在此之前，表格会按检查与行列出仍然敞开的项，例如 `G5 @1440 hero pad 16 12 -4 +-4`。

## 常见问题

**能复制整个站点，还是只有首页？**
它会跟随所有同站链接，把每个页面记录在三种宽度、手机与平板上。没走到的页面、没按过的控件都会记为“未探查”，并锁住结果。你随时看得到数量：发现的页面与走过的页面。

**它会给我原站的源代码吗？**
不会。它测量原站，你用自己选的技术栈写出自己的版本。交付的是你的代码，不是对方代码的翻版。

**看不见图片的模型也能用吗？**
可以。设计以数字传递：尺寸、颜色、间距、字号、可点击范围。图片只用来对比，不用来学习，所以纯文字的模型也能照测量值构建。

**它拒绝复制什么？**
服务端逻辑、凭据、会话令牌、支付与账务数据。遇到这类字段会立即停止，并写进 `HANDOVER.md`，让你清楚知道自己要接哪些东西。

**我怎么知道它真的做到了？**
每项检查都会写一个带退出码的文件，最后的表格由这些记录算出来。没跑过的、或回答“未知”的，直接算零分。模型不能自己填分数。

**它能处理哪些类型的源？**
网站与多页网页应用、手机优先的应用与 PWA 行为、带播放器的流媒体界面、商店与目录、文档站，以及包含绘制调用、着色器与运动的 3D 场景。

**运行它需要什么？**
Python 3.8 以上（只用标准库）、浏览器工具需要 Node 18 以上，以及 Chromium 系浏览器。不用安装包，不用账号，不用密钥。

## 真实状态

这里刻意显示两个不同的数字：得分是各道检查对一对真实原版与副本给出的结果，已证明的数量是通过全部检查的配对数量。决定工具是否完成的是第二个。

**能力靠测量，不靠宣称。** 下面每一道检查都存在并可运行。真正通过的，与某一对目标的得分分开计数。

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 54.0% out of 100 - test-pair-3page (round 1)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 100% | 2 | 0 | 0 | - |
| Behaviour, flows | 0% | 0 | 5 | 0 | failing: G6, G7, G23, G24, G19 |
| Phone & PWA | 0% | 0 | 2 | 0 | failing: G14, G18 |
| Motion & 3D | 33% | 1 | 2 | 0 | failing: G25, G26 |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Sources, repairs | 50% | 2 | 1 | 1 | failing: G16 |
| Evidence, proof, pages | 60% | 3 | 2 | 0 | failing: G1, G12 |
| **Total** | **54.0%** | 13 | 13 | 1 | 14 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### 逐项检查的主张

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates · 0 proven on a real original-to-copy pair · 1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | proven | test-pair-3page checks/round-1 |
| Icons and pictures, one partner each | G8, G17 | proven | test-pair-3page checks/round-1 |
| Every page walked, planned and shipped | G11 | proven | test-pair-3page checks/round-1 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | test-pair-3page checks/round-1 |
| States: hover, focus, open, empty, error | G6 | measured | test-pair-3page checks/round-1 |
| Motion: durations, easings, scroll | G13 | proven | test-pair-3page checks/round-1 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | test-pair-3page checks/round-1 |
| Speed and weight budgets | G15 | proven | test-pair-3page checks/round-1 |
| Logic: same input, same answer, no secrets | G19 | measured | test-pair-3page checks/round-1 |
| Defects found, and the copy repaired | G20, G21 | proven | test-pair-3page checks/round-1 |
| 3D scene read as numbers | G25 | measured | test-pair-3page checks/round-1 |
| 3D motion compared frame by frame | G26 | measured | test-pair-3page checks/round-1 |
| Server seams listed for you to hook up | G16 | measured | test-pair-3page checks/round-1 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | test-pair-3page checks/round-1 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| test-pair-3page | unknown | round 1 | 13 of 27 | 13 | 0 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->



**测量的一半能用。构建的一半还没有做出过通过全部检查的副本。**

完整文档中的进度块由磁盘上的记录写成，从不手写。目前是 27 项检查，在真实的原件与副本组合上已证实的为 0。我们宁可给你一个零和原因，也不要一个百和谎言。

## 我们不越过的线

Antigraf 复制的是页面在浏览器里的外观与行为。它**不复制**服务端逻辑、凭据、会话令牌、支付或会计数据；一旦发现形似这类字段，它会停下并拒绝。这些内容会写入 `HANDOVER.md`，让你清楚知道该在自己的后端接上什么，合法地、按你的条件进行。

**我们不纵容盗版、账号共享、绕过付费墙、DRM 或登录、抓取私人数据，或在未经许可的情况下复制他人的内容、品牌或素材。** 请把 Antigraf 用在你拥有的、公开授权的、或你有权研究的东西上。你没有权利的图像、字体、标志与文案，会被替换成你自己的；没人清理的许可会一直阻止锁定，直到你清理或替换为止。

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf。面向 AI 编程智能体的复制、克隆与调研技能。</sub>
</p>
