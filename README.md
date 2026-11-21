# Medskill Panda

Plugin Claude Code của **Nguyen-Minh-Tan Phung** (pnmtan.med@gmail.com), gồm hai nhóm tính năng:

1. **Slide y khoa có kiểm chứng**: phỏng vấn để chốt brief → lập kế hoạch → tra cứu PubMed/ClinicalTrials → vẽ hình (Kaplan–Meier, CONSORT, cơ chế) → dựng HTML hoặc PPTX theo template bệnh viện → kiểm tra số liệu, trích dẫn và "AI slop".
2. **Viết khoa học**: bài báo, tổng quan tài liệu, đề cương/xin tài trợ, poster LaTeX/PPTX, quản lý trích dẫn, peer review, báo cáo lâm sàng, phác đồ, sơ đồ khoa học, xử lý DOCX/PDF/PPTX/XLSX.

## Cài đặt

Repo: https://github.com/jackfeng94/medskill-panda

Trong Claude Code:

```bash
claude plugin marketplace add jackfeng94/medskill-panda
```

```bash
claude plugin install medskill-panda@medskill-panda
```

Hoặc trong phiên Claude Code, gõ `/plugin marketplace add jackfeng94/medskill-panda` rồi `/plugin install medskill-panda@medskill-panda`.

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

## Các skill (38)

**Thuyết trình y khoa** — `medical-deck` (điểm bắt đầu), `deck-grilling`, `deck-planning`, `evidence-research`, `medical-figures`, `html-deck-building`, `pptx-deck-building`, `template-matching`, `evidence-audit`, `slop-audit`, `/audit-deck`, `/grill-deck`.

**Viết & nghiên cứu** — `scientific-writing`, `literature-review`, `research-lookup`, `citation-management`, `peer-review`, `scientific-critical-thinking`, `scholar-evaluation`, `hypothesis-generation`, `research-grants`, `venue-templates`, `market-research-reports`.

**Lâm sàng** — `clinical-reports`, `clinical-decision-support`, `treatment-plans` (chỉ dùng cho tài liệu nghiên cứu/đã khử định danh; mọi đầu ra cần người có chuyên môn duyệt).

**Hình ảnh & trình bày** — `scientific-slides`, `scientific-schematics`, `infographics`, `generate-image`, `latex-posters`, `pptx-posters`.

**Tệp & web** — `docx`, `pdf`, `pptx`, `xlsx`, `markitdown`, `parallel-web`.

**Lệnh** — `/medskill-panda:scientific-writer-init` cài CLAUDE.md/AGENTS.md cho dự án viết.

## Hook

Chỉ hoạt động khi làm slide: nhắc bắt đầu từ `medical-deck`, khoá thư mục `build/` và `out/` đến khi `plan.md` được duyệt, và quét slop sau mỗi lần lưu slide. Cần Python 3.8+; không có Python thì hook tự bỏ qua.

## Khoá API (tuỳ chọn)

Một số skill gọi dịch vụ ngoài: `OPENROUTER_API_KEY` (generate-image, scientific-schematics, infographics, slide ảnh AI), `PARALLEL_API_KEY` (parallel-web, research-lookup). Các skill còn lại chạy không cần khoá.

## Giấy phép

MIT. Xem `LICENSE` và `NOTICE.md`.
