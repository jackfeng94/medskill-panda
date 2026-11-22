<div align="center">

<img src="assets/logo.png" alt="Medskill Panda" width="128">

[English](README.md) · **Tiếng Việt**

# Medskill Panda

**Slide y khoa có kiểm chứng và viết khoa học, do chính agent lập trình của bạn thực hiện.**<br>
Một plugin cho Claude Code: phỏng vấn bạn, lập kế hoạch bài nói, đối chiếu mọi con số với nguồn,
bắt các dấu hiệu "slide do máy làm", và hỗ trợ viết bài báo, tổng quan, đề cương, poster.

[![licence MIT](https://img.shields.io/badge/licence-MIT-11607a)](LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-c0392b)](#cài-đặt)
[![version 1.3.0](https://img.shields.io/badge/version-1.3.0-4a5a6a)](CHANGELOG.md)
[![skills-36-](https://img.shields.io/badge/skills-36-11607a)](#các-skill)
[![tests](https://github.com/jackfeng94/medskill-panda/actions/workflows/tests.yml/badge.svg)](https://github.com/jackfeng94/medskill-panda/actions/workflows/tests.yml)
[![python 3.8+](https://img.shields.io/badge/python-3.8%2B-4a5a6a)](#hook)

**Chưa quen terminal hay Claude Code? Bắt đầu từ [hướng dẫn từng bước](docs/HUONG-DAN.md).**

<img src="assets/example-slides.vi.92fee725.png" alt="Sáu slide HTML của ví dụ DEMO-HF: tiêu đề, dòng bệnh nhân, Kaplan–Meier, forest plot, chất lượng sống, hiệu quả tuyệt đối" width="100%">

<sub>Bộ slide thật do plugin dựng từ dữ liệu mô phỏng (<a href="examples/demo-hf/">examples/demo-hf</a>): tiêu đề khẳng định, hình vẽ từ dữ liệu, dòng nguồn trên mọi slide, 0 lỗi slop.</sub>

</div>

---

## Vì sao dùng

- **Không con số nào từ trí nhớ.** Mọi HR, %, khoảng tin cậy trên slide đều có nguồn, vị trí
  trong bài (trang, bảng, hình) và câu trích nguyên văn. PMID, DOI, NCT chỉ lấy từ tra cứu thật.
- **Không dựng slide trước khi bạn duyệt kế hoạch.** Hook khoá thư mục `build/` và `out/`
  cho đến khi `plan.md` được bạn đồng ý.
- **Không "slide AI".** Nhãn eyebrow, gợi ý "bấm tiếp" trên slide, ghi chú "đã đổi màu",
  placeholder… bị phát hiện ngay lúc lưu.
- **Hợp với Việt Nam.** Phỏng vấn và slide bằng tiếng Việt, định dạng số `0,58`, tra cứu
  phác đồ Bộ Y tế và Dược thư Quốc gia, dùng template bệnh viện của bạn.

## Cách hoạt động

<div align="center">
<img src="assets/pipeline.vi.1069afb3.png" alt="Medskill Panda hoạt động thế nào: đầu vào, trục chung gồm brief, kế hoạch và sổ bằng chứng, rồi làn slide và làn viết bài, một bước kiểm tra, bàn giao kèm thư mục dự án" width="100%">
</div>

Slide và bản thảo dùng chung một trục bằng chứng: cùng brief, cùng kế hoạch đã duyệt, cùng sổ
bằng chứng, rồi tách thành tuyến slide và tuyến viết bài, nhập lại ở bước kiểm tra. Với bài
thuyết trình, chỉ cần nói *"làm slide journal club về DAPA-HF"*; `medical-deck` chạy các bước:

| # | Bước | Skill | Bạn cần làm |
|---|------|-------|-------------|
| 1 | Phỏng vấn | `deck-grilling` | Trả lời một lượt câu hỏi, xác nhận `brief.md` |
| 2 | Template | `template-matching` | Đưa file .pptx/.potx của bệnh viện (nếu có) |
| 3 | Kế hoạch | `deck-planning` | **Duyệt `plan.md`** |
| 4 | Bằng chứng | `evidence-research` | — |
| 5 | Hình | `medical-figures` | — |
| 6 | Dựng slide | `html-deck-building` · `pptx-deck-building` · `beamer-deck-building` | — |
| 7 | Kiểm tra | `slop-audit` + `evidence-audit` | — |
| 8 | Bàn giao | — | Nhận file và báo cáo những gì đã/chưa kiểm chứng |

**Ba định dạng xuất:** HTML (một file offline, có chuyển động, bút laser), PowerPoint
(trong template của bạn, biểu đồ gốc sửa được), LaTeX Beamer (PDF, hợp với bảo vệ luận án
và bài có công thức).

<div align="center">
<img src="assets/example-pptx.vi.a833d2d6.png" alt="Cùng bài nói dưới dạng PowerPoint sửa được trong một template có nhận diện riêng: slide tiêu đề, sơ đồ thử nghiệm gốc, Kaplan–Meier, forest plot, biểu đồ đường gốc, các con số chính" width="100%">
</div>

## Cài đặt

Lần đầu dùng? [Hướng dẫn từng bước](docs/HUONG-DAN.md) đi từ cài Claude Code, đăng nhập đến
bài thuyết trình đầu tiên.

Trong Claude Code:

```bash
claude plugin marketplace add jackfeng94/medskill-panda
```

```bash
claude plugin install medskill-panda@medskill-panda
```

Hoặc gõ trong phiên Claude Code: `/plugin marketplace add jackfeng94/medskill-panda` rồi
`/plugin install medskill-panda@medskill-panda`.

Cập nhật bản mới:

```bash
claude plugin marketplace update medskill-panda
```

Chạy thử từ bản clone:

```bash
git clone https://github.com/jackfeng94/medskill-panda.git
```

```bash
claude --plugin-dir ./medskill-panda
```

## Bắt đầu nhanh

| Bạn muốn | Gõ |
|----------|----|
| Làm bài thuyết trình | *"Làm slide grand rounds 20 phút về suy tim EF giảm"* |
| Chỉ chốt ý tưởng bài nói | `/medskill-panda:grill-deck` |
| Kiểm tra slide có sẵn | `/medskill-panda:audit-deck` |
| Xem tiến độ các bài nói | `/medskill-panda:status` |
| Thiết lập dự án viết bài báo | `/medskill-panda:scientific-writer-init` |
| Viết bài báo bằng tiếng Anh cho tạp chí quốc tế | *"Draft a STROBE cohort paper for [journal]"* |
| Viết tổng quan tài liệu | *"Viết tổng quan hệ thống về SGLT2i trong suy thận mạn"* |
| Kiểm tra bản thảo Word/LaTeX/Markdown | `/medskill-panda:audit-manuscript bai-bao.docx` |
| Từ bài báo ra slide hoặc poster, cùng số liệu | `/medskill-panda:paper-to-deck` |

## Viết khoa học

Chạy `/medskill-panda:scientific-writer-init` một lần trong thư mục dự án. Từ đó, mỗi yêu
cầu viết đi theo cùng nguyên tắc như làm slide:

1. **Phỏng vấn ngắn**: loại bài, nơi công bố, **ngôn ngữ (tiếng Việt, tiếng Anh hay song
   ngữ)**, định dạng (Word, LaTeX, Markdown), thiết kế nghiên cứu và guideline báo cáo.
2. **Bạn duyệt dàn ý** trước khi viết.
3. **Bằng chứng**: tra PubMed, Europe PMC, OpenAlex, Crossref miễn phí; mỗi nhận định gắn
   với nguồn và câu trích. Bản thảo chưa công bố không gửi ra ngoài.
4. **Viết từng phần**, số liệu chỉ từ dữ liệu của bạn hoặc từ nguồn đã mở.
5. **Kiểm tra** bằng `/medskill-panda:audit-manuscript`: văn phong "AI" bằng cả tiếng Việt
   và tiếng Anh, con số thiếu trích dẫn, placeholder, `p = 0.000`, dấu thập phân lẫn lộn,
   số liệu lệch giữa bản tiếng Việt và tiếng Anh, liên kết nhận định–bằng chứng, guideline,
   tác giả.

<div align="center">
<img src="assets/example-manuscript.vi.8dc2e4cb.png" alt="Trang bản thảo mẫu có tóm tắt tiếng Anh và tiếng Việt, cạnh kết quả lint_prose" width="100%">
</div>

## Biểu đồ

Hình vẽ từ dữ liệu, không bao giờ từ trí nhớ: mỗi biểu đồ được vẽ từ con số trong sổ bằng
chứng hoặc dữ liệu của tác giả, lưu dạng SVG cho slide HTML, PowerPoint và bản thảo, và ghi
nhãn theo ngôn ngữ của bài (`0,75` cho tiếng Việt, `0.75` cho tiếng Anh).

<div align="center">
<img src="assets/chart-gallery.vi.9347c0c3.png" alt="Tám loại biểu đồ: Kaplan–Meier kèm số còn theo dõi, forest plot, sơ đồ CONSORT, biểu đồ đường kèm dải tin cậy, cột nhóm kèm khoảng tin cậy, box plot kèm từng bệnh nhân, cột chồng phân độ NYHA, đường ROC" width="100%">
</div>

<sub>Cả tám biểu đồ vẽ từ dữ liệu mô phỏng bằng <a href="examples/demo-hf/make_charts.py">examples/demo-hf/make_charts.py</a>; bản tiếng Anh ở <code>examples/demo-hf/out/charts/en/</code>.</sub>

## Các skill

<details open>
<summary><b>Thuyết trình (13)</b> — một điểm vào duy nhất: <code>medical-deck</code></summary>

| Skill | Vai trò |
|-------|---------|
| `medical-deck` | Điều phối 8 bước; điểm bắt đầu cho mọi yêu cầu làm slide |
| `deck-grilling` | Phỏng vấn để chốt brief: đối tượng, thời lượng, định dạng, template, nguồn |
| `deck-planning` | Dàn ý tiêu đề-khẳng định, hình cho từng slide, ngân sách thời gian |
| `evidence-research` | PubMed, Europe PMC, ClinicalTrials.gov, phác đồ Bộ Y tế; trích số nguyên văn |
| `medical-figures` | Kaplan–Meier, forest plot, CONSORT/PRISMA, hình cơ chế, hình động |
| `template-matching` | Đo màu, font, bố cục từ template bệnh viện/hội nghị |
| `html-deck-building` | Bộ slide HTML một file, chuyển động, công cụ trình chiếu |
| `pptx-deck-building` | PowerPoint trong template, biểu đồ gốc, ghi chú người nói |
| `beamer-deck-building` | LaTeX Beamer → PDF, template hội nghị / seminar / bảo vệ |
| `slop-audit` | Bắt dấu hiệu slide do máy làm |
| `evidence-audit` | Đối chiếu số với nguồn, kiểm tra trích dẫn, quét thông tin định danh bệnh nhân |
| `grill-deck` | Lệnh tắt: chỉ chạy phỏng vấn |
| `audit-deck` | Lệnh tắt: chạy cả hai bước kiểm tra trên slide có sẵn |

</details>

<details>
<summary><b>Viết & nghiên cứu (9)</b></summary>

`scientific-writing` · `literature-review` · `research-lookup` · `citation-management` ·
`peer-review` · `scientific-critical-thinking` · `hypothesis-generation` ·
`research-grants` · `venue-templates`

</details>

<details>
<summary><b>Lâm sàng (3)</b> — chỉ dùng với dữ liệu nghiên cứu/đã khử định danh</summary>

`clinical-reports` · `clinical-decision-support` · `treatment-plans`

Mọi đầu ra cần người có chuyên môn duyệt; không dùng để ra quyết định điều trị.

</details>

<details>
<summary><b>Hình ảnh & poster (5)</b></summary>

`scientific-schematics` · `infographics` · `generate-image` · `latex-posters` · `pptx-posters`

</details>

<details>
<summary><b>Tệp & web (6)</b></summary>

`docx` · `pdf` · `pptx` · `xlsx` · `markitdown` · `parallel-web`

</details>

## Hook

Chỉ hoạt động khi làm slide, im lặng ở mọi việc khác:

| Hook | Làm gì |
|------|--------|
| `route_prompt.py` | Yêu cầu có chữ "slide", "thuyết trình", "journal club"… → nhắc bắt đầu từ `medical-deck` |
| `plan_gate.py` | Chặn ghi vào `build/`, `out/` và lệnh dựng slide cho đến khi `plan.md` được duyệt |
| `slop_on_save.py` | Kiểm tra mỗi slide HTML vừa lưu: dấu hiệu do máy làm, và từng con số so với `evidence/claims.json` |

Cần Python 3.8+; không có Python thì hook tự bỏ qua, không bao giờ chặn công việc vì lỗi
của chính nó. Tắt cổng duyệt: `MEDSKILL_PANDA_NO_GATE=1`.

## Khoá API (tuỳ chọn)

| Biến | Dùng cho |
|------|----------|
| `OPENROUTER_API_KEY` | `generate-image`, `scientific-schematics`, `infographics` |
| `PARALLEL_API_KEY` | `parallel-web`, `research-lookup` |

Các skill còn lại, kể cả toàn bộ quy trình làm slide và tra cứu PubMed, không cần khoá.

## Phát triển

```bash
python -m unittest discover -s tests -v
```

Test dùng thư viện chuẩn; cài thêm `pypdf python-pptx python-docx reportlab requests` để chạy cả
test PDF/PPTX/DOCX và các script tra cứu.
CI chạy trên mỗi lần push. Thay đổi giữa các phiên bản ở [`CHANGELOG.md`](CHANGELOG.md).

## Giấy phép

MIT, © Nguyen-Minh-Tan Phung ([@jackfeng94](https://github.com/jackfeng94)). Các thành phần
bên thứ ba và giấy phép của chúng: xem [`NOTICE.md`](NOTICE.md).
