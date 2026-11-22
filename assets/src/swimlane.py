"""The 'How it works' figure: a chain of files, each written by one step and read by the next.

Each step is drawn as the document it leaves behind (a sheet with a folded corner), grouped in
three acts. The person steps in at three marked moments; the approval is a gate across the chain;
a failed check loops back underneath. Flat: no rounded boxes, shadows or gradients. Used by make_art.py.
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
  title="Medskill Panda: a chain of files you can check",
  sub="Each step writes one file, and the next step works only from that file. You step in three times.",
  acts=[("I", "Frame", 0, 1), ("II", "Ground in sources", 2, 3), ("III", "Make and prove", 4, 6)],
  sheets=[("brief.md", "Pin down the job", ["who listens, how long,", "which language and file"], "chat"),
          ("plan.md", "Write the argument", ["one claim per slide", "or per section"], "plan"),
          ("claims.json", "Trace every number", ["value, page and the", "exact source sentence"], "ledger"),
          ("figures/", "Draw from data", ["charts recomputed,", "paper figures cropped"], "figure"),
          ("out/", "Assemble", ["HTML, PPTX, Beamer;", "Word, LaTeX, Markdown"], "deck"),
          ("audit/", "Re-check", ["numbers against quotes,", "wording and layout"], "audit"),
          ("STATUS.md", "Hand over", ["what was verified", "and what was not"], "deliver")],
  you=[("You describe", ["the topic and your files,", "then answer once"]),
       ("You say yes", ["to plan.md, or ask", "for changes"]),
       ("You use it", ["present, revise", "or submit"])],
  gate="GATE",
  loop="A failed check reopens the file that caused it · up to 3 rounds",
  on_h="Always on, without being asked",
  on=[("Gate", "No slide or paper file is made before plan.md is approved."),
      ("Number trace", "On every save, a number with no claim behind it is flagged."),
      ("Pattern scan", "Machine-made layouts and stock phrases are flagged on save."),
      ("Prose check", "Unsourced statistics, overclaims, decimal style in VI and EN.")],
 ),
 "vi": dict(
  title="Medskill Panda: một chuỗi file bạn kiểm tra được",
  sub="Mỗi bước ghi ra một file, bước sau chỉ làm việc từ file đó. Bạn tham gia ba lần.",
  acts=[("I", "Định khung", 0, 1), ("II", "Neo vào nguồn", 2, 3), ("III", "Làm ra và chứng minh", 4, 6)],
  sheets=[("brief.md", "Chốt yêu cầu", ["ai nghe, bao lâu,", "ngôn ngữ, loại file"], "chat"),
          ("plan.md", "Viết mạch lập luận", ["mỗi slide, mỗi mục", "một khẳng định"], "plan"),
          ("claims.json", "Truy từng con số", ["giá trị, số trang và", "câu gốc nguyên văn"], "ledger"),
          ("figures/", "Vẽ từ dữ liệu", ["biểu đồ tính lại,", "hình bài báo cắt ra"], "figure"),
          ("out/", "Ráp thành phẩm", ["HTML, PPTX, Beamer;", "Word, LaTeX, Markdown"], "deck"),
          ("audit/", "Soát lại", ["số liệu so với câu trích,", "câu chữ và bố cục"], "audit"),
          ("STATUS.md", "Bàn giao", ["điều đã kiểm chứng", "và điều chưa"], "deliver")],
  you=[("Bạn mô tả", ["chủ đề và tài liệu,", "trả lời một lượt"]),
       ("Bạn đồng ý", ["với plan.md, hoặc", "yêu cầu sửa"]),
       ("Bạn sử dụng", ["trình bày, sửa", "hoặc nộp bài"])],
  gate="CỔNG",
  loop="Kiểm tra trượt thì mở lại đúng file gây lỗi · tối đa 3 vòng",
  on_h="Luôn chạy, không cần gọi",
  on=[("Cổng duyệt", "Chưa duyệt plan.md thì chưa tạo file slide hay bài báo."),
      ("Truy số liệu", "Mỗi lần lưu, số nào không có nhận định đứng sau đều bị báo."),
      ("Quét kiểu máy", "Bố cục và câu sáo kiểu máy làm bị báo ngay khi lưu."),
      ("Soát văn bản", "Thống kê thiếu nguồn, khẳng định quá mức, dấu thập phân Việt/Anh.")],
 ),
}
ACT_COLOR = [TEAL, BLUE, RED]
ACT_TINT = ["#EAF2F4", "#ECF0F7", "#F7ECEA"]
ON_ICON = ["plan", "ledger", "audit", "chat"]


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


def wrap(s, n):
    rows, cur = [], ""
    for w_ in s.split():
        if len(cur) + len(w_) + 1 > n:
            rows.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    return rows + [cur]


def sheet(x, y, w, h, fname, head, rows, ic, color):
    """A document with a folded corner: the file this step leaves behind."""
    f = 22
    out = [f'<path d="M{x} {y} H{x+w-f} L{x+w} {y+f} V{y+h} H{x} Z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.4"/>',
           f'<path d="M{x+w-f} {y} V{y+f} H{x+w}" fill="#EEF1F3" stroke="{INK}" stroke-width="1.4"/>',
           f'<rect x="{x}" y="{y}" width="5" height="{h}" fill="{color}"/>',
           text(x + 18, y + 32, fname, 15, "bold", color, font=MONO),
           f'<line x1="{x+18}" y1="{y+46}" x2="{x+w-18}" y2="{y+46}" stroke="{RULE}" stroke-width="1"/>',
           text(x + 18, y + 76, head, 15, "bold", INK, font=SERIF),
           lines(x + 18, y + 104, rows, 13.5, 19, color=MUTE),
           icon(ic, x + w - 44, y + h - 42, color, 28)]
    return "".join(out)


def pipeline(L):
    t = S[L]
    W, H = 1680, 860
    x0, x1 = 40, 1640
    sw, sh = 182, 196
    G = 96                                   # extra room for the gate between plan.md and claims.json
    g = (x1 - 30 - (x0 + 30) - 7 * sw - G) / 6
    xs, x = [], x0 + 30
    for i in range(7):
        xs.append(x)
        x += sw + g + (G if i == 1 else 0)
    sy = 330
    cy = sy + sh / 2
    gate_x = xs[1] + sw + (g + G) / 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           "<defs>" + "".join(f'<marker id="ah-{c[1:]}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" '
                              f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>'
                              for c in (INK, RED, AMBER)) + "</defs>",
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
           text(x0, 70, t["title"], 34, "bold", font=SERIF),
           f'<rect x="{x0}" y="88" width="{x1-x0}" height="1.5" fill="{INK}"/>',
           text(x0, 120, t["sub"], 17.5, color=MUTE)]
    # acts: tinted fields behind their sheets, roman numeral and name on top
    for k, (num, name, i, j) in enumerate(t["acts"]):
        ax_, bx_ = xs[i] - 16, xs[j] + sw + 16
        out.append(f'<rect x="{ax_:.1f}" y="{sy-48}" width="{bx_-ax_:.1f}" height="{sh+70}" fill="{ACT_TINT[k]}"/>')
        anchor, lx = ("end", bx_ - 14) if k == 0 else ("start", ax_ + 14)  # act I: clear of the first dashed line
        out.append(f'<text x="{lx:.1f}" y="{sy-18}" font-family="{SERIF}" font-weight="bold" font-style="italic" '
                   f'fill="{ACT_COLOR[k]}" text-anchor="{anchor}"><tspan font-size="20">{e(num)}</tspan>'
                   f'<tspan font-size="16" dx="10">{e(name)}</tspan></text>')
    # the chain: one line through every sheet, arrowheads between sheets
    for i in range(6):
        a_, b_ = xs[i] + sw, xs[i + 1]
        out.append(f'<line x1="{a_:.1f}" y1="{cy}" x2="{b_-3:.1f}" y2="{cy}" stroke="{INK}" stroke-width="2.4" marker-end="url(#ah-{INK[1:]})"/>')
    for i, (fname, head, rows, ic) in enumerate(t["sheets"]):
        k = 0 if i < 2 else 1 if i < 4 else 2
        out.append(sheet(xs[i], sy, sw, sh, fname, head, rows, ic, ACT_COLOR[k]))
    # the gate: a bar across the chain
    out.append(f'<rect x="{gate_x-5:.1f}" y="{sy-62}" width="10" height="{sh+96}" fill="{AMBER}"/>')
    out.append(f'<rect x="{gate_x-30:.1f}" y="{cy-15}" width="60" height="30" fill="{AMBER}"/>')
    out.append(text(gate_x, cy + 6, t["gate"], 14, "bold", "#FFFFFF", "middle", extra='letter-spacing="2"'))
    # the three moments that need the person: amber discs above the chain
    for (vx, (verb, rows)) in zip((xs[0] + sw / 2, gate_x, xs[6] + sw / 2), t["you"]):
        dy = 196
        out.append(f'<line x1="{vx:.1f}" y1="{dy+22}" x2="{vx:.1f}" y2="{sy-66 if vx == gate_x else sy-2}" stroke="{AMBER}" '
                   f'stroke-width="2" stroke-dasharray="4 4"/>')
        out.append(f'<circle cx="{vx:.1f}" cy="{dy}" r="22" fill="{AMBER}"/>')
        out.append(f'<circle cx="{vx:.1f}" cy="{dy-5}" r="5.5" fill="#FFFFFF"/>'
                   f'<path d="M{vx-10:.1f} {dy+12} q10 -14 20 0" fill="#FFFFFF"/>')
        right = vx < W - 300
        tx, anchor = (vx + 32, "start") if right else (vx - 32, "end")
        out.append(text(tx, dy - 6, verb, 17, "bold", AMBER, anchor, font=SERIF))
        out.append(lines(tx, dy + 15, rows, 13.5, 18, color=INK, anchor=anchor))
    # the repair loop: from audit/ back under the chain to claims.json
    a_, b_ = xs[5] + sw / 2, xs[2] + sw / 2
    ly = sy + sh + 78
    out.append(f'<path d="M{a_:.1f} {sy+sh} C{a_:.1f} {ly+10} {b_:.1f} {ly+10} {b_:.1f} {sy+sh+5}" fill="none" stroke="{RED}" '
               f'stroke-width="2" stroke-dasharray="7 5" marker-end="url(#ah-{RED[1:]})"/>')
    mx = (a_ + b_) / 2
    wl = len(t["loop"]) * 7.6
    out.append(f'<rect x="{mx-wl/2:.1f}" y="{ly-6}" width="{wl:.1f}" height="26" fill="{PAPER}"/>')
    out.append(text(mx, ly + 12, t["loop"], 14, "bold", RED, "middle"))
    # always-on checks: four columns split by thin rules
    oy = 690
    out.append(text(x0, oy, t["on_h"], 20, "bold", font=SERIF, extra='font-style="italic"'))
    cw = (x1 - x0) / 4
    for k, (h, body) in enumerate(t["on"]):
        nx = x0 + k * cw
        if k:
            out.append(f'<line x1="{nx-14:.1f}" y1="{oy+22}" x2="{nx-14:.1f}" y2="{oy+118}" stroke="{RULE}" stroke-width="1.2"/>')
        out.append(icon(ON_ICON[k], nx, oy + 26, INK, 26))
        out.append(text(nx + 36, oy + 46, h, 16, "bold", INK))
        out.append(lines(nx, oy + 78, wrap(body, 44), 14.5, 20, color=MUTE))
    out.append("</svg>")
    return f'<div id="pipeline" style="width:{W}px;background:{PAPER}">' + "".join(out) + "</div>"
