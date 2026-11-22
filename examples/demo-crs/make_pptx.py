"""Write the DEMO-CRS (ENT) PowerPoint spec (EN and VI) for pptx-deck-building's pptx_from_spec.py.

Run make_data.py and make_charts.py first. The trial schema and the SNOT-22 chart are native
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


THEME = {"fonts": {"heading": "Arial", "body": "Arial"}, "corners": "square",
         "colors": {"primary": "#0F5E7A", "ink": "#15202B", "muted": "#5F6E7B", "line": "#D9E2E8",
                    "intervention": "#C8372D", "control": "#56677F", "title_text": "#15202B"},
         "type_pt": {"title": 28, "body": 18, "small": 13, "footer": 10}}

EN_SUB = {"Age < 50": "age < 50", "Age ≥ 50": "age ≥ 50", "Women": "women", "Men": "men", "Asthma": "asthma",
          "No asthma": "no asthma"}
VI_SUB = {"Age < 50": "dưới 50 tuổi", "Age ≥ 50": "từ 50 tuổi", "Women": "nữ", "Men": "nam", "Asthma": "hen",
          "No asthma": "không hen"}
cross = [g["label"] for g in r["subgroups"] if g["hi"] >= 1]
REFS = [{"authors": "Fokkens WJ, Lund VJ, Hopkins C, et al", "title": "European Position Paper on Rhinosinusitis and Nasal Polyps 2020",
         "journal": "Rhinology", "year": 2020},
        {"authors": "Hopkins C, Gillett S, Slack R, Lund VJ, Browne JP", "title": "Psychometric validity of the 22-item Sinonasal Outcome Test",
         "journal": "Clin Otolaryngol", "year": 2009}]

T = {
 "en": dict(
  cite="Simulated data for demonstration · DEMO-CRS, seed 7",
  t1="In the simulated DEMO-CRS trial, structured care after sinus surgery cut polyp recurrence by about a third",
  sub="A demonstration built from simulated data", who="Medskill Panda demo", event="ENT journal club",
  agenda_t="Four questions in fifteen minutes",
  agenda=[("The question and the design", 3), ("Recurrence and symptoms", 5), ("How far to trust it", 4),
          ("What it means for our rhinology clinic", 3)],
  pico_t="Does structured care after sinus surgery stop polyps coming back?",
  pico=[("Population", "CRS with nasal polyps, after sinus surgery"), ("Intervention", "Steroid irrigation, scheduled endoscopy"),
        ("Comparator", "Usual care"), ("Outcome", "Endoscopic polyp recurrence, 24 months"),
        ("Design", f"Randomised 1:1, {r['n']:,} patients, simulated")],
  t2=f"{r['n']:,} patients were randomised 1:1 after endoscopic sinus surgery",
  pop=["Population", "CRSwNP after endoscopic sinus surgery"],
  arm_i=["Structured care", "Steroid irrigation, endoscopy visits", f"n = {r['n_arm']:,}"],
  arm_c=["Usual care", f"n = {r['n_arm']:,}"],
  ep=["Primary endpoint", "Endoscopic polyp recurrence", "24 months"],
  t3=f"Recurrence diverged early and reached {num(r['cuminc24_intervention'], 'en')}% vs {num(r['cuminc24_control'], 'en')}% by month 24",
  b3=[f"Difference {num(r['arr24'], 'en')} percentage points", f"{r['events_intervention']} vs {r['events_control']} recurrences"],
  take3=f"One recurrence prevented for every {r['nnt24']} patients followed for two years",
  t4="The effect pointed the same way across age, sex and asthma subgroups",
  b4=[f"Overall rate ratio {num(r['rr'], 'en', 2)} (95% CI {num(r['rr_lo'], 'en', 2)}–{num(r['rr_hi'], 'en', 2)})",
      "Intervals cross 1 for " + ", ".join(EN_SUB[x] for x in cross)],
  take4="Subgroups are exploratory: none stands apart",
  t5="Symptoms improved in both arms; with structured care the gain held to month 24",
  months=["Before", "Month 3", "Month 6", "Month 12", "Month 24"], s_int="Structured care", s_ctl="Usual care",
  credit3="Source: simulated DEMO-CRS data (seed 7); Kaplan–Meier estimate",
  credit4="Source: simulated DEMO-CRS data (seed 7); Poisson rate ratios",
  credit5="Source: simulated DEMO-CRS data (seed 11); mean SNOT-22 score (0–110, lower is better)",
  t6=f"Treating {r['nnt24']} patients for two years prevents one recurrence",
  n6=[(f"−{num(r['arr24'], 'en')}", "#56677F"), (num(r["rr"], "en", 2), "#C8372D"), (str(r["nnt24"]), "#0F5E7A")],
  lab6=["percentage points fewer recurrences", "rate ratio", "number needed to treat"],
  ctx6=[f"{num(r['cuminc24_control'], 'en')}% → {num(r['cuminc24_intervention'], 'en')}% at 24 months",
        f"95% CI {num(r['rr_lo'], 'en', 2)}–{num(r['rr_hi'], 'en', 2)}", "over 24 months"],
  t7="A clean comparison, but a simulated cohort cannot change practice",
  strong=("Strengths", ["Randomised comparison", "Endoscopic endpoint", "Absolute and relative effects"]),
  weak=("Limitations", ["Simulated data, not evidence", "Assessors not described", "No adherence data"]),
  take7="Learn the method; do not change practice yet.",
  t8=f"Structured care prevented {num(r['arr24'], 'en')} recurrences per 100 patients over two years",
  sup8=["In a real trial, check adherence to irrigation and who read the endoscopy.",
        "Discussion: which of our patients would we offer this to first?"],
  t9="References", refs=[{"authors": "Medskill Panda", "title": "DEMO-CRS simulated trial dataset, seed 7",
                          "journal": "examples/demo-crs/make_data.py", "year": 2026}] + REFS,
  t10="Questions and discussion", sub10="DEMO-CRS · simulated data for teaching",
 ),
 "vi": dict(
  cite="Dữ liệu mô phỏng để minh hoạ · DEMO-CRS, seed 7",
  t1="Trong thử nghiệm mô phỏng DEMO-CRS, chăm sóc có cấu trúc sau mổ xoang giảm khoảng một phần ba tái phát polyp",
  sub="Ví dụ minh hoạ dựng từ dữ liệu mô phỏng", who="Medskill Panda demo", event="Journal club Tai Mũi Họng",
  agenda_t="Bốn câu hỏi trong mười lăm phút",
  agenda=[("Câu hỏi và thiết kế", 3), ("Tái phát và triệu chứng", 5), ("Tin được đến đâu", 4),
          ("Ý nghĩa cho phòng khám mũi xoang", 3)],
  pico_t="Chăm sóc có cấu trúc sau mổ xoang có ngăn polyp tái phát?",
  pico=[("Đối tượng", "Viêm mũi xoang mạn có polyp, sau mổ"), ("Can thiệp", "Rửa mũi corticoid, nội soi theo lịch"),
        ("So sánh", "Chăm sóc thường quy"), ("Kết cục", "Tái phát polyp trên nội soi, 24 tháng"),
        ("Thiết kế", f"Ngẫu nhiên 1:1, {r['n']} người, mô phỏng")],
  t2=f"{r['n']} bệnh nhân được phân nhóm ngẫu nhiên 1:1 sau phẫu thuật nội soi xoang",
  pop=["Đối tượng", "Polyp mũi, sau mổ nội soi xoang"],
  arm_i=["Chăm sóc có cấu trúc", f"n = {r['n_arm']}"],
  arm_c=["Chăm sóc thường quy", f"n = {r['n_arm']}"],
  ep=["Tiêu chí chính", "Tái phát polyp", "24 tháng"],
  t3=f"Tách biệt sớm: {num(r['cuminc24_intervention'], 'vi')}% so với {num(r['cuminc24_control'], 'vi')}% tái phát sau 24 tháng",
  b3=[f"Chênh {num(r['arr24'], 'vi')} điểm phần trăm", f"{r['events_intervention']} so với {r['events_control']} ca tái phát"],
  take3=f"Cứ {r['nnt24']} bệnh nhân được chăm sóc hai năm thì tránh được một ca tái phát",
  t4="Hiệu quả cùng chiều theo tuổi, giới và hen phế quản",
  b4=[f"Tỷ số tỷ suất chung {num(r['rr'], 'vi', 2)} (KTC 95% {num(r['rr_lo'], 'vi', 2)}–{num(r['rr_hi'], 'vi', 2)})",
      "KTC vượt 1 ở nhóm " + ", ".join(VI_SUB[x] for x in cross)],
  take4="Phân nhóm chỉ để thăm dò: không nhóm nào khác biệt rõ",
  t5="Triệu chứng cải thiện ở cả hai nhóm; với chăm sóc có cấu trúc, cải thiện giữ được đến tháng 24",
  months=["Trước mổ", "Tháng 3", "Tháng 6", "Tháng 12", "Tháng 24"], s_int="Chăm sóc có cấu trúc", s_ctl="Thường quy",
  credit3="Nguồn: dữ liệu mô phỏng DEMO-CRS (seed 7); ước lượng Kaplan–Meier",
  credit4="Nguồn: dữ liệu mô phỏng DEMO-CRS (seed 7); tỷ số tỷ suất Poisson",
  credit5="Nguồn: dữ liệu mô phỏng DEMO-CRS (seed 11); điểm SNOT-22 trung bình (0–110, thấp là tốt)",
  t6=f"Điều trị {r['nnt24']} bệnh nhân trong hai năm tránh được một ca tái phát",
  n6=[(f"−{num(r['arr24'], 'vi')}", "#56677F"), (num(r["rr"], "vi", 2), "#C8372D"), (str(r["nnt24"]), "#0F5E7A")],
  lab6=["điểm phần trăm tái phát ít hơn", "tỷ số tỷ suất", "số cần điều trị"],
  ctx6=[f"{num(r['cuminc24_control'], 'vi')}% → {num(r['cuminc24_intervention'], 'vi')}% sau 24 tháng",
        f"KTC 95% {num(r['rr_lo'], 'vi', 2)}–{num(r['rr_hi'], 'vi', 2)}", "trong 24 tháng"],
  t7="So sánh rõ ràng, nhưng nhóm mô phỏng không thể thay đổi thực hành",
  strong=("Điểm mạnh", ["So sánh ngẫu nhiên", "Tiêu chí nội soi", "Hiệu quả tuyệt đối, tương đối"]),
  weak=("Hạn chế", ["Dữ liệu mô phỏng", "Chưa rõ người đọc nội soi", "Chưa có dữ liệu tuân thủ"]),
  take7="Học phương pháp; chưa đổi thực hành.",
  t8=f"Chăm sóc có cấu trúc giảm {num(r['arr24'], 'vi')} ca tái phát trên 100 bệnh nhân sau hai năm",
  sup8=["Với thử nghiệm thật, cần xem mức tuân thủ rửa mũi và ai đọc kết quả nội soi.",
        "Thảo luận: bệnh nhân nào ở phòng khám của chúng ta nên được ưu tiên?"],
  t9="Tài liệu tham khảo", refs=[{"authors": "Medskill Panda", "title": "Bộ dữ liệu mô phỏng DEMO-CRS, seed 7",
                                  "journal": "examples/demo-crs/make_data.py", "year": 2026}] + REFS,
  t10="Câu hỏi và thảo luận", sub10="DEMO-CRS · dữ liệu mô phỏng để giảng dạy",
 ),
}

for lang, t in T.items():
    b = D / f"pptx_{lang}" / "build"
    b.mkdir(parents=True, exist_ok=True)
    for f in ("1-kaplan-meier.png", "2-forest.png"):
        shutil.copy(D / "out" / "charts" / lang / "slide" / f, b / f)
    snot = v["snot22"]
    spec = {
        "template": "../../theme/template.pptx",
        "layouts": {"title": "Title Slide", "content": "Title Only", "closing": "Title Slide", "key-message": "Title Slide"},
        "styles": {"title": {"size": 26, "bold": True, "color": "#15202B", "anchor": "middle", "align": "left"},
                   "title_slide": {"size": 38, "bold": True, "color": "#FFFFFF", "anchor": "top", "align": "left"},
                   "subtitle": {"size": 20, "color": "#CFE6EE", "align": "left"},
                   "key_message": {"size": 34, "bold": True, "color": "#FFFFFF", "anchor": "top", "align": "left"}},
        "theme": THEME, "cite": t["cite"], "page_numbers": True,
        "slides": [
            {"type": "title", "title": t["t1"], "subtitle": t["sub"], "presenter": t["who"], "event": t["event"]},
            {"type": "agenda", "title": t["agenda_t"], "items": [{"text": a, "minutes": m} for a, m in t["agenda"]]},
            {"type": "pico", "title": t["pico_t"], "rows": [{"label": a, "text": x} for a, x in t["pico"]]},
            {"type": "diagram", "title": t["t2"],
             "nodes": [{"id": "pop", "x": 0, "y": 0.34, "w": 0.22, "h": 0.32, "text": t["pop"]},
                       {"id": "r", "x": 0.28, "y": 0.41, "w": 0.075, "h": 0.18, "text": "R 1:1", "style": "primary", "shape": "circle"},
                       {"id": "a", "x": 0.43, "y": 0.1, "w": 0.27, "h": 0.26, "text": t["arm_i"], "style": "int"},
                       {"id": "b", "x": 0.43, "y": 0.64, "w": 0.27, "h": 0.26, "text": t["arm_c"], "style": "ctl"},
                       {"id": "ep", "x": 0.77, "y": 0.34, "w": 0.23, "h": 0.32, "text": t["ep"]}],
             "edges": [{"from": "pop", "to": "r"}, {"from": "r", "to": "a", "elbow": True}, {"from": "r", "to": "b", "elbow": True},
                       {"from": "a", "to": "ep", "elbow": True}, {"from": "b", "to": "ep", "elbow": True}]},
            {"type": "figure-text", "title": t["t3"], "image": "1-kaplan-meier.png", "alt": "Kaplan–Meier curve",
             "credit": t["credit3"], "bullets": t["b3"], "takeaway": t["take3"], "split": 0.62},
            {"type": "figure-text", "title": t["t4"], "image": "2-forest.png", "alt": "Forest plot",
             "credit": t["credit4"], "bullets": t["b4"], "takeaway": t["take4"], "split": 0.62},
            {"type": "chart", "title": t["t5"], "chart": "line", "categories": t["months"],
             "series": [{"name": t["s_int"], "values": [p[0] for p in snot["intervention"]], "color": "#C8372D"},
                        {"name": t["s_ctl"], "values": [p[0] for p in snot["control"]], "color": "#56677F"}],
             "number_format": "0", "credit": t["credit5"]},
            {"type": "big-number", "title": t["t6"],
             "numbers": [{"value": a, "label": l, "context": cx, "color": col}
                         for (a, col), l, cx in zip(t["n6"], t["lab6"], t["ctx6"])]},
            {"type": "two-column", "title": t["t7"],
             "left": {"heading": t["strong"][0], "bullets": t["strong"][1], "style": "primary"},
             "right": {"heading": t["weak"][0], "bullets": t["weak"][1], "style": "int"}, "takeaway": t["take7"]},
            {"type": "key-message", "message": t["t8"], "support": t["sup8"]},
            {"type": "references", "title": t["t9"], "items": t["refs"]},
            {"type": "closing", "title": t["t10"], "subtitle": t["sub10"], "presenter": t["who"]},
        ],
    }
    notes = ["Introduce DEMO-CRS as a teaching example with simulated data.",
             "Fifteen minutes: four questions, one per part.",
             "State the question in PICO form before showing any result.",
             "Walk through the trial schema from population to endpoint.",
             "Point to the separation of the curves before month 6.",
             "Subgroups are exploratory; say so.",
             "SNOT-22 ranges from 0 to 110; lower is better.",
             "Close the results with the absolute effect, not only the ratio.",
             "Weigh the strengths against what a simulated trial cannot show.",
             "Pause on the bottom line, then open the discussion question.",
             "Sources: the simulated data, the EPOS 2020 position paper and the SNOT-22 validation.",
             "Take questions."]
    assert len(notes) == len(spec["slides"])
    for s, n in zip(spec["slides"], notes):
        s["notes"] = n
    (b / "deck.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
