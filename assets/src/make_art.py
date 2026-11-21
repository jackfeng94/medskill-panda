"""Generate the README artwork (pipeline map + feature cards) as HTML pages, EN and VI.

    python assets/src/make_art.py <out-dir>
    node assets/src/shoot.js <out-dir>/art_en.html assets/hi-en 2     (needs Playwright)

shoot.js writes <prefix>-pipeline.png and <prefix>-cards.png; copy them to
assets/pipeline.png and assets/features.png (and the .vi variants from art_vi.html).
Cards 3 and 4 quote real output of lint_slop.py and lint_prose.py; rerun those tools
and update SLOP and PROSE below if their rules change.
"""
import html
import sys
from pathlib import Path

OUT = Path(sys.argv[1])

T = {
 "en": {
  "title": "One evidence spine, two outputs",
  "sub": "Every stage writes a file, so a later session picks up where this one stopped.",
  "in": "Your materials", "in_items": ["Topic or clinical question", "Papers & guidelines (PDF)", "Your data & results", "Hospital / congress template"],
  "s1": ("Brief", "deck-grilling · interview", "one round of questions"),
  "s2": ("Plan / outline", "deck-planning", "you approve it"),
  "s3": ("Evidence ledger", "evidence-research", "value · source · locator · quote"),
  "s4a": ("Figures", "medical-figures", "from data, with credits"),
  "s5a": ("Slides", "HTML · PPTX · Beamer", "your template"),
  "s4b": ("Manuscript", "scientific-writing", "Word · LaTeX · Markdown · VI / EN"),
  "s6": ("Audit", "slop · evidence · prose", "no blocking findings"),
  "s7": ("Deliver", "file + report", "what was verified"),
  "line_a": "SLIDES", "line_b": "WRITING", "loop": "fix loop · finding goes back to its stage",
  "leg_stage": "stage", "leg_gate": "you approve", "leg_hook": "hook enforces",
  "src": "Free sources", "hooks": "Hooks",
  "hook_items": ["route → medical-deck", "plan gate on build/ out/", "slop check on save"],
  # cards
  "c1": "Every number has a source", "c1s": "A claim on a slide or in a paper is a record, not a memory.",
  "c1_slide": "Hospital admissions fell by", "c1_val": "26%",
  "c1_src": "DEMO-HF trial · Table 2, p. 6", "c1_quote": "“…admissions were 26% lower in the intervention group…”",
  "c1_status": "verified-fulltext", "c1_note": "Illustrative example",
  "c1_ledger": [("c07", "26%", "full text", False), ("c08", "HR 0.74", "full text", False), ("c09", "NNT 21", "derived", False), ("c10", "1.8 days", "abstract only", True)],
  "c3_after": "After the fix: Admissions fell by a quarter",
  "c2": "Nothing is built before you approve", "c2s": "STATUS.md records each stage; the hook reads it.",
  "c2_rows": [("1", "Interview", "done"), ("2", "Template", "done"), ("3", "Plan", "waiting for you"), ("4", "Evidence", "todo"), ("6", "Build", "todo")],
  "c2_hook": "plan gate: build/ and out/ stay closed until you approve plan.md",
  "c3": "Slop is caught on save", "c3s": "Real output of lint_slop.py on a saved slide.",
  "c4": "Manuscript audit, Vietnamese and English", "c4s": "Real output of lint_prose.py on a Vietnamese draft compared with its English version.",
  "c4_notes": {"P02": "stock phrase", "P03": "overstatement", "P04": "statistic without citation", "P05": "report p < 0.001", "P09": "differs from EN version"},
 },
 "vi": {
  "title": "Một trục bằng chứng, hai đầu ra",
  "sub": "Mỗi bước ghi thành file, nên phiên sau làm tiếp đúng chỗ đang dừng.",
  "in": "Tư liệu của bạn", "in_items": ["Chủ đề hoặc câu hỏi lâm sàng", "Bài báo & guideline (PDF)", "Dữ liệu & kết quả của bạn", "Template bệnh viện / hội nghị"],
  "s1": ("Brief", "deck-grilling · phỏng vấn", "một lượt câu hỏi"),
  "s2": ("Kế hoạch / dàn ý", "deck-planning", "bạn duyệt"),
  "s3": ("Sổ bằng chứng", "evidence-research", "giá trị · nguồn · vị trí · trích dẫn"),
  "s4a": ("Hình", "medical-figures", "từ dữ liệu, ghi nguồn"),
  "s5a": ("Slide", "HTML · PPTX · Beamer", "theo template của bạn"),
  "s4b": ("Bản thảo", "scientific-writing", "Word · LaTeX · Markdown · VI / EN"),
  "s6": ("Kiểm tra", "slop · evidence · prose", "không còn lỗi chặn"),
  "s7": ("Bàn giao", "file + báo cáo", "đã kiểm chứng gì"),
  "line_a": "SLIDE", "line_b": "VIẾT BÀI", "loop": "vòng sửa · lỗi quay về đúng bước gây ra",
  "leg_stage": "bước", "leg_gate": "bạn duyệt", "leg_hook": "hook giám sát",
  "src": "Nguồn miễn phí", "hooks": "Hook",
  "hook_items": ["định tuyến → medical-deck", "khoá build/ out/ chờ duyệt", "quét slop khi lưu"],
  "c1": "Mỗi con số đều có nguồn", "c1s": "Một nhận định trên slide hay trong bài là một bản ghi, không phải trí nhớ.",
  "c1_slide": "Tỷ lệ nhập viện giảm", "c1_val": "26%",
  "c1_src": "Thử nghiệm DEMO-HF · Bảng 2, tr. 6", "c1_quote": "“…admissions were 26% lower in the intervention group…”",
  "c1_status": "verified-fulltext", "c1_note": "Ví dụ minh hoạ",
  "c1_ledger": [("c07", "26%", "toàn văn", False), ("c08", "HR 0,74", "toàn văn", False), ("c09", "NNT 21", "tính ra", False), ("c10", "1,8 ngày", "chỉ tóm tắt", True)],
  "c3_after": "Sau khi sửa: Tỷ lệ nhập viện giảm một phần tư",
  "c2": "Chưa duyệt thì chưa dựng", "c2s": "STATUS.md ghi từng bước; hook đọc file này.",
  "c2_rows": [("1", "Phỏng vấn", "done"), ("2", "Template", "done"), ("3", "Kế hoạch", "chờ bạn duyệt"), ("4", "Bằng chứng", "todo"), ("6", "Dựng slide", "todo")],
  "c2_hook": "cổng duyệt: build/ và out/ khoá cho đến khi bạn duyệt plan.md",
  "c3": "Slop bị bắt ngay khi lưu", "c3s": "Kết quả thật của lint_slop.py trên một slide vừa lưu.",
  "c4": "Kiểm tra bản thảo tiếng Việt và tiếng Anh", "c4s": "Kết quả thật của lint_prose.py trên bản thảo tiếng Việt, so với bản tiếng Anh.",
  "c4_notes": {"P02": "cụm từ sáo", "P03": "phóng đại", "P04": "thống kê thiếu trích dẫn", "P05": "ghi p < 0,001", "P09": "lệch với bản EN"},
 },
}
SOURCES = ["PubMed", "Europe PMC", "ClinicalTrials.gov", "OpenAlex", "Crossref", "Bộ Y tế"]
SLOP = [("S01", "03 · RESULTS · ITT", 'class="eyebrow"'), ("S02", "▸ Click for next: subgroups", ""),
        ("S03", "Original Figure 2, recoloured", "")]
PROSE = [("P02", "đóng vai trò then chốt"), ("P03", "chứng minh rằng"), ("P03", "hoàn toàn an toàn"),
         ("P04", "50%"), ("P05", "p = 0.000"), ("P09", "120 ↔ 112")]

CSS = """
:root{--teal:#0F5E7A;--teal2:#2C8AA8;--red:#C8372D;--slate:#56677F;--ink:#18222D;--mute:#617080;--line:#D9E2E8;--bg:#F6F9FA;--amber:#C98A12}
*{box-sizing:border-box}body{margin:0;background:#fff;font-family:Inter,"Segoe UI",Helvetica,Arial,sans-serif;color:var(--ink)}
.mono{font-family:ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace}
#pipeline{width:1600px;padding:44px 40px 36px;background:linear-gradient(180deg,#fff, #F3F8FA)}
#pipeline h1{margin:0;font-size:34px;letter-spacing:-.01em}#pipeline .sub{margin:6px 0 0;color:var(--mute);font-size:18px}
svg text{font-family:Inter,"Segoe UI",Helvetica,Arial,sans-serif}
.foot{display:flex;gap:28px;align-items:center;margin-top:4px;flex-wrap:wrap;font-size:15px;color:var(--mute)}
.foot b{color:var(--ink);margin-right:6px}.chip{display:inline-block;border:1.5px solid var(--line);border-radius:999px;padding:4px 12px;margin:3px 4px 3px 0;background:#fff;color:var(--ink);font-size:14px}
.chip.h{border-color:#BFD8E2;background:#EAF4F8}
#cards{width:1600px;padding:36px 40px;display:grid;grid-template-columns:1fr 1fr;gap:26px;background:#fff}
.card{border:1.5px solid var(--line);border-radius:18px;padding:26px 28px 40px;background:var(--bg);position:relative}
.card h2{margin:0 0 4px;font-size:25px;letter-spacing:-.01em;display:flex;gap:12px;align-items:center}
.card .num{width:34px;height:34px;border-radius:10px;background:var(--teal);color:#fff;display:grid;place-items:center;font-size:18px;flex:none}
.card .lead{margin:0 0 18px;color:var(--mute);font-size:16px}
.pair{display:flex;align-items:center}.slide{background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:22px 24px;flex:1;font-size:23px;font-weight:700;line-height:1.25}
.arrow{width:46px;height:2px;background:var(--red);position:relative;flex:none}.arrow:before,.arrow:after{content:"";position:absolute;top:-5px;width:12px;height:12px;border-radius:50%;background:var(--red)}.arrow:before{left:-6px}.arrow:after{right:-6px}
.ledger{margin-top:16px;display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.lg{background:#fff;border:1.5px solid var(--line);border-radius:10px;padding:8px 10px;font-size:13px}
.lg .v{font-weight:700;font-size:15px;color:var(--ink)}.lg .k{font-family:ui-monospace,Menlo,Consolas,monospace;color:var(--mute);font-size:11.5px}
.lg.ab{border-color:#F0D49A;background:#FFFAF0}.after{margin-top:16px;display:flex;align-items:center;gap:14px}
.after .mini{flex:1;background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:16px 20px;font-size:19px;font-weight:700}
.after .pass{background:#E5F4EA;color:#1D7A3E;border-radius:8px;padding:8px 12px;font-size:14px;font-weight:700;white-space:nowrap}
.hl{color:var(--red);border-bottom:3px solid var(--red)}
.src{flex:1.15;background:#fff;border:1.5px solid #BFD8E2;border-radius:12px;padding:16px 18px;font-size:15px}
.src .t{font-weight:700;margin-bottom:6px}.src .q{color:var(--mute);font-style:italic;margin-bottom:10px}
.ok{display:inline-block;background:#E5F4EA;color:#1D7A3E;border-radius:6px;padding:3px 9px;font-size:13px;font-weight:600}
.note{position:absolute;left:28px;bottom:18px;font-size:13px;color:var(--mute)}
table{border-collapse:collapse;width:100%;background:#fff;border:1.5px solid var(--line);border-radius:12px;overflow:hidden;font-size:16px}
td{padding:9px 14px;border-top:1px solid #EDF1F4}tr:first-child td{border-top:0}td.n{width:42px;color:var(--mute)}
.st{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px;padding:2px 8px;border-radius:6px}
.done{background:#E5F4EA;color:#1D7A3E}.todo{background:#EEF1F4;color:var(--mute)}.wait{background:#FDF1DC;color:#8A5B00;font-weight:700}
.gate{margin-top:14px;display:flex;gap:12px;align-items:center;background:#18222D;color:#E8EEF2;border-radius:10px;padding:12px 16px;font-size:14px}
.lock{flex:none}
.out{background:#fff;border:1.5px solid var(--line);border-radius:12px;overflow:hidden;font-size:15.5px}
.out .hd{background:var(--teal);color:#fff;padding:10px 16px;font-size:14px}
.row{display:flex;gap:12px;padding:9px 16px;border-top:1px solid #EDF1F4;align-items:baseline}
.row b{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;padding:2px 7px;border-radius:5px;color:#fff;background:var(--red);flex:none}
.row b.w{background:var(--amber)}.row .why{margin-left:auto;color:var(--mute);font-size:13.5px;white-space:nowrap}
"""


def station(x, y, name, skill, desc, color, gate=False, below=False, anchor="middle"):
    e = html.escape
    r = 15
    out = []
    if gate:
        out.append(f'<circle cx="{x}" cy="{y}" r="{r+9}" fill="#fff" stroke="{color}" stroke-width="4"/>')
    out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{color}" stroke-width="6"/>')
    if gate:  # small lock glyph
        out.append(f'<g transform="translate({x-7},{y-8})"><rect x="0" y="6" width="14" height="10" rx="2" fill="{color}"/>'
                   f'<path d="M3 6V4a4 4 0 0 1 8 0v2" fill="none" stroke="{color}" stroke-width="2.4"/></g>')
    dy = 52 if below else -66
    out.append(f'<text x="{x}" y="{y+dy}" text-anchor="{anchor}" font-size="21" font-weight="700" fill="#18222D">{e(name)}</text>')
    out.append(f'<text x="{x}" y="{y+dy+22}" text-anchor="{anchor}" font-size="14" fill="{color}" class="mono" font-family="ui-monospace,Menlo,Consolas,monospace">{e(skill)}</text>')
    out.append(f'<text x="{x}" y="{y+dy+42}" text-anchor="{anchor}" font-size="14.5" fill="#617080">{e(desc)}</text>')
    return "\n".join(out)


def pipeline(L):
    t = T[L]
    teal, red, slate = "#0F5E7A", "#C8372D", "#56677F"
    y0, ya, yb = 300, 165, 445
    xs = {"s1": 372, "s2": 545, "s3": 725, "j1": 835, "s4a": 945, "s5a": 1125, "s4b": 1035, "j2": 1235, "s6": 1325, "s7": 1440}
    parts = []
    # inputs
    parts.append(f'<text x="28" y="{y0-118}" font-size="15" font-weight="700" fill="#617080" letter-spacing=".08em">{html.escape(t["in"].upper())}</text>')
    for i, item in enumerate(t["in_items"]):
        yy = y0 - 88 + i * 52
        parts.append(f'<rect x="28" y="{yy}" width="236" height="38" rx="19" fill="#fff" stroke="#D9E2E8" stroke-width="1.5"/>')
        parts.append(f'<text x="44" y="{yy+24}" font-size="13.5" fill="#18222D">{html.escape(item)}</text>')
        parts.append(f'<path d="M264 {yy+19} C 290 {yy+19}, 295 {y0}, {xs["s1"]-24} {y0}" fill="none" stroke="#C7D3DB" stroke-width="2"/>')
    # lines
    parts.append(f'<path d="M{xs["s1"]} {y0} H{xs["j1"]}" stroke="{teal}" stroke-width="12" stroke-linecap="round" fill="none"/>')
    parts.append(f'<path d="M{xs["j1"]} {y0} C {xs["j1"]+40} {y0}, {xs["j1"]+30} {ya}, {xs["j1"]+90} {ya} H{xs["j2"]-90} '
                 f'C {xs["j2"]-30} {ya}, {xs["j2"]-40} {y0}, {xs["j2"]} {y0}" stroke="{red}" stroke-width="12" fill="none" stroke-linecap="round"/>')
    parts.append(f'<path d="M{xs["j1"]} {y0} C {xs["j1"]+40} {y0}, {xs["j1"]+30} {yb}, {xs["j1"]+90} {yb} H{xs["j2"]-90} '
                 f'C {xs["j2"]-30} {yb}, {xs["j2"]-40} {y0}, {xs["j2"]} {y0}" stroke="{slate}" stroke-width="12" fill="none" stroke-linecap="round"/>')
    parts.append(f'<path d="M{xs["j2"]} {y0} H{xs["s7"]}" stroke="{teal}" stroke-width="12" stroke-linecap="round" fill="none"/>')
    # fix loop (dashed) from audit back to evidence, under the writing line
    parts.append(f'<path d="M{xs["s6"]} {y0+104} C {xs["s6"]} 690, {xs["s3"]} 690, {xs["s3"]} {y0+34}" fill="none" stroke="{red}" stroke-width="2.5" stroke-dasharray="8 7"/>')
    parts.append(f'<path d="M{xs["s3"]-8} {y0+48} L{xs["s3"]} {y0+32} L{xs["s3"]+8} {y0+48}" fill="none" stroke="{red}" stroke-width="2.5"/>')
    parts.append(f'<text x="{(xs["s3"]+xs["s6"])//2}" y="640" text-anchor="middle" font-size="14.5" fill="{red}" font-weight="600">{html.escape(t["loop"])}</text>')
    # line labels
    parts.append(f'<text x="{(xs["j1"]+xs["j2"])//2}" y="{ya+44}" text-anchor="middle" font-size="13" font-weight="800" letter-spacing=".18em" fill="{red}">{t["line_a"]}</text>')
    parts.append(f'<text x="{(xs["j1"]+xs["j2"])//2}" y="{yb-30}" text-anchor="middle" font-size="13" font-weight="800" letter-spacing=".18em" fill="{slate}">{t["line_b"]}</text>')
    # stations
    parts.append(station(xs["s1"], y0, *t["s1"], teal))
    parts.append(station(xs["s2"], y0, *t["s2"], teal, gate=True, below=True))
    parts.append(station(xs["s3"], y0, *t["s3"], teal))
    parts.append(station(xs["s4a"], ya, *t["s4a"], red))
    parts.append(station(xs["s5a"], ya, *t["s5a"], red))
    parts.append(station(xs["s4b"], yb, *t["s4b"], slate, below=True))
    parts.append(station(xs["s6"], y0, *t["s6"], teal, gate=True, below=True))
    parts.append(station(xs["s7"], y0, *t["s7"], teal, anchor="middle"))
    # hook markers (small shield) on gated stations
    for x in (xs["s2"], xs["s6"]):
        parts.append(f'<g transform="translate({x-12},{y0-62})"><path d="M10 0 L20 4 V11 C20 17 15 21 10 23 C5 21 0 17 0 11 V4 Z" fill="#EAF4F8" stroke="{teal}" stroke-width="2"/>'
                     f'<path d="M5 11 l4 4 l7 -8" fill="none" stroke="{teal}" stroke-width="2.4"/></g>')
    # legend
    lx, ly = 1150, 690
    parts.append(f'<circle cx="{lx}" cy="{ly}" r="9" fill="#fff" stroke="{teal}" stroke-width="4"/><text x="{lx+18}" y="{ly+5}" font-size="14" fill="#617080">{t["leg_stage"]}</text>')
    parts.append(f'<circle cx="{lx+90}" cy="{ly}" r="13" fill="#fff" stroke="{teal}" stroke-width="3"/><circle cx="{lx+90}" cy="{ly}" r="7" fill="#fff" stroke="{teal}" stroke-width="3"/><text x="{lx+112}" y="{ly+5}" font-size="14" fill="#617080">{t["leg_gate"]}</text>')
    parts.append(f'<g transform="translate({lx+215},{ly-12})"><path d="M10 0 L20 4 V11 C20 17 15 21 10 23 C5 21 0 17 0 11 V4 Z" fill="#EAF4F8" stroke="{teal}" stroke-width="2"/></g><text x="{lx+243}" y="{ly+5}" font-size="14" fill="#617080">{t["leg_hook"]}</text>')
    svg = f'<svg width="1520" height="712" viewBox="0 0 1520 712" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'
    foot = (f'<div class="foot"><span><b>{t["src"]}</b>' + "".join(f'<span class="chip">{s}</span>' for s in SOURCES) + '</span>'
            f'<span><b>{t["hooks"]}</b>' + "".join(f'<span class="chip h mono">{h}</span>' for h in t["hook_items"]) + '</span></div>')
    return f'<div id="pipeline"><h1>{t["title"]}</h1><p class="sub">{t["sub"]}</p>{svg}{foot}</div>'


def cards(L):
    t, e = T[L], html.escape
    lock = ('<svg class="lock" width="18" height="22" viewBox="0 0 18 22"><rect x="1" y="9" width="16" height="12" rx="3" fill="#E8B04B"/>'
            '<path d="M4 9V6a5 5 0 0 1 10 0v3" fill="none" stroke="#E8B04B" stroke-width="2.6"/></svg>')
    rows = "".join(f'<tr><td class="n">{n}</td><td>{e(s)}</td><td style="text-align:right"><span class="st {"done" if st=="done" else "todo" if st=="todo" else "wait"}">{e(st)}</span></td></tr>'
                   for n, s, st in t["c2_rows"])
    slop = "".join(f'<div class="row"><b>{i}</b><span>{e(x)}</span><span class="why mono">{e(n)}</span></div>' for i, x, n in SLOP)
    prose = "".join(f'<div class="row"><b class="w">{i}</b><span>{e(x)}</span><span class="why">{e(t["c4_notes"][i])}</span></div>' for i, x in PROSE)
    ledger = "".join(f'<div class="lg{" ab" if ab else ""}"><div class="k">{k}</div><div class="v">{e(v)}</div><div>{e(s)}</div></div>'
                     for k, v, s, ab in t["c1_ledger"])
    return f'''<div id="cards">
<div class="card"><h2><span class="num">1</span>{e(t["c1"])}</h2><p class="lead">{e(t["c1s"])}</p>
 <div class="pair"><div class="slide">{e(t["c1_slide"])} <span class="hl">{t["c1_val"]}</span></div><div class="arrow"></div>
 <div class="src"><div class="t">{e(t["c1_src"])}</div><div class="q">{e(t["c1_quote"])}</div><span class="ok mono">✓ {t["c1_status"]}</span>
 <div class="mono" style="margin-top:10px;font-size:12.5px;color:#617080">claims.json · c07 · kind: observed</div></div></div>
 <div class="ledger">{ledger}</div>
 <div class="note">{e(t["c1_note"])}</div></div>
<div class="card"><h2><span class="num">2</span>{e(t["c2"])}</h2><p class="lead">{e(t["c2s"])}</p>
 <table>{rows}</table><div class="gate mono">{lock}<span>{e(t["c2_hook"])}</span></div></div>
<div class="card"><h2><span class="num">3</span>{e(t["c3"])}</h2><p class="lead">{e(t["c3s"])}</p>
 <div class="out"><div class="hd mono"># lint_slop: slides.html: 3 blocking, 0 advisory</div>{slop}</div>
 <div class="after"><div class="mini">{e(t["c3_after"])}</div><span class="pass mono">✓ 0 blocking</span></div></div>
<div class="card"><h2><span class="num">4</span>{e(t["c4"])}</h2><p class="lead">{e(t["c4s"])}</p>
 <div class="out"><div class="hd mono"># lint_prose: draft_vi.md (vi) --compare draft_en.md</div>{prose}</div></div>
</div>'''


for L in ("en", "vi"):
    page = f'<!doctype html><html lang="{L}"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{pipeline(L)}{cards(L)}</body></html>'
    (OUT / f"art_{L}.html").write_text(page, encoding="utf-8")
print("ok")
