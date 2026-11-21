# Changelog

## Unreleased

- Ảnh README làm lại: sơ đồ quy trình dạng cột thẻ (tư liệu → trục chung → hai tuyến slide và
  viết bài → kiểm tra → thư mục dự án và bàn giao), cùng ảnh đầu ra thật của bộ slide và bản
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
