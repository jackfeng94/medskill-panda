"""Write a demonstration manuscript (.docx) from results.json: English text, Vietnamese abstract."""
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

D = Path(sys.argv[1])
r = json.loads((D / "out" / "results.json").read_text(encoding="utf-8"))
I, C = "intervention", "control"


def vi(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Cm(2.2))
sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)
st = doc.styles["Normal"]
st.font.name, st.font.size = "Liberation Serif", Pt(10.5)
st.paragraph_format.space_after = Pt(5)
st.paragraph_format.line_spacing = 1.12
for name, size in (("Heading 1", 12), ("Heading 2", 10.5)):
    h = doc.styles[name]
    h.font.name, h.font.size, h.font.bold = "Liberation Sans", Pt(size), True
    h.font.color.rgb = RGBColor(0x0F, 0x5E, 0x7A)
    h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(10), Pt(4)


def para(text, bold_lead=None, size=None, italic=False, align=None, color=None):
    p = doc.add_paragraph()
    if bold_lead:
        b = p.add_run(bold_lead + " ")
        b.bold = True
    run = p.add_run(text)
    run.italic = italic
    if size:
        for x in p.runs:
            x.font.size = Pt(size)
    if color:
        for x in p.runs:
            x.font.color.rgb = RGBColor.from_string(color)
    if align:
        p.alignment = align
    return p


banner = para("Demonstration manuscript · all data are simulated (DEMO-CRS, seed 7) · not a real study",
              size=8.5, color="8A5B00", align=WD_ALIGN_PARAGRAPH.CENTER)
t = doc.add_paragraph()
run = t.add_run("Structured postoperative care and nasal polyp recurrence after endoscopic sinus surgery: "
                "a simulated randomised trial (DEMO-CRS)")
run.bold, run.font.size, run.font.name = True, Pt(16), "Liberation Sans"
para("Medskill Panda demonstration team", size=10)
para("Corresponding author: [MISSING: authors to confirm]", size=9, italic=True, color="617080")
cross_en = {"Age < 50": "patients younger than 50", "Age ≥ 50": "patients aged 50 or older", "Women": "women",
            "Men": "men", "Asthma": "patients with asthma", "No asthma": "patients without asthma"}
cross = [cross_en[g["label"]] for g in r["subgroups"] if g["hi"] >= 1]

doc.add_heading("Abstract", 1)
para("Nasal polyps often recur after endoscopic sinus surgery for chronic rhinosinusitis. We simulated a "
     "randomised trial to illustrate how every reported number can be traced to its analysis.", "Background.")
para(f"{r['n']} adults with chronic rhinosinusitis with nasal polyps were randomly assigned 1:1, after "
     "endoscopic sinus surgery, to structured postoperative care (steroid irrigation and scheduled endoscopic "
     "visits) or usual care and followed for 24 months. The primary outcome was endoscopic polyp recurrence.",
     "Methods.")
para(f"The 24-month cumulative incidence of recurrence was {r['cuminc24_intervention']}% with structured care and "
     f"{r['cuminc24_control']}% with usual care ({r['events_intervention']} vs {r['events_control']} events; "
     f"rate ratio {r['rr']:.2f}, 95% CI {r['rr_lo']:.2f}–{r['rr_hi']:.2f}). The absolute difference was "
     f"{r['arr24']} percentage points, a number needed to treat of {r['nnt24']} over 24 months.", "Results.")
para("In this simulation, structured postoperative care reduced polyp recurrence; the estimates are "
     "illustrative only.", "Conclusions.")

doc.add_heading("Tóm tắt", 1)
para("Polyp mũi thường tái phát sau phẫu thuật nội soi xoang điều trị viêm mũi xoang mạn. Chúng tôi mô phỏng "
     "một thử nghiệm ngẫu nhiên để minh hoạ cách truy nguyên từng con số được báo cáo.", "Đặt vấn đề.")
para(f"{r['n']} người lớn viêm mũi xoang mạn có polyp mũi, sau phẫu thuật nội soi xoang, được phân ngẫu nhiên 1:1 "
     "vào nhóm chăm sóc có cấu trúc (rửa mũi corticoid và tái khám nội soi theo lịch) hoặc chăm sóc thường quy, "
     "theo dõi 24 tháng. Tiêu chí chính là tái phát polyp trên nội soi.", "Phương pháp.")
para(f"Tỷ lệ tái phát tích luỹ sau 24 tháng là {vi(r['cuminc24_intervention'])}% ở nhóm can thiệp và "
     f"{vi(r['cuminc24_control'])}% ở nhóm chứng ({r['events_intervention']} so với {r['events_control']} biến cố; "
     f"tỷ số tỷ suất {vi(r['rr'], 2)}, KTC 95% {vi(r['rr_lo'], 2)}–{vi(r['rr_hi'], 2)}). Chênh lệch tuyệt đối "
     f"{vi(r['arr24'])} điểm phần trăm, số cần điều trị {r['nnt24']} trong 24 tháng.", "Kết quả.")
para("Trong mô phỏng này, chăm sóc có cấu trúc sau mổ làm giảm tái phát polyp; các ước lượng chỉ mang tính "
     "minh hoạ.", "Kết luận.")
para("chronic rhinosinusitis; nasal polyps; endoscopic sinus surgery; recurrence; simulation", "Keywords:", size=9.5)

doc.add_heading("Introduction", 1)
para("Chronic rhinosinusitis with nasal polyps impairs smell, breathing and quality of life, and polyps may "
     "recur after endoscopic sinus surgery [1]. Postoperative care, including topical corticosteroids and "
     "follow-up endoscopy, is part of current recommendations, but how intensive that care should be is less "
     "settled [1]. Symptom burden is commonly measured with the 22-item Sinonasal Outcome Test [2].")
para("This manuscript reports a simulated trial. Its purpose is to show a complete, checkable chain from data "
     "to text; it is not evidence about the intervention.")

doc.add_heading("Methods", 1)
para(f"We simulated {r['n']} adults undergoing endoscopic sinus surgery for chronic rhinosinusitis with nasal "
     "polyps, randomly assigned in a 1:1 ratio to structured postoperative care or usual care. Structured care "
     "comprised steroid nasal irrigation and endoscopic visits at fixed intervals.", "Design and participants.")
para("The primary outcome was endoscopic polyp recurrence within 24 months. Symptoms were scored with "
     "SNOT-22 (0 to 110, lower is better) [2], and disease extent before surgery with the Lund–Mackay CT score [3].",
     "Outcomes.")
para("Cumulative incidence was estimated with the Kaplan–Meier method; rate ratios with 95% confidence intervals "
     "came from Poisson models of events per person-time. Subgroups were prespecified in the simulation code and "
     "are exploratory. All code and data are in the examples/demo-crs folder.", "Statistical analysis.")

doc.add_heading("Results", 1)
para(f"Baseline characteristics were similar between groups (Table 1). During 24 months, "
     f"{r['events_intervention']} patients in the intervention group and {r['events_control']} in the control "
     "group had endoscopic polyp recurrence (Figure 1).")
cap = para("Table 1. Baseline characteristics", size=9.5)
cap.runs[0].bold = True
rows = [("Characteristic", f"Intervention (n = {r['n_arm']})", f"Control (n = {r['n_arm']})"),
        ("Age, years, mean (SD)", f"{r['age_mean'][I]} ({r['age_sd'][I]})", f"{r['age_mean'][C]} ({r['age_sd'][C]})"),
        ("Women, %", f"{r['female_pct'][I]}", f"{r['female_pct'][C]}"),
        ("Asthma, %", f"{r['asthma_pct'][I]}", f"{r['asthma_pct'][C]}"),
        ("Lund–Mackay CT score, mean", f"{r['lmk_mean'][I]}", f"{r['lmk_mean'][C]}")]
tbl = doc.add_table(rows=len(rows), cols=3)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        cell = tbl.cell(i, j)
        cell.text = val
        for p in cell.paragraphs:
            for x in p.runs:
                x.font.size, x.bold = Pt(9.5), i == 0
            if j:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if i in (0, len(rows) - 1):  # three-line table rules
            tcPr = cell._tc.get_or_add_tcPr()
            b = OxmlElement("w:tcBorders")
            for edge in (("top", "bottom") if i == 0 else ("bottom",)):
                el = OxmlElement(f"w:{edge}")
                el.set(qn("w:val"), "single"), el.set(qn("w:sz"), "8"), el.set(qn("w:color"), "18222D")
                b.append(el)
            tcPr.append(b)
doc.add_paragraph()
doc.add_picture(str(D / "out" / "km.png"), width=Cm(13.5))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = para("Figure 1. Cumulative incidence of endoscopic polyp recurrence (Kaplan–Meier), simulated data.",
           size=9.5)
cap.runs[0].bold = True
sub = "; ".join(f"{g['label'].lower()}, {g['rr']:.2f} ({g['lo']:.2f}–{g['hi']:.2f})" for g in r["subgroups"])
para(f"Rate ratios by subgroup were {sub}; the intervals included 1 for {', '.join(cross)}.")

doc.add_heading("Discussion", 1)
para(f"In this simulated trial, structured postoperative care was associated with fewer polyp recurrences over two "
     f"years, an absolute difference of {r['arr24']} percentage points. The direction of effect was the same in "
     "every subgroup, but the subgroups were small and the analyses exploratory.")
para("The simulation has the limits of any simulation: it shows what the analysis would report under assumed "
     "effects, not what the intervention does. A real trial would also need to report adherence to irrigation, "
     "who assessed the endoscopy and whether they were blinded, adverse events of topical steroids, and cost.")
para("Structured postoperative care reduced simulated polyp recurrence. The value of the example lies in the "
     "traceable chain from data to every number in the text.", "Conclusion.")

doc.add_heading("References", 1)
for i, ref in enumerate([
        "Fokkens WJ, Lund VJ, Hopkins C, et al. European Position Paper on Rhinosinusitis and Nasal Polyps 2020. "
        "Rhinology. 2020;58(Suppl S29):1–464.",
        "Hopkins C, Gillett S, Slack R, Lund VJ, Browne JP. Psychometric validity of the 22-item Sinonasal Outcome "
        "Test. Clin Otolaryngol. 2009;34(5):447–454.",
        "Lund VJ, Mackay IS. Staging in rhinosinusitis. Rhinology. 1993;31(4):183–184."], 1):
    para(ref, f"{i}.", size=9.5)
doc.save(str(D / "manuscript" / "demo-crs.docx"))
print("ok")
