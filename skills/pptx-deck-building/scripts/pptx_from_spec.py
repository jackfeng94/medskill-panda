#!/usr/bin/env python3
"""Build an editable .pptx from a JSON slide spec, optionally inside an institution's template.

With "template": the template's masters, backgrounds and layouts are kept; its own sample
slides are removed; each spec slide uses the layout named in the spec (or a sensible
default). Without a template: a clean 16:9 deck drawn from the theme colours and fonts.

Diagrams (trial schema, CONSORT, timelines) are built from native shapes and connectors,
and charts are native PowerPoint charts, so the presenter can edit them.

Usage: python pptx_from_spec.py deck.json out/talk.pptx
Spec reference: ../spec.md. Requires python-pptx.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from lxml import etree  # python-pptx depends on lxml
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
    from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.oxml.ns import qn
    from pptx.util import Emu, Inches, Pt
except ImportError:
    sys.exit("python-pptx is required: pip install python-pptx")

DEFAULT_THEME = {
    "fonts": {"heading": "Arial", "body": "Arial"},
    "colors": {"primary": "#0F5E7A", "ink": "#1B2430", "muted": "#66707C", "line": "#C9CED4",
               "intervention": "#C8372D", "control": "#56677F", "bg": "#FFFFFF", "title_text": "#1B2430"},
    "type_pt": {"title": 32, "body": 20, "small": 14, "footer": 11},
}


def rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#").upper())


class Builder:
    def __init__(self, spec: dict, base: Path):
        self.spec, self.base = spec, base
        self.theme = merge(DEFAULT_THEME, spec.get("theme", {}))
        tpl = spec.get("template")
        if tpl:
            self.prs = Presentation(str(base / tpl))
            self._drop_existing_slides()
        else:
            self.prs = Presentation()
            self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.W, self.H = self.prs.slide_width, self.prs.slide_height
        # Layouts of every master, addressable by name ("Title and Content"; first match wins)
        # or by part name ("slideLayout13"), which is unambiguous when masters share names.
        self.layout_names = {}
        for master in self.prs.slide_masters:
            for lay in master.slide_layouts:
                self.layout_names.setdefault(lay.name, lay)
                self.layout_names[Path(lay.part.partname).stem] = lay

    # ------------------------------------------------------------ helpers
    def _drop_existing_slides(self):
        sldIdLst = self.prs.slides._sldIdLst
        for sldId in list(sldIdLst):
            self.prs.part.drop_rel(sldId.rId)
            sldIdLst.remove(sldId)

    def color(self, key: str) -> RGBColor:
        c = self.theme["colors"]
        return rgb(c.get(key, key if key.startswith("#") else c["ink"]))

    def layout(self, kind: str, wanted: str | None):
        if wanted and wanted in self.layout_names:
            return self.layout_names[wanted]
        names = self.spec.get("layouts", {})
        if names.get(kind) in self.layout_names:
            return self.layout_names[names[kind]]
        if not self.spec.get("template"):
            return self.prs.slide_layouts[6]  # blank in the default template
        prefs = {"title": ["Title Slide"], "closing": ["Title Slide"],
                 "content": ["Title Only", "Title and Content"]}.get(kind, ["Title Only", "Title and Content"])
        for p in prefs:
            if p in self.layout_names:
                return self.layout_names[p]
        return self.prs.slide_layouts[0]

    def font(self, run, size=None, bold=None, color=None, heading=False, italic=None):
        f = run.font
        f.name = self.theme["fonts"]["heading" if heading else "body"]
        if size:
            f.size = Pt(size)
        if bold is not None:
            f.bold = bold
        if italic is not None:
            f.italic = italic
        if color:
            f.color.rgb = self.color(color)

    def apply_style(self, shape, key: str, default: dict | None = None):
        """Format every run of a placeholder with spec["styles"][key] (or `default`)."""
        st = self.spec.get("styles", {}).get(key, default)
        if not st:
            return
        if st.get("box_in"):  # move the placeholder, as the template's own slides do
            shape.left, shape.top, shape.width, shape.height = (Inches(v) for v in st["box_in"])
        if st.get("anchor"):
            shape.text_frame.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE,
                                                "bottom": MSO_ANCHOR.BOTTOM}[st["anchor"]]
        for p in shape.text_frame.paragraphs:
            if st.get("align"):
                p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[st["align"]]
            for r in p.runs:
                if st.get("caps"):
                    r.text = r.text.upper()
                self.font(r, st.get("size"), st.get("bold"), st.get("color"), heading=True, italic=st.get("italic"))
                if st.get("font"):
                    r.font.name = st["font"]

    def textbox(self, x, y, w, h, text, size, color="ink", bold=False, align=PP_ALIGN.LEFT, italic=False,
                anchor=MSO_ANCHOR.TOP, heading=False, name=None):
        tb = self.cur.shapes.add_textbox(x, y, w, h)
        if name:
            tb.name = name
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Emu(0)
        lines = text if isinstance(text, list) else [text]
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            r = p.add_run()
            r.text = line
            self.font(r, size, bold, color, heading, italic)
        return tb

    def title(self, s: dict):
        t = s.get("title", "")
        ph = self.cur.shapes.title
        size = self.theme["type_pt"]["title"]
        if ph is not None:
            ph.text_frame.text = t
            self.apply_style(ph, "title", None if self.spec.get("template") else
                             {"size": size, "bold": True, "color": "title_text"})
            return ph.top + ph.height
        self.textbox(Inches(0.7), Inches(0.45), self.W - Inches(1.4), Inches(1.2), t, size, "title_text",
                     True, heading=True, name="Title")
        return Inches(1.75)

    def content_box(self, top):
        top = max(top + Inches(0.25), Inches(1.6))
        bottom = self.H - Inches(float(self.spec.get("footer_reserve_in", 0.85)))
        return Inches(0.7), top, self.W - Inches(1.4), bottom - top

    def footer(self, s: dict, idx: int):
        cite = s.get("cite", self.spec.get("cite", ""))
        size = self.theme["type_pt"]["footer"]
        y = self.H - Inches(float(self.spec.get("footer_y_from_bottom_in", 0.55)))
        if cite:
            self.textbox(Inches(0.7), y, self.W - Inches(2.6), Inches(0.4), cite, size, "muted", italic=True, name="Source")
        if self.spec.get("page_numbers", True):
            self.textbox(self.W - Inches(1.7), y, Inches(1.0), Inches(0.4), str(idx), size, "muted",
                         align=PP_ALIGN.RIGHT, name="Page")

    def notes(self, s):
        if s.get("notes"):
            self.cur.notes_slide.notes_text_frame.text = s["notes"]

    def image(self, path, x, y, w, h, alt=""):
        from PIL import Image  # python-pptx depends on Pillow
        p = self.base / path
        with Image.open(p) as im:
            iw, ih = im.size
        scale = min(w / iw, h / ih)
        pw, ph = int(iw * scale), int(ih * scale)
        pic = self.cur.shapes.add_picture(str(p), x + (w - pw) // 2, y + (h - ph) // 2, pw, ph)
        pic._element.nvPicPr.cNvPr.set("descr", alt or Path(path).stem)
        return pic

    def bullets(self, items, x, y, w, h, size=None):
        size = size or self.theme["type_pt"]["body"]
        tb = self.cur.shapes.add_textbox(x, y, w, h)
        tb.name = "Body"
        tf = tb.text_frame
        tf.word_wrap = True
        for i, it in enumerate(items):
            it = it if isinstance(it, dict) else {"text": it}
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.level = it.get("level", 0)
            p.space_after = Pt(8)
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(int(Inches(0.3 + 0.35 * p.level))))
            pPr.set("indent", str(int(-Inches(0.28))))
            bu = etree.SubElement(pPr, qn("a:buChar"))
            bu.set("char", "•")
            r = p.add_run()
            r.text = it["text"]
            self.font(r, size - 2 * p.level, it.get("bold", False), it.get("color", "ink"))
        return tb

    # ------------------------------------------------------------ slide types
    def s_title(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("title", s.get("layout")))
        phs = {p.placeholder_format.type: p for p in self.cur.placeholders}
        t = self.cur.shapes.title
        if t is not None:
            t.text_frame.text = s.get("title", "")
            self.apply_style(t, "title_slide")
        else:
            self.textbox(Inches(0.9), Inches(2.2), self.W - Inches(1.8), Inches(2.0), s.get("title", ""), 40,
                         "title_text", True, heading=True, name="Title")
        sub = "\n".join(x for x in (s.get("subtitle"), s.get("presenter")) if x)
        body = next((p for k, p in phs.items() if p != t), None)
        if body is not None and sub:
            body.text_frame.text = sub
            self.apply_style(body, "subtitle")
        elif sub:
            self.textbox(Inches(0.9), Inches(4.5), self.W - Inches(1.8), Inches(1.4), sub.split("\n"), 22, "primary")
        for p in list(self.cur.placeholders):
            if p != t and not p.text_frame.text.strip():
                p._element.getparent().remove(p._element)

    s_closing = s_title

    def s_bullets(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        self.bullets(s.get("bullets", []), x, y, w, h)

    def s_figure(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        credit_h = Inches(0.35) if s.get("credit") else 0
        if s.get("labels"):
            self.labelled_image(s, x, y, w, h - credit_h)
        else:
            self.image(s["image"], x, y, w, h - credit_h, s.get("alt", ""))
        if s.get("credit"):
            self.textbox(x, y + h - credit_h, w, credit_h, s["credit"], self.theme["type_pt"]["small"], "muted",
                         italic=True, name="Credit")

    def labelled_image(self, s, x, y, w, h):
        """Picture in the middle, editable labels in columns either side, leader lines and dots.
        Same `labels` format as medical-figures/scripts/label_figure.py ("at" = fractions of the image)."""
        from PIL import Image
        with Image.open(self.base / s["image"]) as im:
            iw, ih = im.size
        ml, mr = s.get("margin", [0.5, 0.5])
        scale = min(w / ((ml + 1 + mr) * iw), h / ih)
        pw, ph = int(iw * scale), int(ih * scale)
        x0 = x + (w - int((ml + 1 + mr) * pw)) // 2
        px0 = x0 + int(ml * pw)
        pic = self.cur.shapes.add_picture(str(self.base / s["image"]), px0, y, pw, ph)
        pic._element.nvPicPr.cNvPr.set("descr", s.get("alt", Path(s["image"]).stem))
        size = s.get("label_pt", self.theme["type_pt"]["small"] + 2)
        line_h = Pt(size * 1.55)
        for side in ("left", "right"):
            items = [lab for lab in s["labels"] if lab.get("side", "left") == side]
            if not items:
                continue
            ys = [y + int(lab["at"][1] * ph) for lab in items]
            order = sorted(range(len(ys)), key=lambda i: ys[i])
            v = [ys[i] for i in order]
            for i in range(len(v)):  # spread apart, then pull back inside the picture height
                v[i] = max(v[i], y + line_h // 2 if i == 0 else v[i - 1] + line_h)
            for i in range(len(v) - 1, -1, -1):
                v[i] = min(v[i], y + ph - line_h // 2 if i == len(v) - 1 else v[i + 1] - line_h)
            placed = [0] * len(ys)
            for k, i in enumerate(order):
                placed[i] = v[k]
            col_w = int((ml if side == "left" else mr) * pw) - Inches(0.15)
            for lab, ly in zip(items, placed):
                tx = px0 - Inches(0.15) - col_w if side == "left" else px0 + pw + Inches(0.15)
                tb = self.textbox(tx, ly - line_h // 2, col_w, line_h, lab["text"], size, "ink",
                                  align=PP_ALIGN.RIGHT if side == "left" else PP_ALIGN.LEFT,
                                  anchor=MSO_ANCHOR.MIDDLE, name=f"Label {lab['text']}")
                tb.text_frame.word_wrap = False
                tb.text_frame.margin_top = tb.text_frame.margin_bottom = Emu(0)
                ax = px0 - Inches(0.08) if side == "left" else px0 + pw + Inches(0.08)
                tx_pt, ty_pt = px0 + int(lab["at"][0] * pw), y + int(lab["at"][1] * ph)
                ln = self.cur.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, ax, ly, tx_pt, ty_pt)
                ln.line.color.rgb = rgb("#5F6B78")
                ln.line.width = Pt(1)
                ln.name = f"Leader {lab['text']}"
                r = Pt(4)
                d = self.cur.shapes.add_shape(MSO_SHAPE.OVAL, tx_pt - r, ty_pt - r, 2 * r, 2 * r)
                d.fill.solid()
                d.fill.fore_color.rgb = rgb("#1B2430")
                d.line.color.rgb = rgb("#FFFFFF")
                d.line.width = Pt(1)
                d.name = f"Dot {lab['text']}"

    def s_figure_text(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        left = int(w * s.get("split", 0.58))
        credit_h = Inches(0.35) if s.get("credit") else 0
        self.image(s["image"], x, y, left - Inches(0.3), h - credit_h, s.get("alt", ""))
        if s.get("credit"):
            self.textbox(x, y + h - credit_h, left, credit_h, s["credit"], self.theme["type_pt"]["small"], "muted",
                         italic=True, name="Credit")
        self.bullets(s.get("bullets", []), x + left, y, w - left, h)

    def s_big_number(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        nums = s.get("numbers", [])
        cw = w // max(1, len(nums))
        for i, n in enumerate(nums):
            cx = x + i * cw
            self.textbox(cx, y + Inches(0.6), cw - Inches(0.3), Inches(1.4), n["value"], 54, n.get("color", "intervention"),
                         True, name=f"Number {i + 1}")
            self.textbox(cx, y + Inches(2.0), cw - Inches(0.3), Inches(1.2), n.get("label", ""), 20, "muted",
                         name=f"Label {i + 1}")
        if s.get("bullets"):
            self.bullets(s["bullets"], x, y + Inches(3.3), w, h - Inches(3.3), 18)

    def s_table(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        cols, rows = s["columns"], s["rows"]
        tbl = self.cur.shapes.add_table(len(rows) + 1, len(cols), x, y, w, Inches(0.45) * (len(rows) + 1)).table
        widths = s.get("col_widths")
        for j, c in enumerate(cols):
            if widths:
                tbl.columns[j].width = int(w * widths[j] / sum(widths))
            self._cell(tbl.cell(0, j), c, True)
        for i, row in enumerate(rows, 1):
            for j, v in enumerate(row):
                self._cell(tbl.cell(i, j), str(v), False)

    def _cell(self, cell, text, header):
        cell.text = text
        cell.fill.solid()
        cell.fill.fore_color.rgb = self.color("primary") if header else rgb("#FFFFFF")
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                self.font(r, self.theme["type_pt"]["small"] + 2, header, "#FFFFFF" if header else "ink")

    def s_diagram(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        shapes = {}
        styles = {"default": ("#FFFFFF", "primary", "ink"), "int": ("#FBEAE8", "intervention", "ink"),
                  "ctl": ("#EEF1F5", "control", "ink"), "primary": ("primary", "primary", "#FFFFFF"),
                  "muted": ("#F4F5F7", "line", "muted")}
        for n in s.get("nodes", []):
            fill, line, ink = styles.get(n.get("style", "default"), styles["default"])
            kind = MSO_SHAPE.OVAL if n.get("shape") == "circle" else MSO_SHAPE.ROUNDED_RECTANGLE
            shp = self.cur.shapes.add_shape(kind, x + int(w * n["x"]), y + int(h * n["y"]), int(w * n["w"]), int(h * n["h"]))
            shp.name = f"Node {n['id']}"
            shp.fill.solid()
            shp.fill.fore_color.rgb = self.color(fill)
            shp.line.color.rgb = self.color(line)
            shp.line.width = Pt(1.75)
            if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
                shp.adjustments[0] = 0.12
            tf = shp.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = Inches(0.12)
            lines = n["text"] if isinstance(n["text"], list) else [n["text"]]
            for i, line in enumerate(lines):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.alignment = PP_ALIGN.CENTER if n.get("align", "center") == "center" else PP_ALIGN.LEFT
                r = p.add_run()
                r.text = line
                self.font(r, n.get("size", self.theme["type_pt"]["small"] + 2), i == 0 and n.get("bold_first", True), ink)
            shapes[n["id"]] = shp
        for e in s.get("edges", []):
            a, b = shapes[e["from"]], shapes[e["to"]]
            con = self.cur.shapes.add_connector(MSO_CONNECTOR.ELBOW if e.get("elbow") else MSO_CONNECTOR.STRAIGHT, 0, 0, 0, 0)
            con.begin_connect(a, e.get("from_side", 3))
            con.end_connect(b, e.get("to_side", 1))
            con.line.color.rgb = self.color("primary")
            con.line.width = Pt(2)
            ln = con.line._get_or_add_ln()
            tail = etree.SubElement(ln, qn("a:tailEnd"))
            tail.set("type", "triangle")

    def s_chart(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        cd = CategoryChartData()
        cd.categories = s["categories"]
        for ser in s["series"]:
            cd.add_series(ser["name"], ser["values"])
        kind = {"bar": XL_CHART_TYPE.BAR_CLUSTERED, "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
                "line": XL_CHART_TYPE.LINE_MARKERS}[s.get("chart", "bar")]
        gf = self.cur.shapes.add_chart(kind, x, y, w, h - (Inches(0.35) if s.get("credit") else 0), cd)
        ch = gf.chart
        if kind == XL_CHART_TYPE.BAR_CLUSTERED:
            ch.category_axis.reverse_order = True  # first category at the top, as listed
        ch.has_legend = len(s["series"]) > 1
        if ch.has_legend:
            ch.legend.position = XL_LEGEND_POSITION.TOP
            ch.legend.include_in_layout = False
            ch.legend.font.size = Pt(self.theme["type_pt"]["small"])
        ch.font.size = Pt(self.theme["type_pt"]["small"])
        ch.font.name = self.theme["fonts"]["body"]
        for plot in ch.plots:
            plot.has_data_labels = True
            plot.data_labels.number_format = s.get("number_format", "0.0")
            plot.data_labels.number_format_is_linked = False
        for ser, spec_ser in zip(ch.series, s["series"]):
            fmt = ser.format
            if kind == XL_CHART_TYPE.LINE_MARKERS:
                fmt.line.color.rgb = self.color(spec_ser.get("color", "primary"))
            else:
                fmt.fill.solid()
                fmt.fill.fore_color.rgb = self.color(spec_ser.get("color", "primary"))
        if s.get("credit"):
            self.textbox(x, y + h - Inches(0.35), w, Inches(0.35), s["credit"], self.theme["type_pt"]["small"], "muted",
                         italic=True, name="Credit")

    def s_references(self, s, idx):
        self.cur = self.prs.slides.add_slide(self.layout("content", s.get("layout")))
        x, y, w, h = self.content_box(self.title(s))
        self._clear_body_placeholders()
        tb = self.cur.shapes.add_textbox(x, y, w, h)
        tf = tb.text_frame
        tf.word_wrap = True
        for i, ref in enumerate(s.get("items", [])):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(6)
            r = p.add_run()
            r.text = f"{i + 1}. {ref}"
            self.font(r, self.theme["type_pt"]["small"], color="ink")

    def _clear_body_placeholders(self):
        title = self.cur.shapes.title
        for p in list(self.cur.placeholders):
            if p != title and not (p.has_text_frame and p.text_frame.text.strip()):
                p._element.getparent().remove(p._element)

    # ------------------------------------------------------------ build
    def build(self, out: Path):
        for idx, s in enumerate(self.spec["slides"], 1):
            fn = getattr(self, "s_" + s["type"].replace("-", "_"), None)
            if fn is None:
                raise SystemExit(f"slide {idx}: unknown type {s['type']!r}")
            fn(s, idx)
            if s["type"] not in ("title", "closing"):
                self.footer(s, idx)
            self.notes(s)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(out))
        return len(self.spec["slides"])


def merge(a: dict, b: dict) -> dict:
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 2 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    spec_path = Path(argv[0])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    n = Builder(spec, spec_path.parent).build(Path(argv[1]))
    print(f"{argv[1]}: {n} slides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
