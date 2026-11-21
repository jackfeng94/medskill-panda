# Changelog

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
