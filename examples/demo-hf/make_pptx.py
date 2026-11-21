"""Write the DEMO-HF PowerPoint spec (EN and VI) for pptx-deck-building's pptx_from_spec.py.

Run make_data.py and make_charts.py first. The trial schema and the KCCQ chart are native
PowerPoint shapes and charts (editable); the Kaplan–Meier curve and forest plot are PNGs drawn
from the data.
"""
import json
import shutil
import sys
from pathlib import Path

D = Path(sys.argv[1])
r = json.loads((D / "out" / "results.json").read_text(encoding="utf-8"))
v = json.loads((D / "out" / "charts" / "values.json").read_text(encoding="utf-8"))
c = v["consort"]


def num(x, lang, nd=1):
    s = f"{x:.{nd}f}"
    return s.replace(".", ",") if lang == "vi" else s


THEME = {"fonts": {"heading": "Arial", "body": "Arial"},
         "colors": {"primary": "#0F5E7A", "ink": "#15202B", "muted": "#5F6E7B", "line": "#D9E2E8",
                    "intervention": "#C8372D", "control": "#56677F", "title_text": "#15202B"},
         "type_pt": {"title": 28, "body": 18, "small": 13, "footer": 10}}

T = {
 "en": dict(
  cite="Simulated data for demonstration · DEMO-HF, seed 7",
  t1="In the simulated DEMO-HF trial, structured follow-up cut heart-failure admissions by a quarter",
  sub="Journal club · a demonstration built from simulated data", who="Medskill Panda demo",
  t2=f"{r['n']:,} patients were randomised 1:1 and followed for up to 24 months",
  pop=["Population", "HFrEF after a hospital stay"],
  arm_i=["Structured follow-up", f"n = {r['n_arm']:,}"], arm_c=["Usual care", f"n = {r['n_arm']:,}"],
  ep=["Primary endpoint", "First admission for heart failure", "24 months"],
  t3=f"Admissions diverged early and reached {num(r['cuminc24_intervention'], 'en')}% vs {num(r['cuminc24_control'], 'en')}% by month 24",
  b3=[f"Difference {num(r['arr24'], 'en')} percentage points", f"Number needed to treat: {r['nnt24']}",
      f"{r['events_intervention']} vs {r['events_control']} admissions"],
  t4="The effect held across age, sex and diabetes subgroups",
  b4=[f"Overall rate ratio {num(r['rr'], 'en', 2)} (95% CI {num(r['rr_lo'], 'en', 2)}–{num(r['rr_hi'], 'en', 2)})",
      "Every subgroup estimate lies below 1", "Subgroups are exploratory"],
  t5="Quality of life improved by month 3 and the gain held to month 24",
  months=["Baseline", "Month 3", "Month 6", "Month 12", "Month 24"], s_int="Intervention", s_ctl="Usual care",
  t6=f"Treating {r['nnt24']} patients for two years prevents one admission",
  n6=[(f"−{num(r['arr24'], 'en')}", f"percentage points: {num(r['cuminc24_control'], 'en')}% → {num(r['cuminc24_intervention'], 'en')}% at 24 months", "#56677F"),
      (num(r["rr"], "en", 2), f"rate ratio, 95% CI {num(r['rr_lo'], 'en', 2)}–{num(r['rr_hi'], 'en', 2)}", "#C8372D"),
      (str(r["nnt24"]), "number needed to treat for 24 months", "#0F5E7A")],
  credit3="Source: simulated DEMO-HF data (seed 7); Kaplan–Meier estimate",
  credit4="Source: simulated DEMO-HF data (seed 7); Poisson rate ratios",
  credit5="Source: simulated DEMO-HF data (seed 11); mean KCCQ score",
  km="km.png", forest="forest.png",
 ),
 "vi": dict(
  cite="Dữ liệu mô phỏng để minh hoạ · DEMO-HF, seed 7",
  t1="Trong thử nghiệm mô phỏng DEMO-HF, theo dõi có cấu trúc giảm một phần tư số lần nhập viện vì suy tim",
  sub="Journal club · ví dụ minh hoạ dựng từ dữ liệu mô phỏng", who="Medskill Panda demo",
  t2=f"{r['n']:,} bệnh nhân được phân nhóm ngẫu nhiên 1:1 và theo dõi đến 24 tháng".replace(",", "."),
  pop=["Đối tượng", "Suy tim EF giảm sau nằm viện"],
  arm_i=["Theo dõi có cấu trúc", f"n = {r['n_arm']:,}".replace(",", ".")], arm_c=["Chăm sóc thường quy", f"n = {r['n_arm']:,}".replace(",", ".")],
  ep=["Tiêu chí chính", "Lần nhập viện đầu tiên vì suy tim", "24 tháng"],
  t3=f"Tách biệt sớm: {num(r['cuminc24_intervention'], 'vi')}% so với {num(r['cuminc24_control'], 'vi')}% nhập viện sau 24 tháng",
  b3=[f"Chênh {num(r['arr24'], 'vi')} điểm phần trăm", f"Số cần điều trị: {r['nnt24']}",
      f"{r['events_intervention']} so với {r['events_control']} lần nhập viện"],
  t4="Hiệu quả nhất quán theo tuổi, giới và đái tháo đường",
  b4=[f"Tỷ số tỷ suất chung {num(r['rr'], 'vi', 2)} (KTC 95% {num(r['rr_lo'], 'vi', 2)}–{num(r['rr_hi'], 'vi', 2)})",
      "Mọi phân nhóm đều có ước lượng dưới 1", "Phân tích phân nhóm chỉ mang tính thăm dò"],
  t5="Chất lượng sống cải thiện từ tháng 3 và duy trì đến tháng 24",
  months=["Ban đầu", "Tháng 3", "Tháng 6", "Tháng 12", "Tháng 24"], s_int="Can thiệp", s_ctl="Chăm sóc thường quy",
  t6=f"Điều trị {r['nnt24']} bệnh nhân trong hai năm tránh được một lần nhập viện",
  n6=[(f"−{num(r['arr24'], 'vi')}", f"điểm phần trăm: {num(r['cuminc24_control'], 'vi')}% → {num(r['cuminc24_intervention'], 'vi')}% sau 24 tháng", "#56677F"),
      (num(r["rr"], "vi", 2), f"tỷ số tỷ suất, KTC 95% {num(r['rr_lo'], 'vi', 2)}–{num(r['rr_hi'], 'vi', 2)}", "#C8372D"),
      (str(r["nnt24"]), "số cần điều trị trong 24 tháng", "#0F5E7A")],
  credit3="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 7); ước lượng Kaplan–Meier",
  credit4="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 7); tỷ số tỷ suất Poisson",
  credit5="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 11); điểm KCCQ trung bình",
  km="km_vi.png", forest="forest_vi.png",
 ),
}

for lang, t in T.items():
    b = D / f"pptx_{lang}" / "build"
    b.mkdir(parents=True, exist_ok=True)
    for f in ("1-kaplan-meier.png", "2-forest.png"):
        shutil.copy(D / "out" / "charts" / lang / "slide" / f, b / f)
    kccq = v["kccq"]
    spec = {
        "template": "../../theme/template.pptx",
        "layouts": {"title": "Title Slide", "content": "Title Only"},
        "styles": {"title": {"size": 26, "bold": True, "color": "#15202B", "anchor": "middle", "align": "left"},
                   "title_slide": {"size": 38, "bold": True, "color": "#FFFFFF", "anchor": "top", "align": "left"},
                   "subtitle": {"size": 20, "color": "#CFE6EE", "align": "left"}},
        "theme": THEME, "cite": t["cite"], "page_numbers": True,
        "slides": [
            {"type": "title", "title": t["t1"], "subtitle": t["sub"], "presenter": t["who"]},
            {"type": "diagram", "title": t["t2"],
             "nodes": [{"id": "pop", "x": 0, "y": 0.2, "w": 0.22, "h": 0.6, "text": t["pop"]},
                       {"id": "r", "x": 0.28, "y": 0.4, "w": 0.08, "h": 0.2, "text": "R 1:1", "style": "primary", "shape": "circle"},
                       {"id": "a", "x": 0.42, "y": 0.06, "w": 0.28, "h": 0.36, "text": t["arm_i"], "style": "int"},
                       {"id": "b", "x": 0.42, "y": 0.58, "w": 0.28, "h": 0.36, "text": t["arm_c"], "style": "ctl"},
                       {"id": "ep", "x": 0.77, "y": 0.2, "w": 0.23, "h": 0.6, "text": t["ep"]}],
             "edges": [{"from": "pop", "to": "r"}, {"from": "r", "to": "a", "elbow": True}, {"from": "r", "to": "b", "elbow": True},
                       {"from": "a", "to": "ep", "elbow": True}, {"from": "b", "to": "ep", "elbow": True}]},
            {"type": "figure-text", "title": t["t3"], "image": "1-kaplan-meier.png", "alt": "Kaplan–Meier curve",
             "credit": t["credit3"], "bullets": t["b3"], "split": 0.62},
            {"type": "figure-text", "title": t["t4"], "image": "2-forest.png", "alt": "Forest plot",
             "credit": t["credit4"], "bullets": t["b4"], "split": 0.62},
            {"type": "chart", "title": t["t5"], "chart": "line", "categories": t["months"],
             "series": [{"name": t["s_int"], "values": [p[0] for p in kccq["intervention"]], "color": "#C8372D"},
                        {"name": t["s_ctl"], "values": [p[0] for p in kccq["control"]], "color": "#56677F"}],
             "number_format": "0", "credit": t["credit5"]},
            {"type": "big-number", "title": t["t6"],
             "numbers": [{"value": a, "label": l, "color": col} for a, l, col in t["n6"]]},
        ],
    }
    notes = ["Introduce DEMO-HF as a teaching example with simulated data.",
             "Walk through the trial schema from population to endpoint.",
             "Point to the separation of the curves before month 6.",
             "Subgroups are exploratory; say so.",
             "KCCQ ranges from 0 to 100; higher is better.",
             "Close with the absolute effect, not only the ratio."]
    for s, n in zip(spec["slides"], notes):
        s["notes"] = n
    (b / "deck.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
