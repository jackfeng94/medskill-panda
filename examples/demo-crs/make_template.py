"""Make a branded 16:9 PowerPoint template (theme/template.pptx) for the DEMO-CRS example.

It stands in for the hospital or congress template a user would supply: pptx_from_spec.py
keeps its masters, backgrounds and decorations and fills its layouts. Layouts used:
"Title Slide" (teal background, logo, red rule) and "Title Only" (light background, top strip,
accent bar beside the title, small logo).
"""
import copy
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
LOGO = HERE.parents[1] / "assets" / "logo.png"
TEAL, TEAL_D, RED, BG = RGBColor(0x0F, 0x5E, 0x7A), RGBColor(0x0A, 0x42, 0x57), RGBColor(0xC8, 0x37, 0x2D), RGBColor(0xF4, 0xF7, 0xF9)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
layouts = {l.name: l for l in prs.slide_layouts}
prs.slide_master.background.fill.solid()
prs.slide_master.background.fill.fore_color.rgb = BG


def decorate(layout, build):
    """Draw shapes on a scratch slide, then move them into the layout (python-pptx has no API for it)."""
    tmp = prs.slides.add_slide(layouts["Blank"])
    build(tmp.shapes)
    tree = layout.shapes._spTree
    for shp in list(tmp.shapes):
        el = shp._element
        blip = el.find(".//" + qn("a:blip"))
        if blip is not None:  # re-point the picture to the layout's own relationship
            image_part = tmp.part.related_part(blip.get(qn("r:embed")))
            blip.set(qn("r:embed"), layout.part.relate_to(image_part, RT.IMAGE))
        tree.insert(2, copy.deepcopy(el))  # behind the placeholders
    sld_id = prs.slides._sldIdLst[-1]
    prs.part.drop_rel(sld_id.rId)
    prs.slides._sldIdLst.remove(sld_id)


def rect(shapes, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE):
    s = shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def place(ph, x, y, w, h):
    ph.left, ph.top, ph.width, ph.height = Inches(x), Inches(y), Inches(w), Inches(h)


# ---- title slide: teal background, logo, red rule
title = layouts["Title Slide"]
title.background.fill.gradient()
title.background.fill.gradient_angle = 135
stops = title.background.fill.gradient_stops
stops[0].color.rgb, stops[1].color.rgb = TEAL_D, RGBColor(0x16, 0x80, 0x9F)
decorate(title, lambda sh: (sh.add_picture(str(LOGO), Inches(0.9), Inches(0.75), Inches(1.25), Inches(1.25)),
                            rect(sh, 0.9, 2.35, 1.3, 0.09, RED)))
for ph in title.placeholders:
    if ph.placeholder_format.idx == 0:
        place(ph, 0.9, 2.6, 10.8, 2.6)
    else:
        place(ph, 0.9, 5.35, 10.8, 1.3)

# ---- content slides: top strip, accent bar beside the title, small logo
body = layouts["Title Only"]
decorate(body, lambda sh: (rect(sh, 0, 0, 13.333, 0.1, TEAL), rect(sh, 0.55, 0.5, 0.1, 0.82, TEAL),
                           sh.add_picture(str(LOGO), Inches(12.3), Inches(0.42), Inches(0.62), Inches(0.62))))
for ph in body.placeholders:
    if ph.placeholder_format.idx == 0:
        place(ph, 0.85, 0.38, 11.2, 1.06)

(HERE / "theme").mkdir(exist_ok=True)
prs.save(str(HERE / "theme" / "template.pptx"))
print("theme/template.pptx")
