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
  inputs="Your materials", inputs_sub="any of these",
  in_items=[("question", "Topic or clinical question", ""), ("pdf", "Papers & guidelines", "PDF"), ("data", "Your data & results", "for papers"), ("template", "Your template", "optional")],
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
  folder="Project folder", folder_sub="one file per stage",
  files=[("file", "STATUS.md", ""), ("file", "brief.md", 1), ("file", "plan.md / outline.md", 2), ("folder", "evidence/", 3),
         ("folder", "figures/", 4), ("folder", "build/  out/", 5), ("folder", "drafts/", 5), ("folder", "audit/", 6)],
  folder_note="STATUS.md tracks every stage, so a later session picks up where this one stopped.",
  deliver="Deliver", deliver_files=".html · .pptx<br>.pdf · .docx",
  deliver_note="plus a report: what was verified against full text, abstract only, or not at all",
  ex_s="Example output · slide deck", ex_s_sub="Built with medical-deck → html-deck-building from simulated DEMO-HF data. lint_slop: 0 blocking.",
  ex_m="Example output · manuscript", ex_m_sub="Word file from the same data: English text, Vietnamese abstract. Checked with lint_prose.",
  audit_hd="lint_prose: demo-hf.docx (vi+en): 1 error, 0 warnings",
  audit_rows=[("P01", "Corresponding author: [MISSING: authors to confirm]", "a gap only the authors can fill, left visible on purpose")],
  checks=["Abstract in English, Tóm tắt in Vietnamese", "0.75 in English, 0,75 in Vietnamese: no mixed-decimal warning", "Every number from results.json", "Converted to PDF with LibreOffice"],
  sim="All numbers are simulated for demonstration (seed 7).",
 ),
 "vi": dict(
  inputs="Tư liệu của bạn", inputs_sub="một hoặc nhiều thứ",
  in_items=[("question", "Chủ đề hoặc câu hỏi lâm sàng", ""), ("pdf", "Bài báo & guideline", "PDF"), ("data", "Dữ liệu & kết quả", "cho bài báo"), ("template", "Template của bạn", "tuỳ chọn")],
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
  folder="Thư mục dự án", folder_sub="mỗi bước một file",
  files=[("file", "STATUS.md", ""), ("file", "brief.md", 1), ("file", "plan.md / outline.md", 2), ("folder", "evidence/", 3),
         ("folder", "figures/", 4), ("folder", "build/  out/", 5), ("folder", "drafts/", 5), ("folder", "audit/", 6)],
  folder_note="STATUS.md ghi lại từng bước, nên phiên sau làm tiếp đúng chỗ đang dừng.",
  deliver="Bàn giao", deliver_files=".html · .pptx<br>.pdf · .docx",
  deliver_note="kèm báo cáo: đã kiểm chứng với toàn văn, chỉ tóm tắt, hay chưa kiểm chứng",
  ex_s="Ví dụ đầu ra · bộ slide", ex_s_sub="Dựng bằng medical-deck → html-deck-building từ dữ liệu mô phỏng DEMO-HF. lint_slop: 0 lỗi chặn.",
  ex_m="Ví dụ đầu ra · bản thảo", ex_m_sub="File Word từ cùng bộ dữ liệu: nội dung tiếng Anh, tóm tắt tiếng Việt. Kiểm tra bằng lint_prose.",
  audit_hd="lint_prose: demo-hf.docx (vi+en): 1 lỗi, 0 cảnh báo",
  audit_rows=[("P01", "Corresponding author: [MISSING: authors to confirm]", "chỗ trống chỉ tác giả điền được, cố ý để lộ ra")],
  checks=["Abstract tiếng Anh, Tóm tắt tiếng Việt", "0.75 ở phần tiếng Anh, 0,75 ở phần tiếng Việt: không báo lẫn dấu thập phân", "Mọi con số lấy từ results.json", "Chuyển sang PDF bằng LibreOffice"],
  sim="Mọi con số là dữ liệu mô phỏng để minh hoạ (seed 7).",
 ),
}

CSS = """
:root{--teal:#0F5E7A;--red:#C8372D;--slate:#56677F;--ink:#18222D;--mute:#5F6E7B;--line:#DCE4EA;--green:#1D7A3E}
*{box-sizing:border-box}body{margin:0;background:#fff;font-family:Inter,"Segoe UI",Helvetica,Arial,sans-serif;color:var(--ink)}
.mono{font-family:ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace}
#pipeline{width:1680px;padding:30px 34px 30px 26px;background:#fff;display:grid;grid-template-columns:172px 22px 410px 22px 1fr 22px 232px;align-items:stretch}
.col h3{margin:0;font-size:22px;text-align:center;letter-spacing:-.01em}.col .hs{margin:3px 0 14px;text-align:center;color:var(--mute);font-size:13.5px}
.inputs{padding:14px 6px;display:flex;flex-direction:column}.inputs .it{display:flex;flex-direction:column;align-items:center;text-align:center;margin:12px 0 18px}
.inputs .it svg{width:58px;height:58px}.inputs .it b{font-size:15px;margin-top:6px}.inputs .it span{font-size:13px;color:var(--mute)}
.arrow{display:flex;align-items:center;justify-content:center}.arrow svg{width:22px;height:30px}
.panel{border-radius:22px;padding:18px 16px 16px;border:2px solid}
.spine{background:#EEF6F9;border-color:#B9D6E1}.tracks{background:#F3F2FA;border-color:#CFCBEA}
.card{background:#fff;border-radius:16px;padding:14px 16px 14px 18px;box-shadow:0 2px 0 rgba(24,34,45,.04),0 6px 18px rgba(24,34,45,.06);position:relative;margin-bottom:14px;border-left:5px solid var(--c)}
.card:last-child{margin-bottom:0}.card .hd{display:flex;gap:12px;align-items:center}
.n{width:34px;height:34px;border-radius:50%;background:var(--c);color:#fff;font-weight:800;display:grid;place-items:center;font-size:17px;flex:none}
.card h4{margin:0;font-size:21px;letter-spacing:-.01em}.card .sk{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;color:var(--mute)}
.card .ic{margin-left:auto;width:48px;height:48px;flex:none}.card p{margin:9px 0 0;font-size:14.5px;line-height:1.38;color:#33414D}
.pill{display:inline-block;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;background:#F1F4F6;border:1px solid var(--line);border-radius:8px;padding:3px 8px;margin:8px 6px 0 0}
.chip{display:inline-block;font-size:12.5px;border-radius:999px;padding:3px 10px;margin:6px 5px 0 0;background:#EAF1FB;color:#1F4E8C;border:1px solid #C9DAF3}
.gate{margin-top:10px;display:flex;gap:8px;align-items:center;border-radius:999px;padding:7px 12px;font-weight:700;font-size:14px}
.gate svg{width:15px;height:17px}.gate.y{background:#FFF6DC;color:#8A5B00;border:1.5px solid #EBC764}.gate.r{background:#FDECEA;color:#A82B22;border:1.5px solid #EDB1AA}
.lane{display:grid;grid-template-columns:28px 1fr 1fr;gap:12px;align-items:stretch;margin-bottom:12px}
.lane .lb{writing-mode:vertical-rl;transform:rotate(180deg);text-align:center;font-weight:800;letter-spacing:.2em;font-size:12.5px;color:var(--c);border-radius:10px;background:#fff;border:1.5px solid var(--line)}
.lane .card{margin:0}
.audit{background:#fff;border-radius:16px;padding:14px 16px;box-shadow:0 6px 18px rgba(24,34,45,.06);border-left:5px solid #9B3D9B;margin-top:4px}
.revs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}
.rev{border-radius:12px;padding:10px 12px;border:1.5px solid var(--line);background:#FBFCFD}.rev .t{display:flex;gap:8px;align-items:center;font-weight:700;font-size:15px}
.rev svg{width:30px;height:30px;flex:none}.rev .sk{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--mute);margin-top:3px}.rev p{margin:6px 0 0;font-size:13px;color:#33414D;line-height:1.35}
.pass{display:flex;gap:16px;align-items:center;margin-top:12px;font-size:14px}.pass .ok{white-space:nowrap;flex:none;display:flex;gap:8px;align-items:center;background:#E5F4EA;color:var(--green);border:1.5px solid #A9D8B8;border-radius:999px;padding:6px 14px;font-weight:700}
.pass .ok svg{width:18px;height:18px;color:var(--green)}.pass i{color:var(--red)}
.side{display:flex;flex-direction:column;gap:16px}
.folder{background:#FFF9EC;border:2px solid #F0D9A2;border-radius:22px;padding:16px 16px}
.folder .f{display:flex;gap:10px;align-items:center;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px;padding:6px 2px;border-bottom:1px dashed #EAD9B0}
.folder .f:last-of-type{border-bottom:0}.folder .f svg{width:18px;height:20px;flex:none}.folder .f .b{margin-left:auto;width:22px;height:22px;border-radius:50%;color:#fff;font:700 12px Inter,Arial;display:grid;place-items:center}
.folder .note{font-size:13px;color:var(--mute);margin-top:10px;line-height:1.4;text-align:center}
.deliver{background:#ECF7F0;border:2px solid #A9D8B8;border-radius:22px;padding:16px;text-align:center}
.deliver h3{display:flex;gap:10px;align-items:center;justify-content:center;margin:0;font-size:22px}.deliver svg.big{width:86px;height:86px;margin:8px auto 4px;display:block}
.deliver .fx{font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:700;font-size:15px}.deliver p{font-size:13px;color:var(--mute);margin:6px 0 0;line-height:1.4}
/* examples */
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

ARROW = '<div class="arrow"><svg viewBox="0 0 22 30"><path d="M3 4l14 11L3 26" fill="none" stroke="#7E8E9B" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'


def card(n, color, title, skill, body, icon, extra=""):
    return (f'<div class="card" style="--c:{color}"><div class="hd"><span class="n">{n}</span><div><h4>{e(title)}</h4>'
            f'<div class="sk">{e(skill)}</div></div><span class="ic">{ICON[icon]}</span></div><p>{e(body)}</p>{extra}</div>')


def pipeline(L):
    t = T[L]
    inputs = "".join(f'<div class="it">{ICON[i]}<b>{e(a)}</b><span>{e(b)}</span></div>' for i, a, b in t["in_items"])
    c1 = card(1, STAGE_COLOR[1], t["c1"][0], t["c1"][1], t["c1"][2], "chat",
              f'<span class="pill">{t["c1"][3]}</span><div class="gate y">{ICON["check"].replace("currentColor", "#C99A2E")}{e(t["c1"][4])}</div>')
    c2 = card(2, STAGE_COLOR[2], t["c2"][0], t["c2"][1], t["c2"][2], "plan",
              f'<span class="pill">{t["c2"][3]}</span><div class="gate r">{ICON["lock"]}{e(t["c2"][4])}</div>')
    chips = "".join(f'<span class="chip">{s}</span>' for s in ("PubMed", "Europe PMC", "ClinicalTrials.gov", "OpenAlex", "Crossref", "Bộ Y tế"))
    c3 = card(3, STAGE_COLOR[3], t["c3"][0], t["c3"][1], t["c3"][2], "ledger",
              f'<div>{chips}</div><span class="pill">{t["c3"][3]}</span><p>{e(t["c3"][4])}</p>')
    lane_a = (f'<div class="lane" style="--c:{STAGE_COLOR[4]}"><div class="lb">{t["lane_a"]}</div>'
              + card(4, STAGE_COLOR[4], *t["c4"], "figure") + card(5, STAGE_COLOR[5], *t["c5"], "deck") + '</div>')
    lane_b = (f'<div class="lane" style="--c:{STAGE_COLOR["4w"]}"><div class="lb">{t["lane_b"]}</div>'
              + card(4, STAGE_COLOR["4w"], *t["c4w"], "draft") + card(5, STAGE_COLOR["5w"], *t["c5w"], "venue") + '</div>')
    revs = "".join(f'<div class="rev"><div class="t">{ICON[i]}{e(a)}</div><div class="sk">{e(b)}</div><p>{e(c)}</p></div>' for i, a, b, c in t["rev"])
    audit = (f'<div class="audit"><div class="hd" style="display:flex;gap:12px;align-items:center"><span class="n" style="--c:{STAGE_COLOR[6]};background:{STAGE_COLOR[6]}">6</span>'
             f'<div><h4 style="margin:0;font-size:21px">{e(t["c6"][0])}</h4><div class="sk" style="font-size:13px;color:#5F6E7B">{e(t["c6"][1])}</div></div></div>'
             f'<div class="revs">{revs}</div><div class="pass"><span class="ok">{ICON["check"]}{e(t["pass_"])}</span><i>↺ {e(t["loop"])}</i></div></div>')
    files = "".join(f'<div class="f">{ICON[k]}<span>{e(name)}</span>'
                    + (f'<span class="b" style="background:{STAGE_COLOR[n]}">{n}</span>' if n else "") + '</div>' for k, name, n in t["files"])
    side = (f'<div class="side"><div class="folder"><h3 style="margin:0;text-align:center;font-size:21px">{e(t["folder"])}</h3>'
            f'<div class="hs" style="text-align:center;color:#5F6E7B;font-size:13px;margin:2px 0 8px">{e(t["folder_sub"])}</div>{files}'
            f'<div class="note">{e(t["folder_note"])}</div></div>'
            f'<div class="deliver"><h3><span class="n" style="background:{STAGE_COLOR[7]}">7</span>{e(t["deliver"])}</h3>{ICON["deliver"].replace("<svg ", "<svg class=\"big\" ")}'
            f'<div class="fx">{t["deliver_files"]}</div><p>{e(t["deliver_note"])}</p></div></div>')
    return (f'<div id="pipeline"><div class="col inputs"><h3>{e(t["inputs"])}</h3><div class="hs">{e(t["inputs_sub"])}</div>{inputs}</div>{ARROW}'
            f'<div class="col panel spine"><h3>{e(t["spine"])}</h3><div class="hs mono">{e(t["spine_sub"])}</div>{c1}{c2}{c3}</div>{ARROW}'
            f'<div class="col panel tracks"><h3>{e(t["tracks"])}</h3><div class="hs">{e(t["tracks_sub"])}</div>{lane_a}{lane_b}{audit}</div>{ARROW}'
            f'{side}</div>')


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
    return slides + ms


OUT.mkdir(parents=True, exist_ok=True)
for L in ("en", "vi"):
    page = (f'<!doctype html><html lang="{L}"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body>{pipeline(L)}{examples(L)}</body></html>')
    (OUT / f"art_{L}.html").write_text(page, encoding="utf-8")
print("ok")
