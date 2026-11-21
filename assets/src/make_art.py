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
import html
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
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
  ex_s="Example output · slide deck", ex_s_sub="Built with medical-deck → html-deck-building from simulated DEMO-HF data. lint_slop: 0 blocking.",
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
  ex_s="Ví dụ đầu ra · bộ slide", ex_s_sub="Dựng bằng medical-deck → html-deck-building từ dữ liệu mô phỏng DEMO-HF. lint_slop: 0 lỗi chặn.",
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
#pipeline{width:1680px;background:#fff;padding:0 0 30px}
.band{background:linear-gradient(115deg,#0B4F67,#137A9C);color:#fff;padding:22px 34px;display:flex;align-items:center;gap:18px;border-radius:0 0 30px 30px}
.band .logo svg{width:66px;height:66px;display:block}.band h2{margin:0;font-size:30px;letter-spacing:-.01em}.band p{margin:4px 0 0;opacity:.85;font-size:15px}
.start{margin-left:auto;display:flex;gap:9px;align-items:center;flex-wrap:wrap;justify-content:flex-end;max-width:820px}
.start .lab{font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;opacity:.85;margin-right:2px;font-weight:700}
.sc{display:flex;gap:8px;align-items:center;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.28);border-radius:12px;padding:6px 12px 6px 6px;font-size:14px}
.sc svg{width:30px;height:30px;background:#fff;border-radius:8px;padding:2px;flex:none}.sc small{opacity:.75;margin-left:2px}
.sec{padding:0 34px}
.sec-t{display:flex;align-items:center;gap:12px;margin:24px 0 12px;font-weight:800;font-size:13.5px;letter-spacing:.18em;text-transform:uppercase;color:#5F6E7B}
.sec-t:after{content:"";flex:1;height:2px;background:#E3E9EE}.sec-t span{color:#18222D;letter-spacing:0;text-transform:none;font-weight:500;font-size:14px}
.row3{display:grid;grid-template-columns:1fr 46px 1fr 46px 1fr;align-items:stretch}
.join{display:flex;align-items:center;justify-content:center}.join svg{width:40px;height:22px}
.tile{background:#fff;border:1.5px solid #E1E7EC;border-radius:18px;box-shadow:0 8px 22px rgba(24,34,45,.07);overflow:hidden;display:flex;flex-direction:column}
.tile .bar{height:7px;background:var(--c)}.tile .in{padding:14px 18px 16px;flex:1;display:flex;flex-direction:column}
.tile .hd{display:flex;gap:13px;align-items:center}
.sq{width:38px;height:38px;border-radius:11px;background:var(--c);color:#fff;font-weight:800;display:grid;place-items:center;font-size:18px;flex:none;transform:rotate(-6deg);box-shadow:0 3px 0 rgba(0,0,0,.12)}
.tile h4{margin:0;font-size:20px;letter-spacing:-.01em}.tile .sk{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;color:var(--mute)}
.tile .ic{margin-left:auto;width:46px;height:46px;flex:none}.tile p{margin:9px 0 0;font-size:14.5px;line-height:1.4;color:#33414D}
.pill{display:inline-block;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;background:#F1F4F6;border:1px solid var(--line);border-radius:8px;padding:3px 8px;margin:8px 6px 0 0}
.chip{display:inline-block;font-size:12.5px;border-radius:999px;padding:3px 10px;margin:6px 5px 0 0;background:#EAF1FB;color:#1F4E8C;border:1px solid #C9DAF3}
.rib{margin:12px -18px -16px;padding:9px 18px;font-weight:700;font-size:14px;display:flex;gap:9px;align-items:center;margin-top:auto}
.rib svg{width:16px;height:18px}.rib.y{background:#FFF4D6;color:#8A5B00}.rib.r{background:#FDE7E4;color:#A82B22}.rib.b{background:#E8F0FC;color:#1F4E8C}
.fork{display:block;width:1612px;height:56px}
.lanes{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.lane{border-radius:24px;border:2px dashed var(--c);padding:0 16px 16px;background:var(--bg);position:relative}
.lane .tab{display:inline-block;margin:-15px 0 10px 18px;background:var(--c);color:#fff;font-weight:800;letter-spacing:.18em;font-size:13px;padding:6px 16px;border-radius:999px}
.lane .pair{display:grid;grid-template-columns:1fr 34px 1fr;align-items:stretch}.lane .join svg{width:28px}
.lane .outs{margin-top:12px;display:flex;gap:8px;align-items:center;font-size:13.5px;color:var(--mute)}
.lane .outs b{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;color:var(--c);background:#fff;border:1.5px solid var(--c);border-radius:8px;padding:3px 9px}
.audit-band .in{padding:16px 20px}.revs{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px}
.rev{border-radius:14px;padding:12px 14px;border:1.5px solid var(--line);background:#FBFCFD;display:flex;gap:12px}
.rev svg{width:38px;height:38px;flex:none}.rev b{font-size:15.5px}.rev .sk{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--mute);margin-top:2px}
.rev p{margin:5px 0 0;font-size:13.5px;color:#33414D;line-height:1.35}
.pass{display:flex;gap:18px;align-items:center;margin-top:14px;font-size:14px}.pass .ok{white-space:nowrap;display:flex;gap:8px;align-items:center;background:#E5F4EA;color:var(--green);border:1.5px solid #A9D8B8;border-radius:999px;padding:6px 14px;font-weight:700}
.pass .ok svg{width:18px;height:18px;color:var(--green)}.pass i{color:var(--red)}
.foot{display:grid;grid-template-columns:420px 1fr;gap:22px}
.deliver p{font-size:13.5px}
.deliver .fx{font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:700;font-size:15px;margin-top:6px}
.files{background:#FFF9EC;border:1.5px solid #F0D9A2;border-radius:18px;padding:14px 18px}
.files .fl{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.files .f{display:flex;gap:8px;align-items:center;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13.5px;background:#fff;border:1px solid #EAD9B0;border-radius:10px;padding:6px 8px 6px 10px}
.files .f svg{width:16px;height:18px;flex:none}.files .f .b{width:21px;height:21px;border-radius:6px;color:#fff;font:700 11.5px Inter,Arial;display:grid;place-items:center}
.files .note{font-size:13px;color:var(--mute);margin-top:10px}
/* examples */
.cgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.chart{background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:8px;box-shadow:0 6px 18px rgba(24,34,45,.06)}.chart img{display:block;width:100%}
.ex{width:1680px;padding:32px 34px;background:#fff}
.ex h2{margin:0;font-size:28px;letter-spacing:-.01em}.ex .sub{margin:6px 0 20px;color:var(--mute);font-size:16px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.shot{border-radius:14px;overflow:hidden;border:1.5px solid var(--line);box-shadow:0 10px 28px rgba(24,34,45,.10)}.shot img{display:block;width:100%}
.sim{margin-top:14px;font-size:13px;color:#8A5B00}
.ms{display:grid;grid-template-columns:720px 1fr;gap:34px;align-items:start}
.page{border:1.5px solid var(--line);box-shadow:0 12px 30px rgba(24,34,45,.12);border-radius:6px;overflow:hidden;background:#fff}.page img{display:block;width:100%}
.term{border-radius:14px;overflow:hidden;border:1.5px solid var(--line);margin-bottom:18px}.term .hd{background:var(--teal);color:#fff;padding:12px 16px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px}
.term .row{display:flex;gap:12px;padding:12px 16px;align-items:baseline;flex-wrap:wrap}.term b{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;background:var(--red);color:#fff;border-radius:5px;padding:2px 7px}
.term .why{width:100%;color:var(--mute);font-size:13.5px;padding-left:44px}
.checks div{display:flex;gap:10px;align-items:center;font-size:15.5px;padding:9px 0;border-bottom:1px solid #EEF2F5}.checks svg{width:20px;height:20px;color:var(--green);flex:none}
.figcrop{margin-top:18px;border:1.5px solid var(--line);border-radius:10px;overflow:hidden;width:520px;background:#fff}.figcrop img{display:block;width:100%}
"""

JOIN = '<div class="join"><svg viewBox="0 0 40 22"><path d="M2 11h32M26 3l9 8-9 8" fill="none" stroke="#8A99A6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
LOGO = (ROOT / "assets" / "logo.svg").read_text(encoding="utf-8")
LOGO = LOGO[LOGO.index("<svg"):].replace("<title>Medskill Panda</title>", "")


def tile(n, color, title, skill, body, icon, extra="", cls=""):
    num = f'<span class="sq" style="--c:{color}">{n}</span>' if n else ""
    return (f'<div class="tile {cls}" style="--c:{color}"><div class="bar"></div><div class="in"><div class="hd">{num}<div><h4>{e(title)}</h4>'
            f'<div class="sk">{e(skill)}</div></div><span class="ic">{ICON[icon]}</span></div>'
            + (f'<p>{e(body)}</p>' if body else "") + f'{extra}</div></div>')


def fork(merge=False):
    """Connector from the spine's centre to the two lane centres (or back, when merge)."""
    w, h, c, a, b = 1612, 56, 806, 393, 1219
    if merge:
        d = f"M{a} 0 V18 Q{a} 28 {a+10} 28 H{b-10} Q{b} 28 {b} 18 V0 M{c} 28 V{h-4}"
        tip = f'<path d="M{c-8} {h-12} L{c} {h-2} L{c+8} {h-12}" fill="none" stroke="#8A99A6" stroke-width="3" stroke-linecap="round"/>'
    else:
        d = f"M{c} 0 V24 M{a} {h-2} V38 Q{a} 28 {a+10} 28 H{b-10} Q{b} 28 {b} 38 V{h-2}"
        tip = "".join(f'<path d="M{x-8} {h-12} L{x} {h-2} L{x+8} {h-12}" fill="none" stroke="#8A99A6" stroke-width="3" stroke-linecap="round"/>' for x in (a, b))
    return f'<svg class="fork" viewBox="0 0 {w} {h}"><path d="{d}" fill="none" stroke="#8A99A6" stroke-width="3" stroke-linecap="round"/>{tip}</svg>'


def pipeline(L):
    t = T[L]
    starts = "".join(f'<span class="sc">{ICON[i]}{e(a)}{f"<small>· {e(b)}</small>" if b else ""}</span>' for i, a, b in t["in_items"])
    band = (f'<div class="band"><span class="logo">{LOGO}</span><div><h2>{e(t["head"])}</h2><p>{e(t["head_sub"])}</p></div>'
            f'<div class="start"><span class="lab">{e(t["inputs"])}</span>{starts}</div></div>')
    chips = "".join(f'<span class="chip">{s}</span>' for s in ("PubMed", "Europe PMC", "ClinicalTrials.gov", "OpenAlex", "Crossref", "Bộ Y tế"))
    s1 = tile(1, STAGE_COLOR[1], t["c1"][0], t["c1"][1], t["c1"][2], "chat",
              f'<div><span class="pill">{t["c1"][3]}</span></div><div class="rib y">{ICON["check"].replace("currentColor", "#C99A2E")}{e(t["c1"][4])}</div>')
    s2 = tile(2, STAGE_COLOR[2], t["c2"][0], t["c2"][1], t["c2"][2], "plan",
              f'<div><span class="pill">{t["c2"][3]}</span></div><div class="rib r">{ICON["lock"]}{e(t["c2"][4])}</div>')
    s3 = tile(3, STAGE_COLOR[3], t["c3"][0], t["c3"][1], t["c3"][2], "ledger",
              f'<div>{chips}</div><div class="rib b">{ICON["check"].replace("currentColor", "#2F6FD0")}{e(t["c3"][4])}</div>')
    spine = f'<div class="sec"><div class="sec-t">{e(t["spine"])} <span>· {e(t["spine_sub"])}</span></div><div class="row3">{s1}{JOIN}{s2}{JOIN}{s3}</div></div>'

    def lane(tab, color, bg, a, b, ia, ib, outs):
        o = "".join(f"<b>{x}</b>" for x in outs)
        return (f'<div class="lane" style="--c:{color};--bg:{bg}"><span class="tab">{tab}</span><div class="pair">'
                + tile(4, color, *a, ia) + JOIN + tile(5, color, *b, ib) + f'</div><div class="outs">{e(t["outs"])} {o}</div></div>')

    lanes = (f'<div class="sec">{fork()}<div class="lanes">'
             + lane(t["lane_a"], STAGE_COLOR[4], "#FFF7F6", t["c4"], t["c5"], "figure", "deck", (".html", ".pptx", ".pdf"))
             + lane(t["lane_b"], STAGE_COLOR["4w"], "#F6F8FA", t["c4w"], t["c5w"], "draft", "venue", (".docx", ".tex", ".md"))
             + f'</div>{fork(True)}</div>')
    revs = "".join(f'<div class="rev">{ICON[i]}<div><b>{e(a)}</b><div class="sk">{e(b)}</div><p>{e(c)}</p></div></div>' for i, a, b, c in t["rev"])
    audit = tile(6, STAGE_COLOR[6], t["c6"][0], t["c6"][1], "", "shield",
                 f'<div class="revs">{revs}</div><div class="pass"><span class="ok">{ICON["check"]}{e(t["pass_"])}</span><i>↺ {e(t["loop"])}</i></div>',
                 cls="audit-band")
    files = "".join(f'<span class="f">{ICON[k]}{e(name)}' + (f'<span class="b" style="background:{STAGE_COLOR[n]}">{n}</span>' if n else "") + '</span>'
                    for k, name, n in t["files"])
    deliver = tile(7, STAGE_COLOR[7], t["deliver"], "", "", "deliver",
                   f'<div class="fx">{t["deliver_files"]}</div><p>{e(t["deliver_note"])}</p>', cls="deliver")
    foot = (f'<div class="sec"><div class="sec-t">{e(t["folder"])} <span>· {e(t["folder_sub"])}</span></div><div class="foot">{deliver}'
            f'<div class="files"><b>{e(t["files_title"])}</b><div class="fl">{files}</div><div class="note">{e(t["folder_note"])}</div></div></div></div>')
    return f'<div id="pipeline">{band}{spine}{lanes}<div class="sec">{audit}</div>{foot}</div>'


def examples(L):
    t = T[L]
    shots = "".join(f'<div class="shot"><img src="{img(DEMO / "screens" / f"{L}-{i}.png")}"></div>' for i in range(1, 5))
    slides = (f'<div class="ex" id="slides"><h2>{e(t["ex_s"])}</h2><p class="sub">{e(t["ex_s_sub"])}</p>'
              f'<div class="grid">{shots}</div><div class="sim">{e(t["sim"])}</div></div>')
    rows = "".join(f'<div class="row"><b>{i}</b><span>{e(x)}</span><span class="why">{e(w)}</span></div>' for i, x, w in t["audit_rows"])
    checks = "".join(f'<div>{ICON["check"]}<span>{e(c)}</span></div>' for c in t["checks"])
    ms = (f'<div class="ex" id="manuscript"><h2>{e(t["ex_m"])}</h2><p class="sub">{e(t["ex_m_sub"])}</p>'
          f'<div class="ms"><div class="page"><img src="{img(DEMO / "screens" / "page1.png")}"></div>'
          f'<div><div class="term"><div class="hd">{e(t["audit_hd"])}</div>{rows}</div><div class="checks">{checks}</div>'
          f'<div class="figcrop"><img src="{img(DEMO / "screens" / "page2-figure.png")}"></div>'
          f'<div class="sim">{e(t["sim"])}</div></div></div></div>')
    charts = "".join(f'<div class="chart"><img src="data:image/svg+xml;base64,{base64.b64encode(f.read_bytes()).decode()}"></div>'
                     for f in sorted((DEMO / "out" / "charts" / L).glob("*.svg")))
    gallery = (f'<div class="ex" id="charts"><h2>{e(t["ex_c"])}</h2><p class="sub">{e(t["ex_c_sub"])}</p>'
               f'<div class="cgrid">{charts}</div><div class="sim">{e(t["sim"])}</div></div>')
    return slides + ms + gallery


OUT.mkdir(parents=True, exist_ok=True)
for L in ("en", "vi"):
    page = (f'<!doctype html><html lang="{L}"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body>{pipeline(L)}{examples(L)}</body></html>')
    (OUT / f"art_{L}.html").write_text(page, encoding="utf-8")
print("ok")
