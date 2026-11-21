"""The 'How it works' figure: a two-lane flowchart (what you do / what Medskill Panda does).

Plain SVG in the style of a journal figure: square boxes, thin rules, one accent colour, every
arrow labelled with what is handed over. Used by make_art.py.
"""
import html

e = html.escape
INK, MUTE, RULE, TEAL, AMBER, RED = "#16212B", "#5C6B78", "#B9C5CE", "#0F5E7A", "#9A6700", "#B4362C"
SANS = "Arial, 'Liberation Sans', Helvetica, sans-serif"
MONO = "'DejaVu Sans Mono', Menlo, Consolas, monospace"

S = {
 "en": dict(
  title="How Medskill Panda works",
  sub="You make three decisions. The plugin does the rest, writes every step to a file and checks its own work.",
  you="YOU", panda=["MEDSKILL", "PANDA"],
  a=["A. Ask for a talk", "or a paper; attach", "papers, data, template.", "Answer the questions."],
  b=["B. Read the plan.", "Approve it, or", "ask for changes."],
  c=["C. Open the files.", "Present, or revise", "and submit."],
  up1="questions", dn1="request, answers", up2="plan.md", dn2="approved", up3="files + report",
  steps=[("Interview", "deck-grilling", "brief.md"),
         ("Plan", "deck-planning", "plan.md"),
         ("Evidence", "evidence-research", "claims.json"),
         ("Figures, draft", "medical-figures", "figures/ drafts/"),
         ("Build", "html · pptx · beamer", "out/"),
         ("Audit", "slop · evidence · prose", "audit/"),
         ("Deliver", "report", "STATUS.md")],
  build2=["slides: .html .pptx .pdf", "paper: .docx .tex .md"],
  loop="A finding goes back to the step that caused it (at most 3 rounds).",
  notes_h="Checks that run by themselves",
  notes=[("Plan gate", "Nothing is built before you approve the plan."),
         ("Slop check", "Every saved slide is scanned for machine-made patterns."),
         ("Evidence audit", "Every number is compared with its source quote."),
         ("Manuscript audit", "Style in Vietnamese and English, unsourced statistics, decimals.")],
 ),
 "vi": dict(
  title="Medskill Panda hoạt động thế nào",
  sub="Bạn đưa ra ba quyết định. Plugin làm phần còn lại, ghi mỗi bước ra file và tự kiểm tra kết quả.",
  you="BẠN", panda=["MEDSKILL", "PANDA"],
  a=["A. Yêu cầu bài nói", "hoặc bài báo; gửi kèm", "tài liệu, dữ liệu, template.", "Trả lời các câu hỏi."],
  b=["B. Đọc kế hoạch.", "Duyệt, hoặc", "yêu cầu sửa."],
  c=["C. Mở file kết quả.", "Trình bày, hoặc", "sửa và nộp."],
  up1="câu hỏi", dn1="yêu cầu, trả lời", up2="plan.md", dn2="đã duyệt", up3="file + báo cáo",
  steps=[("Phỏng vấn", "deck-grilling", "brief.md"),
         ("Kế hoạch", "deck-planning", "plan.md"),
         ("Bằng chứng", "evidence-research", "claims.json"),
         ("Hình, bản thảo", "medical-figures", "figures/ drafts/"),
         ("Dựng", "html · pptx · beamer", "out/"),
         ("Kiểm tra", "slop · evidence · prose", "audit/"),
         ("Bàn giao", "báo cáo", "STATUS.md")],
  build2=["slide: .html .pptx .pdf", "bài báo: .docx .tex .md"],
  loop="Lỗi phát hiện được quay về đúng bước gây ra (tối đa 3 vòng).",
  notes_h="Các bước tự kiểm tra",
  notes=[("Cổng duyệt", "Chưa duyệt kế hoạch thì chưa dựng gì."),
         ("Quét slop", "Mỗi slide vừa lưu được quét dấu hiệu do máy làm."),
         ("Kiểm tra bằng chứng", "Mỗi con số được đối chiếu với câu trích nguồn."),
         ("Kiểm tra bản thảo", "Văn phong Việt/Anh, thống kê thiếu nguồn, dấu thập phân.")],
 ),
}


def text(x, y, s, size=15, weight="normal", color=INK, anchor="start", font=SANS, style=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" {style}>{e(s)}</text>')


def lines(x, y, rows, size=15, lh=21, **kw):
    return "".join(text(x, y + i * lh, r, size, **kw) for i, r in enumerate(rows))


def arrow(x1, y1, x2, y2, color=MUTE, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.6"{d} marker-end="url(#ah-{color[1:]})"/>'


def handoff(x, top, bottom, up, down):
    """Two vertical arrows between a 'you' box and a step: up (to you) on the right, down on the left."""
    return (arrow(x - 14, top, x - 14, bottom - 2) + arrow(x + 14, bottom, x + 14, top + 2)
            + text(x - 22, (top + bottom) / 2 + 5, down, 13, color=INK, anchor="end")
            + text(x + 22, (top + bottom) / 2 + 5, up, 13, color=INK))


def pipeline(L):
    t = S[L]
    W, H = 1680, 770
    x0, x1, lab = 40, 1640, 150
    you_y, you_h = 112, 140
    pan_y, pan_h = 112 + 140 + 70, 250
    sx, bw, gap = x0 + lab + 30, 176, 0
    gap = (x1 - 20 - sx - 7 * bw) / 6
    by, bh = pan_y + 36, 128
    cx = [sx + i * (bw + gap) + bw / 2 for i in range(7)]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           "<defs>" + "".join(
               f'<marker id="ah-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
               f'<path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>' for c in (MUTE, RED, INK)) + "</defs>",
           f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           text(x0, 52, t["title"], 30, "bold"), text(x0, 82, t["sub"], 17, color=MUTE)]
    # lanes
    out += [f'<rect x="{x0}" y="{you_y}" width="{x1-x0}" height="{you_h}" fill="#FBF6EA" stroke="{RULE}"/>',
            f'<rect x="{x0}" y="{pan_y}" width="{x1-x0}" height="{pan_h}" fill="#F1F6F8" stroke="{RULE}"/>',
            f'<line x1="{x0+lab}" y1="{you_y}" x2="{x0+lab}" y2="{you_y+you_h}" stroke="{RULE}"/>',
            f'<line x1="{x0+lab}" y1="{pan_y}" x2="{x0+lab}" y2="{pan_y+pan_h}" stroke="{RULE}"/>',
            text(x0 + lab / 2, you_y + you_h / 2 + 7, t["you"], 19, "bold", AMBER, "middle"),
            lines(x0 + lab / 2, pan_y + pan_h / 2 - 4, t["panda"], 19, 24, weight="bold", color=TEAL, anchor="middle")]
    # you boxes above steps 1, 2 and 7
    yb_y, yb_h = you_y + 14, you_h - 28
    for k, (i, rows, w) in enumerate(((0, t["a"], bw + 10), (1, t["b"], bw + 10), (6, t["c"], bw + 10))):
        bx = cx[i] - w / 2
        out.append(f'<rect x="{bx}" y="{yb_y}" width="{w}" height="{yb_h}" fill="#FFFFFF" stroke="{AMBER}" stroke-width="1.4"/>')
        out.append(lines(bx + 12, yb_y + 24, rows, 14, 20))
    # steps
    for i, (name, skill, f) in enumerate(t["steps"]):
        bx = cx[i] - bw / 2
        out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.3"/>')
        out.append(f'<rect x="{bx}" y="{by}" width="30" height="30" fill="{TEAL}"/>')
        out.append(text(bx + 15, by + 21, str(i + 1), 16, "bold", "#FFFFFF", "middle"))
        out.append(text(bx + 40, by + 21, name, 16, "bold"))
        out.append(text(bx + 12, by + 52, skill, 11.5, color=MUTE, font=MONO))
        if i == 4:
            out.append(lines(bx + 12, by + 74, t["build2"], 10.5, 17, font=MONO))
        out.append(f'<line x1="{bx}" y1="{by+bh-30}" x2="{bx+bw}" y2="{by+bh-30}" stroke="{RULE}"/>')
        out.append(text(bx + 12, by + bh - 10, "→ " + f, 12.5, color=TEAL, font=MONO))
        if i < 6:
            out.append(arrow(bx + bw + 2, by + bh / 2, bx + bw + gap - 3, by + bh / 2, INK))
    # handoffs between lanes
    top, bot = yb_y + yb_h, by
    out.append(handoff(cx[0], top, bot, t["up1"], t["dn1"]))
    out.append(handoff(cx[1], top, bot, t["up2"], t["dn2"]))
    out.append(arrow(cx[6], bot, cx[6], top + 2) + text(cx[6] + 10, (top + bot) / 2 + 5, t["up3"], 13, color=INK))
    # fix loop: audit (6) back to evidence (3)
    ly = by + bh + 30
    out.append(f'<path d="M{cx[5]} {by+bh} V{ly} H{cx[2]} V{by+bh+4}" fill="none" stroke="{RED}" stroke-width="1.6" '
               f'stroke-dasharray="6 5" marker-end="url(#ah-{RED[1:]})"/>')
    out.append(text((cx[2] + cx[5]) / 2, ly + 22, t["loop"], 13.5, color=RED, anchor="middle"))
    # notes
    ny = pan_y + pan_h + 46
    out.append(text(x0, ny, t["notes_h"], 15, "bold"))
    cw = (x1 - x0) / 4
    for k, (h, body) in enumerate(t["notes"]):
        nx = x0 + k * cw
        out.append(f'<line x1="{nx}" y1="{ny+16}" x2="{nx+cw-24}" y2="{ny+16}" stroke="{INK}" stroke-width="1.2"/>')
        out.append(text(nx, ny + 42, h, 15, "bold"))
        words, rows, cur = body.split(), [], ""
        for w_ in words:  # wrap at ~44 characters
            if len(cur) + len(w_) + 1 > 44:
                rows.append(cur)
                cur = w_
            else:
                cur = (cur + " " + w_).strip()
        rows.append(cur)
        out.append(lines(nx, ny + 66, rows, 14, 20, color=MUTE))
    out.append("</svg>")
    return f'<div id="pipeline" style="width:{W}px;background:#fff">' + "".join(out) + "</div>"
