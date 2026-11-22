"""The 'How it works' figure: what you do / what Medskill Panda does, as an editorial flowchart.

Journal-infographic style: square blocks of solid colour per phase, serif headings, line icons,
labelled hand-offs. No rounded corners, shadows or gradients. Used by make_art.py.
"""
import html

e = html.escape
INK, MUTE, RULE, PAPER = "#16212B", "#55636F", "#C3CDD5", "#FAF8F4"
TEAL, BLUE, RED, SLATE, PLUM, GREEN, AMBER = "#0F5E7A", "#2C5F9E", "#B4362C", "#4F5F73", "#7A3E7A", "#2E7D4F", "#A86A00"
SERIF = "'DejaVu Serif', Georgia, 'Liberation Serif', serif"
SANS = "'Liberation Sans', Arial, Helvetica, sans-serif"
MONO = "'DejaVu Sans Mono', Menlo, Consolas, monospace"
STEP_COLOR = [TEAL, TEAL, BLUE, RED, RED, PLUM, GREEN]

ICON = {  # 32 x 32 line icons, drawn in the step colour
 "chat": '<path d="M5 7h18v12H12l-5 5v-5H5z"/><path d="M10 12h8M10 15.5h5"/><path d="M25 12h2v11h-3v3l-4-3h-6"/>',
 "plan": '<rect x="5" y="5" width="22" height="22"/><path d="M10 11h12M10 16h12M10 21h7"/><path d="M19 22l2 2 5-6"/>',
 "ledger": '<path d="M8 4h13l5 5v19H8z"/><path d="M21 4v5h5"/><path d="M12 14h10M12 18h10M12 22h6"/>',
 "figure": '<path d="M5 5v22h22"/><path d="M8 9h5v4h4v4h5v3h4"/><path d="M8 9h3v7h5v5h5v3h5" stroke-dasharray="2 2"/>',
 "deck": '<rect x="4" y="5" width="24" height="16"/><path d="M8 17l4-4 3 2 6-6"/><path d="M16 21v5M11 27h10"/>',
 "audit": '<path d="M16 4l10 4v8c0 6-4 10-10 12C10 26 6 22 6 16V8z"/><path d="M11 16l4 4 7-8"/>',
 "deliver": '<path d="M5 9h22v17H5z"/><path d="M5 9l4-5h14l4 5"/><path d="M12 16l4 4 4-4M16 11v9"/>',
}

S = {
 "en": dict(
  title="How Medskill Panda works",
  sub="You make three decisions. The plugin does the rest, writes every step to a file and checks its own work.",
  you="YOU", panda="MEDSKILL PANDA",
  phases=[("Plan together", 0, 1), ("Research and build", 2, 4), ("Check and deliver", 5, 6)],
  a=("A", "Ask", ["A talk or a paper,", "plus your papers, data", "and template. Answer", "one round of questions."]),
  b=("B", "Approve", ["Read the plan.", "Approve it, or say", "what to change."]),
  c=("C", "Use", ["Open the files.", "Present, or revise", "and submit."]),
  up1="questions", dn1="request · answers", up2="plan.md", dn2="approval", up3="files · report",
  steps=[("Interview", "deck-grilling", ["audience, length,", "language, format"], "brief.md", "chat"),
         ("Plan", "deck-planning", ["one conclusion", "per slide or section"], "plan.md", "plan"),
         ("Evidence", "evidence-research", ["value, source,", "page, exact quote"], "claims.json", "ledger"),
         ("Figures, text", "medical-figures", ["charts from data;", "drafts per section"], "figures/ drafts/", "figure"),
         ("Build", "html · pptx · beamer", ["slides: html pptx pdf", "paper: docx tex md"], "out/", "deck"),
         ("Audit", "slop · evidence · prose", ["numbers vs sources,", "style VI / EN"], "audit/", "audit"),
         ("Deliver", "report", ["what was verified,", "what was not"], "STATUS.md", "deliver")],
  loop="Each finding goes back to the step that caused it · at most 3 rounds",
  notes_h="Checks that run by themselves",
  notes=[("Plan gate", "Nothing is built before you approve the plan.", TEAL),
         ("Slop check", "Every saved slide is scanned for machine-made patterns.", RED),
         ("Evidence audit", "Every number is compared with its source quote.", BLUE),
         ("Manuscript audit", "Style in Vietnamese and English, unsourced statistics, decimals.", PLUM)],
 ),
 "vi": dict(
  title="Medskill Panda hoạt động thế nào",
  sub="Bạn đưa ra ba quyết định. Plugin làm phần còn lại, ghi mỗi bước ra file và tự kiểm tra kết quả.",
  you="BẠN", panda="MEDSKILL PANDA",
  phases=[("Lập kế hoạch cùng bạn", 0, 1), ("Nghiên cứu và dựng", 2, 4), ("Kiểm tra và bàn giao", 5, 6)],
  a=("A", "Yêu cầu", ["Bài nói hoặc bài báo,", "kèm tài liệu, dữ liệu,", "template. Trả lời", "một lượt câu hỏi."]),
  b=("B", "Duyệt", ["Đọc kế hoạch.", "Duyệt, hoặc nói", "cần sửa gì."]),
  c=("C", "Sử dụng", ["Mở file kết quả.", "Trình bày, hoặc", "sửa và nộp."]),
  up1="câu hỏi", dn1="yêu cầu · trả lời", up2="plan.md", dn2="đã duyệt", up3="file · báo cáo",
  steps=[("Phỏng vấn", "deck-grilling", ["đối tượng, thời lượng,", "ngôn ngữ, định dạng"], "brief.md", "chat"),
         ("Kế hoạch", "deck-planning", ["một kết luận", "cho mỗi slide, mỗi mục"], "plan.md", "plan"),
         ("Bằng chứng", "evidence-research", ["giá trị, nguồn,", "trang, câu trích"], "claims.json", "ledger"),
         ("Hình, văn bản", "medical-figures", ["biểu đồ từ dữ liệu;", "bản thảo từng mục"], "figures/ drafts/", "figure"),
         ("Dựng", "html · pptx · beamer", ["slide: html pptx pdf", "bài báo: docx tex md"], "out/", "deck"),
         ("Kiểm tra", "slop · evidence · prose", ["số liệu so với nguồn,", "văn phong Việt / Anh"], "audit/", "audit"),
         ("Bàn giao", "báo cáo", ["đã kiểm chứng gì,", "chưa kiểm chứng gì"], "STATUS.md", "deliver")],
  loop="Mỗi lỗi quay về đúng bước gây ra · tối đa 3 vòng",
  notes_h="Các bước tự kiểm tra",
  notes=[("Cổng duyệt", "Chưa duyệt kế hoạch thì chưa dựng gì.", TEAL),
         ("Quét slop", "Mỗi slide vừa lưu được quét dấu hiệu do máy làm.", RED),
         ("Kiểm tra bằng chứng", "Mỗi con số được đối chiếu với câu trích nguồn.", BLUE),
         ("Kiểm tra bản thảo", "Văn phong Việt/Anh, thống kê thiếu nguồn, dấu thập phân.", PLUM)],
 ),
}


def text(x, y, s, size=15, weight="normal", color=INK, anchor="start", font=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" {extra}>{e(s)}</text>')


def lines(x, y, rows, size=15, lh=20, **kw):
    return "".join(text(x, y + i * lh, r, size, **kw) for i, r in enumerate(rows))


def arrow(x1, y1, x2, y2, color=INK, width=2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{d} '
            f'marker-end="url(#ah-{color[1:]})"/>')


def icon(name, x, y, color, size=34):
    k = size / 32
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.3f})" fill="none" stroke="{color}" stroke-width="1.8" '
            f'stroke-linejoin="round" stroke-linecap="round">{ICON[name]}</g>')


def pipeline(L):
    t = S[L]
    W, H = 1680, 900
    x0, x1, lab = 40, 1640, 64
    you_y, you_h = 150, 150
    pan_y = you_y + you_h + 86
    sx = x0 + lab + 26
    bw = 182
    gap = (x1 - 18 - sx - 7 * bw) / 6
    by, bh = pan_y + 34, 176
    pan_h = 34 + bh + 118
    cx = [sx + i * (bw + gap) + bw / 2 for i in range(7)]
    colors = (INK, RED, MUTE)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           "<defs>" + "".join(f'<marker id="ah-{c[1:]}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" '
                              f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>' for c in colors) + "</defs>",
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
           f'<rect x="{x0}" y="34" width="60" height="6" fill="{RED}"/>',
           text(x0, 84, t["title"], 34, "bold", font=SERIF),
           text(x0, 116, t["sub"], 17.5, color=MUTE)]
    # lanes: solid label bands
    out += [f'<rect x="{x0}" y="{you_y}" width="{x1-x0}" height="{you_h}" fill="#FFFFFF" stroke="{RULE}"/>',
            f'<rect x="{x0}" y="{you_y}" width="{lab}" height="{you_h}" fill="{AMBER}"/>',
            text(x0 + lab / 2 + 6, you_y + you_h / 2, t["you"], 17, "bold", "#FFFFFF", "middle",
                 extra=f'transform="rotate(-90 {x0 + lab / 2 + 6} {you_y + you_h / 2})" letter-spacing="3"'),
            f'<rect x="{x0}" y="{pan_y}" width="{x1-x0}" height="{pan_h}" fill="#FFFFFF" stroke="{RULE}"/>',
            f'<rect x="{x0}" y="{pan_y}" width="{lab}" height="{pan_h}" fill="{TEAL}"/>',
            text(x0 + lab / 2 + 6, pan_y + pan_h / 2, t["panda"], 17, "bold", "#FFFFFF", "middle",
                 extra=f'transform="rotate(-90 {x0 + lab / 2 + 6} {pan_y + pan_h / 2})" letter-spacing="3"')]
    # your three decisions
    yb_y, yb_h = you_y + 18, you_h - 36
    for i, (letter, verb, rows) in ((0, t["a"]), (1, t["b"]), (6, t["c"])):
        bx, w = cx[i] - (bw + 16) / 2, bw + 16
        out.append(f'<rect x="{bx:.1f}" y="{yb_y}" width="{w}" height="{yb_h}" fill="#FFF7E6" stroke="{AMBER}" stroke-width="1.5"/>')
        out.append(f'<rect x="{bx:.1f}" y="{yb_y}" width="34" height="34" fill="{AMBER}"/>')
        out.append(text(bx + 17, yb_y + 24, letter, 19, "bold", "#FFFFFF", "middle", font=SERIF))
        out.append(text(bx + 44, yb_y + 24, verb, 19, "bold", AMBER, font=SERIF))
        out.append(lines(bx + 12, yb_y + 54, rows, 13.5, 17.5))
    # phase brackets above the steps
    for name, i, j in t["phases"]:  # brackets under the steps
        a_, b_ = cx[i] - bw / 2, cx[j] + bw / 2
        yy = by + bh + 22
        out.append(f'<path d="M{a_:.1f} {yy-10} V{yy} H{b_:.1f} V{yy-10}" fill="none" stroke="{STEP_COLOR[i]}" stroke-width="2"/>')
        out.append(text((a_ + b_) / 2, yy + 22, name.upper(), 13, "bold", STEP_COLOR[i], "middle", extra='letter-spacing="1.5"'))
    # steps
    for i, (name, skill, rows, f, ic) in enumerate(t["steps"]):
        c = STEP_COLOR[i]
        bx = cx[i] - bw / 2
        out.append(f'<rect x="{bx:.1f}" y="{by}" width="{bw}" height="{bh}" fill="#FFFFFF" stroke="{c}" stroke-width="1.6"/>')
        out.append(f'<rect x="{bx:.1f}" y="{by}" width="{bw}" height="46" fill="{c}"/>')
        out.append(text(bx + 14, by + 32, str(i + 1), 26, "bold", "#FFFFFF", font=SERIF))
        out.append(text(bx + 40, by + 30, name, 17, "bold", "#FFFFFF"))
        out.append(icon(ic, bx + bw - 38, by + 8, "#FFFFFF", 30))
        out.append(text(bx + 14, by + 70, skill, 11.5, color=MUTE, font=MONO))
        out.append(lines(bx + 14, by + 100, rows, 13.5, 18))
        out.append(f'<rect x="{bx:.1f}" y="{by+bh-34}" width="{bw}" height="34" fill="#F3F5F7"/>')
        out.append(text(bx + 14, by + bh - 12, f, 12.5, "bold", c, font=MONO))
        if i < 6:
            out.append(arrow(bx + bw + 3, by + 23, bx + bw + gap - 4, by + 23))
    # hand-offs between the lanes
    top, bot = yb_y + yb_h, by

    def label(x, y, s, anchor):
        w = len(s) * 7.2 + 14
        rx = x - w if anchor == "end" else x
        return (f'<rect x="{rx:.1f}" y="{y-15:.1f}" width="{w:.1f}" height="22" fill="{PAPER}"/>'
                + text(x - 7 if anchor == "end" else x + 7, y + 1, s, 13, "bold", INK, anchor))

    mid = (top + bot) / 2 + 2
    for i, up, dn in ((0, t["up1"], t["dn1"]), (1, t["up2"], t["dn2"])):
        out.append(arrow(cx[i] - 16, top, cx[i] - 16, bot - 3, AMBER and INK))
        out.append(arrow(cx[i] + 16, bot, cx[i] + 16, top + 3))
        out.append(label(cx[i] - 26, mid, dn, "end"))
        out.append(label(cx[i] + 26, mid, up, "start"))
    out.append(arrow(cx[6], bot, cx[6], top + 3))
    out.append(label(cx[6] + 10, mid, t["up3"], "start") if False else label(cx[6] - 10, mid, t["up3"], "end"))
    # fix loop
    ly = by + bh + 86
    out.append(f'<path d="M{cx[5]:.1f} {by+bh} V{ly} H{cx[2]:.1f} V{by+bh+5}" fill="none" stroke="{RED}" stroke-width="2" '
               f'stroke-dasharray="7 5" marker-end="url(#ah-{RED[1:]})"/>')
    out.append(f'<rect x="{(cx[2]+cx[5])/2 - len(t["loop"])*3.9:.1f}" y="{ly-12}" width="{len(t["loop"])*7.8:.1f}" height="24" fill="#FFFFFF"/>')
    out.append(text((cx[2] + cx[5]) / 2, ly + 5, t["loop"], 13.5, "bold", RED, "middle"))
    # checks that run by themselves
    ny = pan_y + pan_h + 54
    out.append(text(x0, ny, t["notes_h"], 20, "bold", font=SERIF))
    cw = (x1 - x0) / 4
    for k, (h, body, c) in enumerate(t["notes"]):
        nx = x0 + k * cw
        out.append(f'<rect x="{nx}" y="{ny+18}" width="{cw-28:.1f}" height="5" fill="{c}"/>')
        out.append(text(nx, ny + 50, h, 16, "bold", c))
        words, rows, cur = body.split(), [], ""
        for w_ in words:
            if len(cur) + len(w_) + 1 > 46:
                rows.append(cur)
                cur = w_
            else:
                cur = (cur + " " + w_).strip()
        rows.append(cur)
        out.append(lines(nx, ny + 74, rows, 14.5, 20, color=INK))
    out.append("</svg>")
    return f'<div id="pipeline" style="width:{W}px;background:{PAPER}">' + "".join(out) + "</div>"
