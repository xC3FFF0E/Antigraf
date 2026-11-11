<p align="center">
  <img src="assets/antigraf.png" width="160" height="160" alt="Biểu tượng Antigraf: chân dung khắc hình người đội vòng nguyệt quế trên nền xanh lá">
</p>

<h1 align="center">Antigraf</h1>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.zh-hant.md">繁體中文</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <b>Tiếng Việt</b> ·
  <a href="README.pt.md">Português</a>
</p>

<p align="center">
  <b>Từ tiếng Hy Lạp <i>antígrafo</i> (αντίγραφο): một bản sao đáp lại bản gốc.</b><br>
  Kỹ năng nhân bản, sao chép hoặc nghiên cứu cho các tác nhân lập trình AI.<br>
  Nó nghiên cứu nguồn, dựng phiên bản của bạn,
  và <b>chứng minh</b> độ gần bằng những lệnh bạn chạy lại được.
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
  <a href="#cách-hoạt-động">Cách hoạt động</a> ·
<a href="#bốn-công-việc">Bốn công việc</a> ·
<a href="#điều-làm-nó-khác-biệt">Điều làm nó khác biệt</a> ·
<a href="#chỗ-nào-có-gì">Chỗ nào có gì</a> ·
<a href="#cài-đặt">Cài đặt</a> ·
<a href="#cách-dùng">Cách dùng</a> ·
<a href="#câu-hỏi-mọi-người-hay-đặt">Câu hỏi mọi người hay đặt</a> ·
<a href="#tình-trạng-trung-thực">Tình trạng trung thực</a> ·
<a href="#giấy-phép">Giấy phép</a> ·
<a href="#đóng-góp-và-bảo-mật">Đóng góp và bảo mật</a> ·
<a href="#ranh-giới-chúng-tôi-không-vượt-qua">Ranh giới chúng tôi không vượt qua</a>
</p>

<br>

Antigraf sống trong agent của bạn dưới dạng một gói hướng dẫn và một bộ công cụ nhỏ. Nó đi qua một
trang web, ứng dụng điện thoại hoặc trò chơi, ghi lại từng phần thành con số, dựng bản sao của bạn,
rồi bắt hai bên trả lời cùng một bộ kiểm tra cho đến khi không còn gì thất bại và không còn gì chưa
biết.

Điểm mấu chốt không phải là nói "trông giống nhau". Mà là chỉ ra dòng còn khác, và lệnh cho thấy nó.

<br>

<b>Nói gọn:</b> Antigraf là kỹ năng nhân bản 1:1 cho các tác nhân lập trình AI. Dùng để sao chép một website, nhân bản một ứng dụng web hay trò chơi, làm lại thiết kế thành của bạn, hoặc nghiên cứu cách một trang được dựng từ đầu đến cuối. Nó phủ toàn bộ trang, không chỉ trang đầu: mọi tuyến, khu, điều khiển, trạng thái mở, chuyển động, bố cục điện thoại, hành vi ngoại tuyến và cảnh 3D, mỗi thứ đều so với bản gốc và đều giữ khóa 100% cho đến khi khớp.

<table>
  <tr>
    <td width="25%" valign="top">
      <h3>Nghiên cứu mọi thứ</h3>
      Trang, màn hình, menu, nút điều khiển, và cả thứ nằm sau một cú nhấp. Mỗi con số đều mang nguồn gốc, nên phỏng đoán không thể giả làm phép đo.
    </td>
    <td width="25%" valign="top">
      <h3>Dựng bản của bạn</h3>
      Bản sao nằm trong dự án của bạn, với công nghệ bạn chọn. Không có gì từ nguồn đi kèm ngoài những gì bạn có quyền dùng.
    </td>
    <td width="25%" valign="top">
      <h3>Kiểm chứng, không phỏng đoán</h3>
      27 phép kiểm tra chạy ở cả hai bên mỗi vòng. Một phép chưa từng chạy, hoặc trả lời chưa biết, sẽ chặn khoá và không bao giờ tính là đạt.
    </td>
    <td width="25%" valign="top">
      <h3>Sẵn sàng cho agent</h3>
      Một tệp kỹ năng và các script thuần, để bất kỳ mô hình và môi trường nào cũng chạy cùng bộ kiểm tra. Đo lường không cần AI.
    </td>
  </tr>
</table>

<br>

## Cách hoạt động

Chỉ vào một nguồn, chọn một công việc, và nó chạy qua năm bước:

1. **Nghiên cứu:** đi qua nguồn, mở những gì ẩn sau cú nhấp và ghi lại thành con số.
2. **Lập kế hoạch:** mỗi trang, khối, nút, trạng thái và tuyến một dòng, mỗi dòng có phép kiểm tra phán xét nó.
3. **Dựng:** viết bản sao, phần nhìn thấy trước. Phần máy chủ chỉ được nêu tên, không sao chép.
4. **Đối chiếu:** cùng bộ kiểm tra chạy trên bản gốc và bản sao, hết vòng này đến vòng khác.
5. **Tinh chỉnh:** mỗi dòng thất bại quay lại làm chỉ dẫn dựng tiếp theo, cho đến khi khoá đóng.

## Bốn công việc

`/antigraf` hỏi đúng một câu trước khi mọi thứ bắt đầu.

| # | Công việc | Nó làm gì |
|---|---|---|
| **1** | **Sao chép** | Sao chép nguồn 1:1. Không hỏi thêm gì, và khoá mục tiêu ở 100%. |
| **2** | **Tái tạo** | Sao chép thành phiên bản của riêng bạn. Nó hỏi cần đổi gì: màu, thương hiệu, biểu tượng, câu chữ. |
| **3** | **Cải thiện** | Đặt một nguồn cạnh dự án của bạn, chỉ ra nó làm gì tốt hơn, và kết thúc bằng danh sách ngắn việc cần làm tiếp. |
| **4** | **Nghiên cứu** | Chỉ đọc, không chạy gì, thông tin nhạy cảm được che. Nó được dựng bằng gì, từ ngoài vào trong. |

Mọi công việc đã xong đều kết thúc bằng bảng 1 đến 100 trung thực theo từng lĩnh vực, điều gì đang
giữ chân lĩnh vực đó, và các lựa chọn tiếp theo của bạn.

## Điều làm nó khác biệt

| | **Antigraf** | Một kỹ năng sao chép thông thường |
|---|---|---|
| Chạy ở đâu | Mọi môi trường, mọi mô hình. Chỉ thư viện chuẩn của Python 3 và Node | Gắn với một vòng lặp agent |
| Cách quyết định "xong" | 27 phép kiểm tra, mỗi phép có mã thoát riêng, chạy đủ mỗi vòng | Mô hình nói trông ổn rồi |
| "Chưa so sánh" | Luôn chặn khoá | Thường bị tính là đạt |
| Khác biệt bạn chấp nhận | Chỉ của bạn, do bạn viết, không bao giờ bị bỏ im lặng | Không được mô hình hoá |
| Việc lớn | Chia thành làn, tối đa 3 trợ giúp, quy tắc 60 phút | Một lần chạy dài trôi dần |
| Điều nó tự nói về mình | Khối tiến độ sinh ra từ sổ ghi thật | Trang viết gì thì là vậy |

Không có điểm tổng nào che dòng nào đã thất bại. Hình ảnh tự nó không bao giờ làm đạt bất cứ điều gì.
Một mô hình yếu hơn, hoặc không nhìn được hình, không bao giờ hạ chuẩn: nó tiêu ít hơn và nói ra.

## Chỗ nào có gì

| Đường dẫn | Nội dung |
|---|---|
| `skills/antigraf/SKILL.md` | bản thân kỹ năng: công việc, giai đoạn, bậc, không gian làm việc, vòng, luật |
| `skills/antigraf/README.md` | tài liệu đầy đủ: các bước kiểm, dung sai, tiến độ, bố trí |
| `skills/antigraf/references/` | 12 hướng dẫn: kiểm, lập kế hoạch, độ trung thực, cảnh, bàn giao, bằng chứng |
| `skills/antigraf/scripts/` | 46 công cụ: 39 Python, 7 trình duyệt, một danh sách thiết bị |
| `assets/` | biểu tượng, 512 và 128 pixel |

Trang này nói nó hứa gì. Tài liệu đầy đủ nói dung sai chính xác của từng bước kiểm.

## Cài đặt

Không trình quản lý gói, không `pip install`, không tài khoản. Đây là một thư mục văn bản và script
thuần.

**Cách 1: sao chép thư mục (khuyến nghị)**

```bash
git clone https://github.com/xC3FFF0E/Antigraf.git
```

Rồi chuyển `Antigraf/skills/antigraf/` đến nơi agent của bạn nạp kỹ năng. Thư mục giữ nguyên tên,
giữ `SKILL.md` ở trên, và mang theo `references/` cùng `scripts/`.

| Môi trường | Thư mục đặt ở đâu |
|---|---|
| Thư mục kỹ năng của một dự án | `<dự án của bạn>/.claude/skills/antigraf/` |
| Mọi dự án trên máy | `~/.claude/skills/antigraf/` |
| Nơi khác | thư mục kỹ năng mà môi trường của bạn đọc |

**Cách 2: không có quyền vào thư mục**

Dán nội dung `skills/antigraf/SKILL.md` vào ô hướng dẫn tuỳ chỉnh của agent. Kỹ năng chạy chỉ bằng
văn bản đó, không có công cụ: các phép kiểm tra do mô hình làm bằng tay, và bảng cuối nói rõ phép nào
được làm theo cách đó.

**Cách 3: không cần agent**

Các công cụ là script bình thường.

```bash
cd skills/antigraf
python scripts/antigraf_mode.py --choose 1 --target https://example.com
```

Yêu cầu: **Python 3.8 trở lên** (chỉ thư viện chuẩn), **Node 18 trở lên** cho công cụ trình duyệt, và
trình duyệt dựa trên Chromium (Edge hoặc Chrome) để đi và nhấp. Mọi phần đều tuỳ chọn: thiếu một
phần, kỹ năng xuống một bậc và nói rõ trong bảng cuối thay vì phỏng đoán.

## Cách dùng

Một dòng là đủ:

```
/antigraf https://example.com
```

Từ đó nó chạy theo sáu bước.

| Bước | Điều gì xảy ra |
|---|---|
| **1. Hỏi công việc** | 1 Sao chép, 2 Tái tạo, 3 Cải thiện, 4 Nghiên cứu. Chưa có câu trả lời thì chưa sao chép gì. |
| **2. Chỉ hỏi điều cần** | Sao chép không hỏi thêm. Tái tạo hỏi cần đổi gì. Cải thiện hỏi dự án và điều bạn thật sự muốn. Nghiên cứu hỏi độ sâu và phần nào quan trọng. |
| **3. Viết kế hoạch bạn nhìn thấy** | Tối đa bảy bước bằng lời của bạn, một bước đánh dấu *dừng ở đây*, lưu xuống đĩa để mô hình khác tiếp từ đúng bước đó. |
| **4. Nghiên cứu, lập kế hoạch, dựng, đo** | Cùng bộ kiểm tra chạy trên bản gốc và bản sao, hết vòng này đến vòng khác. |
| **5. Đóng khoảng cách** | Mỗi dòng thất bại quay lại làm chỉ dẫn tiếp theo, và một dòng từng đạt mà nay thất bại được đánh dấu là thoái lui. |
| **6. Đưa bảng ra** | Tám lĩnh vực, mỗi lĩnh vực trên 100, nêu điều đang giữ chân nó. Rồi đến các lựa chọn. |

Bảng cuối trông như thế này, và được tính từ bằng chứng đã ghi, không bao giờ do mô hình tự đánh:

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

Một phép chưa từng chạy, hoặc trả lời chưa biết, tính là **không**, nên điểm tổng không bao giờ có thể
tô đẹp bản sao. Mọi công việc kết thúc bằng bảng này và ba đề nghị: đẩy tiếp, chấp nhận một khác biệt
là của bạn bằng giấy miễn có chữ ký, hoặc dừng.

Khoá chỉ đóng ở **100%**: mọi dòng đạt, không gì chưa biết, không khác biệt nào chưa giải thích. Trước
đó bảng nói rõ còn gì mở, theo phép kiểm tra và theo dòng, ví dụ `G5 @1440 hero pad 16 12 -4 +-4`.

## Câu hỏi mọi người hay đặt

**Nó sao chép được cả trang web hay chỉ trang đầu?**
Nó đi theo mọi liên kết cùng trang và ghi mỗi trang ở ba bề rộng, trên điện thoại và máy tính bảng. Những gì chưa tới, trang chưa đi và điều khiển chưa bấm đều được ghi là *chưa khảo sát* và giữ khóa. Bạn luôn thấy con số: trang tìm được so với trang đã đi.

**Nó có đưa cho tôi mã nguồn của bản gốc không?**
Không. Nó đo bản gốc và bạn dựng bản của mình bằng công nghệ bạn chọn. Thứ nhận được là mã của bạn, không phải bản sao mã của họ.

**Mô hình không nhìn được ảnh có dùng được không?**
Được. Thiết kế truyền bằng con số: kích thước, màu, khoảng cách, cỡ chữ, vùng bấm. Ảnh chỉ dùng để so, không dùng để học, nên mô hình chỉ đọc chữ vẫn dựng từ số đo.

**Nó từ chối sao chép những gì?**
Logic phía máy chủ, thông tin đăng nhập, mã phiên, thanh toán và dữ liệu kế toán. Gặp trường có dạng đó là dừng ngay và ghi vào `HANDOVER.md`, để bạn biết mình phải nối gì.

**Làm sao biết nó thật sự xong?**
Mỗi bước kiểm để lại một tệp kèm mã thoát, và bảng cuối được tính từ các sổ đó. Bước kiểm chưa chạy, hoặc trả lời không rõ, tính là không điểm. Mô hình không tự ghi điểm cho mình được.

**Nó xử lý được những loại nguồn nào?**
Website và ứng dụng web nhiều trang, ứng dụng ưu tiên điện thoại và hành vi PWA, giao diện phát trực tuyến có trình phát, cửa hàng và danh mục, trang tài liệu, và cảnh 3D gồm lệnh vẽ, shader và chuyển động.

**Chạy nó cần gì?**
Python 3.8 trở lên chỉ với thư viện chuẩn, Node 18 trở lên cho công cụ trình duyệt, và trình duyệt Chromium. Không cần cài gói, không tài khoản, không khóa.

## Tình trạng trung thực

Hai con so khac nhau duoc hien thi co chu dich: diem la nhung gi cac cong kiem noi ve mot cap that su goc-ban sao, con so da chung minh la so cap da qua toan bo cong kiem. Con so thu hai quyet dinh cong cu da xong hay chua.

**Nang luc duoc do, khong phai tuyen bo.** Moi cong kiem deu ton tai va chay duoc. Cai gi thuc su dat duoc thi dem rieng, tach khoi diem cua mot cap muc tieu.

<!-- ANTIGRAF:SCORE (written by scripts/antigraf_registry.py - do not edit by hand) -->

**Measured: 62.6% out of 100 - the three-page test pair (round 3)**

| Area | Score | Passing | Failing | Not measured | What holds it down |
|---|---|---|---|---|---|
| Words & layout | 100% | 3 | 0 | 0 | - |
| Design, icons | 50% | 1 | 1 | 0 | failing: G4 |
| Behaviour, flows | 20% | 1 | 4 | 0 | failing: G6, G7, G23, G19 |
| Phone & PWA | 100% | 2 | 0 | 0 | - |
| Motion & 3D | 33% | 1 | 2 | 0 | failing: G25, G26 |
| Media & speed | 100% | 2 | 0 | 0 | - |
| Sources, repairs | 75% | 3 | 1 | 0 | failing: G22 |
| Evidence, proof, pages | 40% | 2 | 3 | 0 | failing: G1, G11, G12 |
| **Total** | **62.6%** | 15 | 12 | 0 | 12 gate(s) not passing |

The lock needs 100%: every gate passing, nothing unknown. A gate that never ran counts as zero, not as a pass.

<!-- /ANTIGRAF:SCORE -->

### Tung cong kiem

<!-- ANTIGRAF:PROGRESS (written by scripts/antigraf_registry.py - do not edit by hand) -->

**27 gates  ·  0 proven on a real original-to-copy pair  ·  1 measured so far**

| What the gates check | Gates | State | Where it was measured |
|---|---|---|---|
| Look: sections, words, colours, spacing | G2, G3, G4, G5 | measured | the three-page test pair round 3 |
| Icons and pictures, one partner each | G8, G17 | measured | the three-page test pair round 3 |
| Every page walked, planned and shipped | G11 | measured | the three-page test pair round 3 |
| Behaviour: pressed, and the same result | G7, G23, G24 | measured | the three-page test pair round 3 |
| States: hover, focus, open, empty, error | G6 | measured | the three-page test pair round 3 |
| Motion: durations, easings, scroll | G13 | measured | the three-page test pair round 3 |
| Phone, install and offline (PWA) | G9, G14, G18 | measured | the three-page test pair round 3 |
| Speed and weight budgets | G15 | measured | the three-page test pair round 3 |
| Logic: same input, same answer, no secrets | G19 | measured | the three-page test pair round 3 |
| Defects found, and the copy repaired | G20, G21 | measured | the three-page test pair round 3 |
| 3D scene read as numbers | G25 | measured | the three-page test pair round 3 |
| 3D motion compared frame by frame | G26 | measured | the three-page test pair round 3 |
| Server seams listed for you to hook up | G16 | measured | the three-page test pair round 3 |
| Evidence, proof and a frozen plan | G0, G1, G10, G12 | measured | the three-page test pair round 3 |

| Target | Family | Kind | Gates passed | Failed | Unknown | Verdict |
|---|---|---|---|---|---|---|
| the three-page test pair | unknown | round 3 | 15 of 27 | 12 | 0 | measured |

`proven` means every gate ran, passed, and nothing was unknown. `measured` means the gates ran and left a real exit code. Anything else is `not proven`, and is not being claimed.

<!-- /ANTIGRAF:PROGRESS -->



**Nửa đo lường đã chạy được. Nửa dựng vẫn chưa từng tạo ra bản sao đạt mọi phép kiểm tra.**

Khối tiến độ trong tài liệu đầy đủ được viết từ sổ ghi trên đĩa, không bao giờ viết tay. Hiện nay là 27
phép kiểm tra, 0 đã chứng minh trên một cặp bản gốc - bản sao thật. Chúng tôi thà cho bạn thấy số
không và lý do, còn hơn một trăm và lời nói dối.

## Giấy phép

Hai giấy phép, bạn chọn một: **Apache License 2.0** ([LICENSE-APACHE](LICENSE-APACHE)) hoặc **MIT** ([LICENSE-MIT](LICENSE-MIT)). Bản tóm tắt và những gì giấy phép không bao gồm nằm trong [LICENSE.md](LICENSE.md). Biểu tượng và tên thuộc về dự án; bản fork vẫn được, miễn là ghi rõ đó là fork.

## Đóng góp và bảo mật

Cách đề xuất một thay đổi, và quy tắc duy nhất quan trọng (một phép kiểm tra mới phải được chứng minh là thất bại trước), nằm trong [CONTRIBUTING.md](CONTRIBUTING.md). Cách báo một lỗ hổng một cách riêng tư, và Antigraf bảo vệ bạn khỏi điều gì hay không, nằm trong [SECURITY.md](SECURITY.md).

## Ranh giới chúng tôi không vượt qua

Antigraf sao chép vẻ ngoài của trang và cách nó hành xử trong trình duyệt. Nó **không** sao chép logic
máy chủ, thông tin đăng nhập, mã phiên, dữ liệu thanh toán hay kế toán, và nó dừng lại từ chối khi
thấy một trường có hình dạng như vậy. Những phần đó được ghi vào `HANDOVER.md`, để bạn biết chính xác
cần nối gì vào máy chủ của mình, một cách hợp pháp và theo điều kiện của bạn.

**Chúng tôi không dung túng vi phạm bản quyền, chia sẻ tài khoản, vượt tường trả phí, DRM hay đăng
nhập, thu thập dữ liệu riêng tư, hay sao chép nội dung, thương hiệu, tài nguyên của người khác khi
chưa được phép.** Hãy dùng Antigraf với thứ bạn sở hữu, thứ có giấy phép mở, hoặc thứ bạn được phép
nghiên cứu. Hình ảnh, phông chữ, logo và câu chữ bạn không có quyền sẽ được thay bằng của bạn, và một
giấy phép chưa ai làm rõ sẽ giữ khoá đóng cho đến khi bạn làm rõ hoặc thay nó.

<br>

<p align="center">
  <img src="assets/antigraf-128.png" width="36" height="36" alt="Antigraf"><br>
  <sub>Antigraf. Kỹ năng nhân bản, sao chép hoặc nghiên cứu cho các tác nhân lập trình AI.</sub>
</p>
