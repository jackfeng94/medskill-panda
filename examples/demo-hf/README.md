# DEMO-HF example · Ví dụ DEMO-HF

**English.** A complete example built with this plugin's own tools from **simulated data**
(seed 7). It is not a real study; every number in it is computed by `make_data.py` and
stored in `out/results.json`.

| Output | File |
|--------|------|
| HTML deck (English, Vietnamese), one offline file each | `deck_en/out/demo-hf.html`, `deck_vi/out/demo-hf.html` |
| Manuscript (Word, English text with a Vietnamese abstract) and its PDF | `manuscript/demo-hf.docx`, `manuscript/demo-hf.pdf` |
| Figures and every computed number | `out/` |
| Screenshots used in the main README | `screens/` |

The decks pass `lint_slop.py` with 0 findings. `lint_prose.py` reports one error on the
manuscript, on purpose: `[MISSING: authors to confirm]`, a gap only the authors can fill.

Rebuild everything (needs numpy, matplotlib, python-docx, pymupdf, LibreOffice and Node
Playwright):

```bash
sh examples/demo-hf/build.sh
```

**Tiếng Việt.** Ví dụ trọn vẹn dựng bằng chính công cụ của plugin từ **dữ liệu mô phỏng**
(seed 7). Đây không phải nghiên cứu thật; mọi con số do `make_data.py` tính và lưu trong
`out/results.json`. Mở `deck_vi/out/demo-hf.html` để xem bộ slide tiếng Việt, và
`manuscript/demo-hf.docx` để xem bản thảo (nội dung tiếng Anh, tóm tắt tiếng Việt). Dựng lại
toàn bộ bằng lệnh `build.sh` ở trên.
