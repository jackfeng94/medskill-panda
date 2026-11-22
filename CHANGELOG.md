# Changelog

## Unreleased

- **PowerPoint truyền đạt tốt hơn và đủ thành phần:** `pptx_from_spec.py` có thêm các loại slide
  `agenda` (mục lục, đánh dấu phần đang nói, số phút), `section` (slide chuyển phần), `pico` (câu
  hỏi nghiên cứu dạng PICO), `two-column`/`comparison` (điểm mạnh và hạn chế, cũ và mới),
  `key-message` (câu kết luận cần nhớ, chữ lớn). Slide tiêu đề có thêm `affiliation`, `event`,
  `date`; `figure-text` và `two-column` có `takeaway` (một câu chốt dưới đường kẻ màu nhấn);
  `big-number` canh giữa, có vạch ngăn và dòng `context`; `references` nhận mục có cấu trúc
  (đánh số, thụt dòng treo, tên tạp chí in nghiêng). Đường kẻ và mũi tên không còn bóng mờ.
- **`check_spec.py`:** kiểm tra `deck.json` trước khi dựng: trường bắt buộc, ghi chú, nguồn của
  slide số liệu, và đủ thành phần theo loại bài (`--recipe journal-club`, `journal-club-report`,
  `conference`, `lecture`).
- **Từ một bài báo PDF ra bộ PPTX journal club đầy đủ:** bảng thành phần trong
  `pptx-deck-building`, ánh xạ recipe trong `deck-planning`, mục 7.8 trong hướng dẫn. Ví dụ
  DEMO-HF giờ là bài journal club 12 slide; CI chạy `check_spec`, `check_pptx`, `lint_slop` trên nó.
- **Badge số unit test** trong README; test bảo đảm con số khớp bộ test.

## 1.3.0

### Mới trong lần này
- **Kiểm tra số liệu ngay khi lưu slide:** hook `slop_on_save.py` giờ đối chiếu mọi con số trên
  slide vừa lưu với `evidence/claims.json` (dùng `check_claims.slide_findings`). Số không có nhận
  định nào bị báo UNSUPPORTED, số thuộc nhận định của slide khác bị báo ELSEWHERE; chưa có
  `claims.json` mà slide có số cũng bị báo.
- **Lệnh `/medskill-panda:paper-to-deck`:** từ bài báo viết bằng `scientific-writing` ra slide hoặc
  poster dùng chung sổ bằng chứng. `medical-deck/scripts/manuscript_to_evidence.py` nhập các nhận
  định đánh dấu `[claim:…] [evidence:…]` (giá trị, câu trích, nguồn, trạng thái kiểm chứng).
- **CI chạy ví dụ DEMO-HF** (`examples/demo-hf/check.sh`): dựng slide HTML, PowerPoint và bản
  thảo bằng chính công cụ của plugin rồi chạy mọi bước kiểm tra.
- **Gỡ hai skill ít liên quan:** `market-research-reports`, `scholar-evaluation` (còn 36 skill).

### Từ sau 1.2.0
- Ảnh README và hướng dẫn mang mã nội dung trong tên (`pipeline.vi.1069afb3.png`…), do
  `assets/src/publish_art.py` tạo và tự cập nhật đường dẫn: đổi ảnh là đổi tên, nên trình duyệt
  và GitHub không còn hiện bản cũ. Test bảo đảm mọi ảnh đều có mã và đều được dùng.
- Hướng dẫn A–Z có thêm ảnh ở các bước: kết quả slide HTML và PowerPoint, các loại biểu đồ, bản
  thảo mẫu.
- Ảnh README theo phong cách đồ hoạ tạp chí: sơ đồ quy trình có dải màu theo giai đoạn, biểu tượng
  nét mảnh, tiêu đề chữ có chân, ngoặc nhóm ba giai đoạn; ảnh ví dụ thành các "plate" kiểu hình
  trong bài báo (cột chú thích, slide lớn kèm ảnh nhỏ, trang bản thảo có chú thích đánh số, biểu đồ
  gắn nhãn A–H). Không bo góc, không đổ bóng, không nền chuyển màu.
- Slide tiêu đề của ví dụ có đường Kaplan–Meier thật thay cho khoảng trống.
- `pptx_from_spec.py`, sơ đồ (`diagram`): kiểu mặc định mới, ô vuông viền mảnh, dải màu nhấn ở
  đầu ô, dòng đầu in đậm cùng màu, chữ căn trái, không bóng, đường nối mảnh màu xám; kiểu bo góc
  cũ vẫn có qua `theme.corners: "rounded"`. Sửa lỗi đường nối vào hình tròn (ô ngẫu nhiên hoá) đi
  chéo vì dùng sai điểm nối.
- Hướng dẫn từ A đến Z cho người mới (`docs/HUONG-DAN.md`, `docs/GUIDE.md`): cài Claude Code,
  đăng nhập, cài plugin, làm bài thuyết trình đầu tiên, kiểm tra slide, viết bài báo, làm tiếp,
  cập nhật, xử lý sự cố, thuật ngữ; liên kết từ đầu hai README.
- Ảnh README làm lại theo phong cách tài liệu khoa học: sơ đồ hai làn (bạn / Medskill Panda)
  với nhãn rõ trên từng mũi tên, góc vuông, không đổ bóng; slide mẫu và ảnh ví dụ bỏ bo góc,
  đổ bóng và nền chuyển màu.
- Ví dụ DEMO-HF thiết kế lại: slide HTML 6 trang (slide tiêu đề nền màu, khung biểu đồ, khung
  kết luận) và bản PowerPoint dựng bằng `pptx-deck-building` trong một template có nhận diện
  riêng (`make_template.py`), với sơ đồ và biểu đồ gốc sửa được; ảnh README tương ứng.
- `lint_slop.py` không đếm chân trang, số trang và dòng nguồn của PPTX vào giới hạn chữ (S18),
  giống cách đã làm với HTML.
- Bộ sưu tập biểu đồ (`examples/demo-hf/make_charts.py`): Kaplan–Meier kèm số còn theo dõi, forest
  plot, CONSORT, biểu đồ đường kèm dải KTC, cột nhóm kèm KTC, box plot kèm từng điểm, cột chồng
  phân độ NYHA, ROC; dạng SVG, tiếng Anh và tiếng Việt; thêm mục Biểu đồ vào hai README.
- Ảnh README làm lại: sơ đồ quy trình dạng thẻ theo dải ngang (băng tiêu đề và đầu vào →
  trục chung → hai làn slide và viết bài → dải kiểm tra → bàn giao và thư mục dự án), cùng ảnh đầu ra thật của bộ slide và bản
  thảo; mỗi ảnh có bản tiếng Anh và tiếng Việt. Script sinh ảnh ở `assets/src/`.
- Ví dụ trọn vẹn `examples/demo-hf/` (dữ liệu mô phỏng): bộ slide HTML tiếng Anh và tiếng
  Việt, bản thảo Word có tóm tắt song ngữ, dựng lại bằng `build.sh`.
- `lint_prose.py` nhận diện ngôn ngữ theo từng đoạn: bài song ngữ dùng 0.75 ở phần tiếng Anh
  và 0,75 ở phần tiếng Việt không còn bị báo lẫn dấu thập phân; "chênh lệch tuyệt đối" và các
  thuật ngữ thống kê tương tự không còn bị coi là phóng đại.
- README song ngữ: `README.md` (tiếng Anh, bản mặc định trên GitHub) và `README.vi.md`
  (tiếng Việt), có nút chuyển ngôn ngữ.
- `lint_prose.py --compare` bỏ qua số thứ tự trích dẫn như `[4]`.
- Test giữ hai bản README đồng bộ: đủ skill, cùng phiên bản, cùng các lệnh, ảnh tồn tại.

## 1.2.0

### Viết khoa học
- Viết lại hướng dẫn dự án (`templates/CLAUDE.scientific-writer.md`, `AGENTS…`): phỏng vấn →
  tác giả duyệt dàn ý → bằng chứng → viết → kiểm tra → bàn giao. Bỏ các quy định mâu thuẫn với
  skill `scientific-writing` ("không bao giờ hỏi", chỉ tiêu số trích dẫn, bắt buộc hình AI,
  mọi tìm kiếm qua dịch vụ trả phí).
- Chọn ngôn ngữ ngay từ đầu: tiếng Việt, tiếng Anh hoặc song ngữ, với quy tắc riêng cho từng
  ngôn ngữ và kiểm tra số liệu khớp giữa hai bản.
- Mặc định dùng công cụ tra cứu miễn phí; bản thảo chưa công bố không gửi ra ngoài khi chưa
  được tác giả cho phép.
- `lint_prose.py` mới (Markdown, LaTeX, Word; tiếng Việt và tiếng Anh): placeholder, văn phong
  "máy làm", phóng đại, thống kê thiếu trích dẫn, `p = 0.000`, dấu thập phân lẫn lộn, gạch đầu
  dòng tràn lan, số lệch giữa hai bản ngôn ngữ.
- Lệnh `/medskill-panda:audit-manuscript` chạy mọi bước kiểm tra bản thảo và ghi báo cáo.
- Ba script của `literature-review` có `--help`.
- Test cho template, `lint_prose.py` và các script viết bài; CI cài thêm `python-docx`.

## 1.1.0

### Gộp chức năng trùng lặp
- `scientific-slides` được gộp vào quy trình `medical-deck`. `medical-deck` giờ là điểm vào
  duy nhất cho mọi yêu cầu làm slide (y khoa và nghiên cứu nói chung).
- Thêm skill `beamer-deck-building`: bước 6 xuất LaTeX Beamer (PDF), dùng lại các template
  hội nghị / seminar / bảo vệ luận án và script kiểm tra của `scientific-slides`.
- Hướng dẫn về loại bài nói, thời lượng, cấu trúc và thiết kế slide chuyển sang
  `deck-planning/references/`.
- Bỏ quy trình "mỗi slide là một ảnh AI" của `scientific-slides`, vì nó đi ngược nguyên tắc
  mọi con số phải có nguồn. Ảnh AI cho từng hình vẫn có trong `medical-figures` và `generate-image`.
- Mô tả của `pptx` không còn tự nhận mọi yêu cầu "slides/presentation"; nó là bộ công cụ
  .pptx cấp thấp, còn bài thuyết trình mới đi qua `medical-deck`.

### Sửa lỗi
- Cổng duyệt kế hoạch (`hooks/talk.py`) không còn coi "isn't approved yet", "not yet been
  approved" hay "approved? no" là đã duyệt. Có từ phủ định là chặn.
- `lint_slop.py` báo lỗi chặn S00 khi không nhận ra slide nào, thay vì báo "0 lỗi".
- `lint_slop.py` quét theo từng khối (đoạn, tiêu đề, chú thích): mỗi lỗi trích đúng phần tử
  của nó và không bị báo trùng.
- `slop-audit` ghi rõ: S00–S04 được kiểm tra tự động, S05–S06 cần xem bằng mắt.

### Tính năng mới
- `lint_slop.py` và các script của `evidence-audit` đọc được PDF (mỗi trang một slide).
- Cổng duyệt kế hoạch chặn cả `latexmk`, `pdflatex`, `xelatex`, `lualatex`.
- Lệnh `/medskill-panda:status`: xem tiến độ từng bài thuyết trình và bước tiếp theo.
- `evidence-research`: nguồn Việt Nam (Quyết định của Bộ Y tế, Dược thư Quốc gia, tạp chí
  trong nước).
- Bộ test `tests/` (thư viện chuẩn `unittest`) và CI trên GitHub Actions.
- Hook không còn sinh thư mục `__pycache__` trong plugin.

## 1.0.0

- Phát hành đầu tiên: 38 skill, hook cho slide y khoa, lệnh `scientific-writer-init`.
