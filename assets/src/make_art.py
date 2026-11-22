"""Generate the README artwork as HTML pages (EN and VI), then screenshot them with shoot.js.

    python assets/src/make_art.py <out-dir>
    node assets/src/shoot.js <out-dir>/art_en.html <out-dir>/en 2
    node assets/src/shoot.js <out-dir>/art_vi.html <out-dir>/vi 2

shoot.js writes <prefix>-pipeline.png, <prefix>-slides.png and <prefix>-manuscript.png; copy
them to assets/pipeline(.vi).png, assets/example-slides(.vi).png and
assets/example-manuscript(.vi).png. The example images embed real output from
examples/demo-hf/ (run its scripts first; see examples/demo-hf/README.md).
"""
import base64
import sys as _sys
import html
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
_sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "examples" / "demo-hf"
e = html.escape


def img(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


# ------------------------------------------------------------------ icons (own drawings)
ICON = {
 "question": '<svg viewBox="0 0 48 48"><rect x="6" y="8" width="36" height="26" rx="8" fill="#E6F0F4" stroke="#0F5E7A" stroke-width="2.5"/><path d="M16 34l-4 8 10-8" fill="#E6F0F4" stroke="#0F5E7A" stroke-width="2.5" stroke-linejoin="round"/><path d="M20 17a4 4 0 1 1 5.5 3.7c-1 .5-1.5 1.3-1.5 2.3v1" fill="none" stroke="#0F5E7A" stroke-width="2.6" stroke-linecap="round"/><circle cx="24" cy="28.5" r="1.6" fill="#0F5E7A"/></svg>',
 "pdf": '<svg viewBox="0 0 48 48"><path d="M12 4h17l9 9v31H12z" fill="#fff" stroke="#56677F" stroke-width="2.5" stroke-linejoin="round"/><path d="M29 4v9h9" fill="none" stroke="#56677F" stroke-width="2.5"/><rect x="6" y="24" width="26" height="12" rx="3" fill="#C8372D"/><text x="19" y="33.2" font-size="9" font-weight="800" fill="#fff" text-anchor="middle" font-family="Inter,Arial">PDF</text></svg>',
 "data": '<svg viewBox="0 0 48 48"><rect x="7" y="8" width="34" height="32" rx="4" fill="#fff" stroke="#56677F" stroke-width="2.5"/><path d="M7 17h34M7 26h34M7 34h34M19 8v32" stroke="#56677F" stroke-width="2"/><rect x="23" y="29" width="4" height="9" fill="#C8372D"/><rect x="29" y="25" width="4" height="13" fill="#0F5E7A"/><rect x="35" y="21" width="4" height="17" fill="#0F5E7A" opacity=".5"/></svg>',
 "template": '<svg viewBox="0 0 48 48"><rect x="5" y="9" width="38" height="28" rx="4" fill="#fff" stroke="#56677F" stroke-width="2.5"/><rect x="5" y="9" width="38" height="7" rx="3" fill="#0F5E7A"/><circle cx="12" cy="24" r="3" fill="#C8372D"/><path d="M18 24h18M12 31h24" stroke="#C7D3DB" stroke-width="3" stroke-linecap="round"/><path d="M24 37v5M17 43h14" stroke="#56677F" stroke-width="2.5" stroke-linecap="round"/></svg>',
 "chat": '<svg viewBox="0 0 48 48"><rect x="4" y="6" width="30" height="22" rx="7" fill="#0F5E7A"/><circle cx="12" cy="17" r="2.6" fill="#fff"/><circle cx="19" cy="17" r="2.6" fill="#fff"/><circle cx="26" cy="17" r="2.6" fill="#fff"/><rect x="18" y="22" width="26" height="18" rx="6" fill="#F4D58D"/><path d="M24 31h14" stroke="#8A5B00" stroke-width="2.6" stroke-linecap="round"/></svg>',
 "plan": '<svg viewBox="0 0 48 48"><rect x="5" y="6" width="17" height="13" rx="3" fill="#fff" stroke="#0F5E7A" stroke-width="2.3"/><rect x="26" y="6" width="17" height="13" rx="3" fill="#fff" stroke="#0F5E7A" stroke-width="2.3"/><rect x="5" y="23" width="17" height="13" rx="3" fill="#fff" stroke="#0F5E7A" stroke-width="2.3"/><path d="M9 15l3-4 3 2 4-5" fill="none" stroke="#C8372D" stroke-width="2"/><circle cx="35" cy="33" r="9" fill="#1D7A3E"/><path d="M31 33l3 3 5-6" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/></svg>',
 "ledger": '<svg viewBox="0 0 48 48"><rect x="7" y="5" width="28" height="36" rx="3" fill="#fff" stroke="#0F5E7A" stroke-width="2.5"/><path d="M13 14h16M13 21h16M13 28h10" stroke="#9FB4C0" stroke-width="2.6" stroke-linecap="round"/><circle cx="33" cy="33" r="8" fill="#fff" stroke="#0F5E7A" stroke-width="3"/><path d="M39 39l5 5" stroke="#0F5E7A" stroke-width="3.5" stroke-linecap="round"/></svg>',
 "figure": '<svg viewBox="0 0 48 48"><path d="M7 6v34h36" fill="none" stroke="#56677F" stroke-width="2.5"/><path d="M10 10h8v6h7v6h8v5h7" fill="none" stroke="#C8372D" stroke-width="3"/><path d="M10 10h5v10h8v8h7v5h10" fill="none" stroke="#56677F" stroke-width="3"/></svg>',
 "deck": '<svg viewBox="0 0 48 48"><rect x="4" y="7" width="40" height="27" rx="4" fill="#fff" stroke="#C8372D" stroke-width="2.5"/><path d="M10 15h20" stroke="#18222D" stroke-width="3" stroke-linecap="round"/><path d="M10 27l6-5 5 3 7-7" fill="none" stroke="#C8372D" stroke-width="2.4"/><path d="M24 34v6M17 41h14" stroke="#56677F" stroke-width="2.5" stroke-linecap="round"/></svg>',
 "draft": '<svg viewBox="0 0 48 48"><path d="M9 4h22l8 8v32H9z" fill="#fff" stroke="#56677F" stroke-width="2.5" stroke-linejoin="round"/><path d="M15 16h12M15 22h18M15 28h18M15 34h11" stroke="#9FB4C0" stroke-width="2.5" stroke-linecap="round"/><path d="M33 26l8-8 4 4-8 8-5 1z" fill="#F4D58D" stroke="#8A5B00" stroke-width="2"/></svg>',
 "venue": '<svg viewBox="0 0 48 48"><path d="M6 18L24 7l18 11z" fill="#E6F0F4" stroke="#56677F" stroke-width="2.4" stroke-linejoin="round"/><path d="M11 20v15M19 20v15M29 20v15M37 20v15" stroke="#56677F" stroke-width="3"/><path d="M6 39h36" stroke="#56677F" stroke-width="3" stroke-linecap="round"/></svg>',
 "slop": '<svg viewBox="0 0 48 48"><rect x="4" y="8" width="30" height="22" rx="3" fill="#fff" stroke="#C8372D" stroke-width="2.4"/><path d="M9 15h12" stroke="#C8372D" stroke-width="2.6"/><circle cx="32" cy="30" r="10" fill="#fff" stroke="#C8372D" stroke-width="3"/><path d="M28 26l8 8M36 26l-8 8" stroke="#C8372D" stroke-width="3" stroke-linecap="round"/></svg>',
 "shield": '<svg viewBox="0 0 48 48"><path d="M24 4l16 6v12c0 10-7 18-16 22C15 40 8 32 8 22V10z" fill="#E5F4EA" stroke="#1D7A3E" stroke-width="2.6" stroke-linejoin="round"/><path d="M16 24l6 6 10-12" fill="none" stroke="#1D7A3E" stroke-width="3.2" stroke-linecap="round"/></svg>',
 "prose": '<svg viewBox="0 0 48 48"><rect x="5" y="7" width="38" height="34" rx="4" fill="#fff" stroke="#56677F" stroke-width="2.4"/><text x="15" y="23" font-size="11" font-weight="800" fill="#0F5E7A" font-family="Inter,Arial">VI</text><text x="27" y="35" font-size="11" font-weight="800" fill="#C8372D" font-family="Inter,Arial">EN</text><path d="M14 33l20-18" stroke="#9FB4C0" stroke-width="2"/></svg>',
 "deliver": '<svg viewBox="0 0 48 48"><rect x="4" y="6" width="40" height="28" rx="4" fill="#fff" stroke="#1D7A3E" stroke-width="2.6"/><path d="M10 26l7-7 6 4 9-9" fill="none" stroke="#C8372D" stroke-width="2.6"/><path d="M24 34v6M16 42h16" stroke="#18222D" stroke-width="2.6" stroke-linecap="round"/><circle cx="38" cy="10" r="7" fill="#1D7A3E"/><path d="M35 10l2.5 2.5L41 8" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/></svg>',
 "file": '<svg viewBox="0 0 20 24"><path d="M3 1h9l5 5v17H3z" fill="#fff" stroke="#8A99A6" stroke-width="1.6" stroke-linejoin="round"/><path d="M12 1v5h5" fill="none" stroke="#8A99A6" stroke-width="1.6"/></svg>',
 "folder": '<svg viewBox="0 0 24 20"><path d="M1 3h8l2 2.5h12V19H1z" fill="#F2C76B" stroke="#C99A2E" stroke-width="1.3" stroke-linejoin="round"/></svg>',
 "lock": '<svg viewBox="0 0 18 22"><rect x="1.5" y="9" width="15" height="12" rx="3" fill="currentColor"/><path d="M4.5 9V6.5a4.5 4.5 0 0 1 9 0V9" fill="none" stroke="currentColor" stroke-width="2.4"/></svg>',
 "check": '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" fill="currentColor"/><path d="M6 10.5l2.6 2.6L14 7.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/></svg>',
}
STAGE_COLOR = {1: "#0F5E7A", 2: "#0F5E7A", 3: "#2F6FD0", 4: "#C8372D", 5: "#C8372D", "4w": "#56677F", "5w": "#56677F", 6: "#9B3D9B", 7: "#1D7A3E"}

T = {
 "en": dict(
  head="How Medskill Panda works", head_sub="One evidence spine, two outputs, one audit. Every stage leaves a file.",
  inputs="Start with", inputs_sub="any of these", outs="writes", files_title="Your project folder",
  in_items=[("question", "Topic or question", ""), ("pdf", "Papers & guidelines", ""), ("data", "Your data", ""), ("template", "Template", "optional")],
  spine="Shared spine", spine_sub="medical-deck · works with you",
  c1=("Brief", "deck-grilling", "One round of numbered questions with a recommended answer each: audience, venue, language, format.", "brief.md", "You confirm the brief"),
  c2=("Plan / outline", "deck-planning · outline.md", "Assertion titles for slides; sections, claims and word budget for papers.", "plan.md", "You approve the plan"),
  c3=("Evidence ledger", "evidence-research", "Retrieved, never recalled.", "claims.json · claims.csv", "Each claim: value, source, locator, verbatim quote."),
  tracks="Two outputs", tracks_sub="fresh subagents · they work from files, not from the chat",
  lane_a="SLIDES", lane_b="WRITING",
  c4=("Figures", "medical-figures", "From data or the paper's own vectors; credits and licences."),
  c5=("Build the deck", "html · pptx · beamer", "Your template, speaker notes, no overflow."),
  c4w=("Draft", "scientific-writing", "Section by section; numbers only from data or sources."),
  c5w=("Venue & guideline", "venue-templates", "Word, LaTeX or Markdown; reporting checklist."),
  c6=("Audit", "independent reviewers, in parallel"),
  rev=[("slop", "Slop reviewer", "slop-audit", "Eyebrows, on-slide cues, process notes, placeholders"),
       ("shield", "Evidence reviewer", "evidence-audit", "Every number against its quote; PMID/DOI resolve; patient identifiers"),
       ("prose", "Manuscript audit", "lint_prose · audit-manuscript", "Stock phrases VI/EN, unsourced statistics, decimals, VI↔EN numbers")],
  pass_="No blocking findings → deliver", loop="otherwise the finding goes back to its stage · up to 3 rounds",
  folder="Deliver", folder_sub="with a record of every stage",
  files=[("file", "STATUS.md", ""), ("file", "brief.md", 1), ("file", "plan.md / outline.md", 2), ("folder", "evidence/", 3),
         ("folder", "figures/", 4), ("folder", "build/  out/", 5), ("folder", "drafts/", 5), ("folder", "audit/", 6)],
  folder_note="STATUS.md tracks every stage, so a later session picks up where this one stopped.",
  deliver="Deliver", deliver_files=".html · .pptx · .pdf · .docx",
  deliver_note="plus a report: what was verified against full text, abstract only, or not at all",
  ex_s="Example output · HTML deck", ex_s_sub="One offline file built by html-deck-building from simulated DEMO-HF data: figures drawn from the data, a source on every slide. lint_slop: 0 findings.",
  ex_p="Example output · PowerPoint in your template", ex_p_sub="The same talk built by pptx-deck-building inside a branded template: native, editable diagram and chart; speaker notes on every slide. check_pptx and lint_slop: 0 findings.",
  ex_m="Example output · manuscript", ex_m_sub="Word file from the same data: English text, Vietnamese abstract. Checked with lint_prose.",
  audit_hd="lint_prose: demo-hf.docx (vi+en): 1 error, 0 warnings",
  audit_rows=[("P01", "Corresponding author: [MISSING: authors to confirm]", "a gap only the authors can fill, left visible on purpose")],
  checks=["Abstract in English, Tóm tắt in Vietnamese", "0.75 in English, 0,75 in Vietnamese: no mixed-decimal warning", "Every number from results.json", "Converted to PDF with LibreOffice"],
  sim="All numbers are simulated for demonstration (seed 7).",
  ex_c="Chart gallery", ex_c_sub="Eight chart types drawn from the same simulated data by examples/demo-hf/make_charts.py. SVG, ready for HTML or PowerPoint decks and manuscripts.",
 ),
 "vi": dict(
  head="Medskill Panda hoạt động thế nào", head_sub="Một trục bằng chứng, hai đầu ra, một bước kiểm tra. Mỗi bước để lại một file.",
  inputs="Bắt đầu từ", inputs_sub="một hoặc nhiều thứ", outs="xuất ra", files_title="Thư mục dự án của bạn",
  in_items=[("question", "Chủ đề / câu hỏi", ""), ("pdf", "Bài báo & guideline", ""), ("data", "Dữ liệu", ""), ("template", "Template", "tuỳ chọn")],
  spine="Trục chung", spine_sub="medical-deck · làm cùng bạn",
  c1=("Brief", "deck-grilling", "Một lượt câu hỏi đánh số, mỗi câu có đáp án gợi ý: đối tượng, nơi công bố, ngôn ngữ, định dạng.", "brief.md", "Bạn xác nhận brief"),
  c2=("Kế hoạch / dàn ý", "deck-planning · outline.md", "Tiêu đề khẳng định cho slide; mục, nhận định và số chữ cho bài báo.", "plan.md", "Bạn duyệt kế hoạch"),
  c3=("Sổ bằng chứng", "evidence-research", "Tra cứu thật, không nhớ.", "claims.json · claims.csv", "Mỗi nhận định: giá trị, nguồn, vị trí, câu trích nguyên văn."),
  tracks="Hai đầu ra", tracks_sub="subagent mới cho mỗi bước · làm việc từ file, không từ cuộc trò chuyện",
  lane_a="SLIDE", lane_b="VIẾT BÀI",
  c4=("Hình", "medical-figures", "Từ dữ liệu hoặc vector gốc của bài báo; ghi nguồn và giấy phép."),
  c5=("Dựng slide", "html · pptx · beamer", "Theo template của bạn, có ghi chú người nói, không tràn chữ."),
  c4w=("Viết bản thảo", "scientific-writing", "Từng phần; số liệu chỉ từ dữ liệu hoặc nguồn."),
  c5w=("Tạp chí & guideline", "venue-templates", "Word, LaTeX hoặc Markdown; checklist báo cáo."),
  c6=("Kiểm tra", "các bộ kiểm tra độc lập, chạy song song"),
  rev=[("slop", "Kiểm tra slop", "slop-audit", "Nhãn eyebrow, gợi ý bấm trên slide, ghi chú quy trình, placeholder"),
       ("shield", "Kiểm tra bằng chứng", "evidence-audit", "Đối chiếu từng con số với câu trích; PMID/DOI; thông tin định danh"),
       ("prose", "Kiểm tra bản thảo", "lint_prose · audit-manuscript", "Cụm từ sáo VI/EN, thống kê thiếu nguồn, dấu thập phân, số lệch VI↔EN")],
  pass_="Không còn lỗi chặn → bàn giao", loop="nếu còn, lỗi quay về đúng bước gây ra · tối đa 3 vòng",
  folder="Bàn giao", folder_sub="kèm hồ sơ của từng bước",
  files=[("file", "STATUS.md", ""), ("file", "brief.md", 1), ("file", "plan.md / outline.md", 2), ("folder", "evidence/", 3),
         ("folder", "figures/", 4), ("folder", "build/  out/", 5), ("folder", "drafts/", 5), ("folder", "audit/", 6)],
  folder_note="STATUS.md ghi lại từng bước, nên phiên sau làm tiếp đúng chỗ đang dừng.",
  deliver="Bàn giao", deliver_files=".html · .pptx · .pdf · .docx",
  deliver_note="kèm báo cáo: đã kiểm chứng với toàn văn, chỉ tóm tắt, hay chưa kiểm chứng",
  ex_s="Ví dụ đầu ra · slide HTML", ex_s_sub="Một file offline do html-deck-building dựng từ dữ liệu mô phỏng DEMO-HF: hình vẽ từ dữ liệu, có nguồn trên mọi slide. lint_slop: 0 lỗi.",
  ex_p="Ví dụ đầu ra · PowerPoint theo template của bạn", ex_p_sub="Cùng bài nói do pptx-deck-building dựng trong một template có nhận diện riêng: sơ đồ và biểu đồ gốc sửa được, có ghi chú người nói trên mọi slide. check_pptx và lint_slop: 0 lỗi.",
  ex_m="Ví dụ đầu ra · bản thảo", ex_m_sub="File Word từ cùng bộ dữ liệu: nội dung tiếng Anh, tóm tắt tiếng Việt. Kiểm tra bằng lint_prose.",
  audit_hd="lint_prose: demo-hf.docx (vi+en): 1 lỗi, 0 cảnh báo",
  audit_rows=[("P01", "Corresponding author: [MISSING: authors to confirm]", "chỗ trống chỉ tác giả điền được, cố ý để lộ ra")],
  checks=["Abstract tiếng Anh, Tóm tắt tiếng Việt", "0.75 ở phần tiếng Anh, 0,75 ở phần tiếng Việt: không báo lẫn dấu thập phân", "Mọi con số lấy từ results.json", "Chuyển sang PDF bằng LibreOffice"],
  sim="Mọi con số là dữ liệu mô phỏng để minh hoạ (seed 7).",
  ex_c="Bộ sưu tập biểu đồ", ex_c_sub="Tám loại biểu đồ vẽ từ cùng bộ dữ liệu mô phỏng bằng examples/demo-hf/make_charts.py. Định dạng SVG, dùng được cho slide HTML, PowerPoint và bản thảo.",
 ),
}

CSS = """
:root{--teal:#0F5E7A;--red:#C8372D;--slate:#56677F;--ink:#18222D;--mute:#5F6E7B;--line:#DCE4EA;--green:#1D7A3E}
*{box-sizing:border-box}body{margin:0;background:#fff;font-family:Inter,"Segoe UI",Helvetica,Arial,sans-serif;color:var(--ink)}
.mono{font-family:ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace}
/* examples: journal-figure plates */
.plate{width:1680px;padding:40px 40px 44px;background:#FAF8F4;display:grid;grid-template-columns:330px 1fr;gap:40px;border-top:1px solid #E2DED6}
.cap .rule{width:56px;height:6px;background:var(--c)}
.cap .no{font:700 64px/1 'DejaVu Serif',Georgia,serif;color:var(--c);margin:18px 0 6px}
.cap h2{font:700 27px/1.2 'DejaVu Serif',Georgia,serif;margin:0 0 14px;color:#16212B}
.cap p{font-size:15.5px;line-height:1.5;color:#33414D;margin:0 0 20px}
.cap dl{margin:0;border-top:2px solid #16212B}
.cap dl div{display:grid;grid-template-columns:96px 1fr;gap:10px;padding:9px 0;border-bottom:1px solid #D9D4CB;font-size:14px}
.cap dt{font-weight:700;text-transform:uppercase;letter-spacing:.08em;font-size:11.5px;color:#6B6458;padding-top:2px}
.cap dd{margin:0;color:#16212B}.cap dd code{font:12.5px 'DejaVu Sans Mono',Menlo,monospace;background:#EFEBE3;padding:1px 5px}
.cap .ok{color:#2E7D4F;font-weight:700}
.cap .sim{margin-top:16px;font-size:12.5px;color:#8A5B00}
.frame{background:#fff;border:1px solid #CFC9BE}.frame img{display:block;width:100%}
.hero-row{display:grid;grid-template-columns:1fr;gap:14px}
.thumbs{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}
.thumbs figure{margin:0}.thumbs figcaption{font-size:12.5px;color:#55636F;margin-top:6px}
.thumbs figcaption b{color:#16212B;margin-right:4px}
.ms{display:grid;grid-template-columns:600px 1fr;gap:34px;align-items:start}
.page{position:relative}.mk{position:absolute;left:-15px;width:30px;height:30px;background:var(--c);color:#fff;font:700 16px/30px 'DejaVu Serif',Georgia,serif;text-align:center}
.callouts{margin:0;padding:0;list-style:none;border-top:2px solid #16212B}
.callouts li{display:grid;grid-template-columns:34px 1fr;gap:10px;padding:11px 0;border-bottom:1px solid #D9D4CB;font-size:15px;line-height:1.4}
.callouts li b{display:block;width:28px;height:28px;background:var(--c);color:#fff;font:700 15px/28px 'DejaVu Serif',Georgia,serif;text-align:center}
.callouts li span strong{display:block;color:#16212B}.callouts li span{color:#33414D}
.term{margin-top:22px;border:1px solid #CFC9BE;background:#fff}.term .hd{background:#16212B;color:#fff;padding:10px 14px;font:13px 'DejaVu Sans Mono',Menlo,monospace}
.term .row{padding:10px 14px;font:13.5px 'DejaVu Sans Mono',Menlo,monospace;color:#16212B}.term .row b{background:#B4362C;color:#fff;padding:1px 6px;margin-right:8px}
.cgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.panel{position:relative;background:#fff;border:1px solid #CFC9BE;padding:30px 6px 6px}.panel img{display:block;width:100%}
.panel .lt{position:absolute;left:0;top:0;width:28px;height:28px;background:#16212B;color:#fff;font:700 16px/28px 'DejaVu Serif',Georgia,serif;text-align:center}
"""

JOIN = '<div class="join"><svg viewBox="0 0 40 22"><path d="M2 11h32M26 3l9 8-9 8" fill="none" stroke="#8A99A6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
LOGO = (ROOT / "assets" / "logo.svg").read_text(encoding="utf-8")
LOGO = LOGO[LOGO.index("<svg"):].replace("<title>Medskill Panda</title>", "")


from swimlane import pipeline  # noqa: E402  (the 'How it works' figure)


PL = {
 "en": dict(
  sim="All numbers are simulated for demonstration (seed 7).",
  spec=("Format", "Built by", "Checks", "Data"),
  s=("01", "HTML slide deck", "One offline file with motion, speaker notes and a laser pointer. Titles state the conclusion; every figure is drawn from the data and every slide carries its source.",
     ["<code>.html</code>, 6 slides", "<code>html-deck-building</code>", "<span class=ok>lint_slop: 0 findings</span>", "simulated DEMO-HF trial"],
     ["Title", "Trial flow", "Subgroups", "Quality of life", "Bottom line"]),
  p=("02", "PowerPoint in your template", "The same talk inside a hospital or congress template. The trial diagram and the line chart are native PowerPoint objects you can edit; every slide has speaker notes.",
     ["<code>.pptx</code>, 6 slides", "<code>pptx-deck-building</code>", "<span class=ok>check_pptx, lint_slop: 0</span>", "simulated DEMO-HF trial"],
     ["Title", "Kaplan–Meier", "Subgroups", "Native line chart", "Bottom line"]),
  m=("03", "Manuscript, two languages", "A Word file written from the same data: English text with a Vietnamese abstract, a three-line table and a figure. The audit flags the one gap only the authors can fill.",
     ["<code>.docx</code> and PDF", "<code>scientific-writing</code>", "<span class=ok>lint_prose: 1 deliberate gap</span>", "simulated DEMO-HF trial"]),
  callouts=[("Banner", "The document says the data are simulated."), ("Explicit gap", "[MISSING: authors to confirm] instead of an invented author."),
            ("English abstract", "Numbers written 0.75, 95% CI 0.63–0.89."), ("Tóm tắt (Vietnamese)", "Same numbers written 0,75; KTC 95% 0,63–0,89."),
            ("Table 1", "Baseline characteristics computed from the data.")],
  c=("04", "Charts from data", "Eight chart types common in medical talks and papers, drawn from the same simulated data as SVG, with labels in the deck's language.",
     ["SVG, English and Vietnamese", "<code>make_charts.py</code>", "values in <code>values.json</code>", "simulated DEMO-HF trial"]),
 ),
 "vi": dict(
  sim="Mọi con số là dữ liệu mô phỏng để minh hoạ (seed 7).",
  spec=("Định dạng", "Dựng bằng", "Kiểm tra", "Dữ liệu"),
  s=("01", "Slide HTML", "Một file offline có chuyển động, ghi chú người nói và bút laser. Tiêu đề nói kết luận; mọi hình vẽ từ dữ liệu, mọi slide ghi nguồn.",
     ["<code>.html</code>, 6 slide", "<code>html-deck-building</code>", "<span class=ok>lint_slop: 0 lỗi</span>", "thử nghiệm mô phỏng DEMO-HF"],
     ["Tiêu đề", "Dòng bệnh nhân", "Phân nhóm", "Chất lượng sống", "Kết luận"]),
  p=("02", "PowerPoint theo template", "Cùng bài nói, dựng trong template bệnh viện hoặc hội nghị. Sơ đồ thử nghiệm và biểu đồ đường là đối tượng gốc của PowerPoint, sửa được; slide nào cũng có ghi chú.",
     ["<code>.pptx</code>, 6 slide", "<code>pptx-deck-building</code>", "<span class=ok>check_pptx, lint_slop: 0</span>", "thử nghiệm mô phỏng DEMO-HF"],
     ["Tiêu đề", "Kaplan–Meier", "Phân nhóm", "Biểu đồ đường gốc", "Kết luận"]),
  m=("03", "Bản thảo hai ngôn ngữ", "File Word viết từ cùng bộ dữ liệu: nội dung tiếng Anh, tóm tắt tiếng Việt, bảng ba đường kẻ và hình. Bộ kiểm tra chỉ ra chỗ trống duy nhất mà tác giả phải tự điền.",
     ["<code>.docx</code> và PDF", "<code>scientific-writing</code>", "<span class=ok>lint_prose: 1 chỗ trống cố ý</span>", "thử nghiệm mô phỏng DEMO-HF"]),
  callouts=[("Dòng cảnh báo", "Bài ghi rõ dữ liệu là mô phỏng."), ("Chỗ trống rõ ràng", "[MISSING: authors to confirm] thay vì bịa tên tác giả."),
            ("Abstract tiếng Anh", "Số viết 0.75, 95% CI 0.63–0.89."), ("Tóm tắt tiếng Việt", "Cùng số liệu viết 0,75; KTC 95% 0,63–0,89."),
            ("Bảng 1", "Đặc điểm nền tính từ dữ liệu.")],
  c=("04", "Biểu đồ từ dữ liệu", "Tám loại biểu đồ hay gặp trong slide và bài báo y khoa, vẽ từ cùng bộ dữ liệu mô phỏng, xuất SVG, nhãn theo ngôn ngữ của bài.",
     ["SVG, tiếng Anh và tiếng Việt", "<code>make_charts.py</code>", "giá trị trong <code>values.json</code>", "thử nghiệm mô phỏng DEMO-HF"]),
 ),
}
COLORS = {"s": "#B4362C", "p": "#0F5E7A", "m": "#7A3E7A", "c": "#2C5F9E"}


def caption(L, key, extra=""):
    q, no, title, desc, spec = PL[L], *PL[L][key][:4]
    rows = "".join(f"<div><dt>{e(h)}</dt><dd>{v}</dd></div>" for h, v in zip(q["spec"], spec))
    return (f'<div class="cap"><div class="rule"></div><div class="no">{no}</div><h2>{e(title)}</h2><p>{e(desc)}</p>'
            f'<dl>{rows}</dl>{extra}<div class="sim">{e(q["sim"])}</div></div>')


def deck_plate(L, key, files, hero, pid):
    names = PL[L][key][4]
    others = [i for i in range(1, 7) if i != hero]
    thumbs = "".join(f'<figure><div class="frame"><img src="{img(DEMO / "screens" / files.format(i=i))}"></div>'
                     f'<figcaption><b>{i}</b>{e(n)}</figcaption></figure>' for i, n in zip(others, names))
    return (f'<div class="plate" id="{pid}" style="--c:{COLORS[key]}">{caption(L, key)}<div class="hero-row">'
            f'<div class="frame"><img src="{img(DEMO / "screens" / files.format(i=hero))}"></div><div class="thumbs">{thumbs}</div></div></div>')


def examples(L):
    q = PL[L]
    slides = deck_plate(L, "s", L + "-{i}.png", 3, "slides")
    pptx = deck_plate(L, "p", "pptx-" + L + "-{i}.png", 2, "pptx")
    marks_y = (7.3, 16.9, 23.0, 41.0, 69.3)  # % of the page height, matched to the rendered page
    marks = "".join(f'<span class="mk" style="top:calc({y}% - 15px)">{k}</span>' for k, y in enumerate(marks_y, 1))
    callouts = "".join(f'<li><b>{k}</b><span><strong>{e(h)}</strong>{e(b)}</span></li>' for k, (h, b) in enumerate(q["callouts"], 1))
    term = (f'<div class="term"><div class="hd">$ lint_prose.py demo-hf.docx</div>'
            f'<div class="row"><b>P01</b>[MISSING: authors to confirm]</div></div>')
    ms = (f'<div class="plate" id="manuscript" style="--c:{COLORS["m"]}">{caption(L, "m")}<div class="ms">'
          f'<div class="page frame">{marks}<img src="{img(DEMO / "screens" / "page1.png")}"></div>'
          f'<div><ol class="callouts">{callouts}</ol>{term}'
          f'<div class="frame" style="margin-top:22px;width:470px"><img src="{img(DEMO / "screens" / "page2-figure.png")}"></div></div></div></div>')
    charts = "".join(f'<div class="panel"><span class="lt">{"ABCDEFGH"[k]}</span>'
                     f'<img src="data:image/svg+xml;base64,{base64.b64encode(f.read_bytes()).decode()}"></div>'
                     for k, f in enumerate(sorted((DEMO / "out" / "charts" / L).glob("*.svg"))))
    gallery = f'<div class="plate" id="charts" style="--c:{COLORS["c"]}">{caption(L, "c")}<div class="cgrid">{charts}</div></div>'
    return slides + pptx + ms + gallery


OUT.mkdir(parents=True, exist_ok=True)
for L in ("en", "vi"):
    page = (f'<!doctype html><html lang="{L}"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body>{pipeline(L)}{examples(L)}</body></html>')
    (OUT / f"art_{L}.html").write_text(page, encoding="utf-8")
print("ok")
