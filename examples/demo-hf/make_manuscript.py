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


banner = para("Demonstration manuscript · all data are simulated (DEMO-HF, seed 7) · not a real study",
              size=8.5, color="8A5B00", align=WD_ALIGN_PARAGRAPH.CENTER)
t = doc.add_paragraph()
run = t.add_run("Effect of structured post-discharge follow-up on heart-failure admissions: "
                "a simulated randomised trial (DEMO-HF)")
run.bold, run.font.size, run.font.name = True, Pt(16), "Liberation Sans"
para("Medskill Panda demonstration team", size=10)
para("Corresponding author: [MISSING: authors to confirm]", size=9, italic=True, color="617080")

doc.add_heading("Abstract", 1)
para("Readmission after hospitalisation for heart failure is frequent. We simulated a randomised trial "
     "to illustrate how every reported number can be traced to its analysis.", "Background.")
para(f"{r['n']} patients with heart failure with reduced ejection fraction were randomly assigned 1:1 to "
     "structured follow-up or usual care and followed for 24 months. The primary outcome was the first "
     "admission for heart failure.", "Methods.")
para(f"The 24-month cumulative incidence of admission was {r['cuminc24_intervention']}% with the intervention and "
     f"{r['cuminc24_control']}% with usual care ({r['events_intervention']} vs {r['events_control']} events; "
     f"rate ratio {r['rr']:.2f}, 95% CI {r['rr_lo']:.2f}–{r['rr_hi']:.2f}). The absolute difference was "
     f"{r['arr24']} percentage points, a number needed to treat of {r['nnt24']} over 24 months.", "Results.")
para("In this simulation, structured follow-up reduced admissions for heart failure; the estimates are "
     "illustrative only.", "Conclusions.")

doc.add_heading("Tóm tắt", 1)
para("Tái nhập viện sau đợt điều trị suy tim thường gặp. Chúng tôi mô phỏng một thử nghiệm ngẫu nhiên để "
     "minh hoạ cách truy nguyên từng con số được báo cáo.", "Đặt vấn đề.")
para(f"{r['n']} bệnh nhân suy tim phân suất tống máu giảm được phân ngẫu nhiên 1:1 vào nhóm theo dõi có cấu trúc "
     "hoặc chăm sóc thường quy, theo dõi 24 tháng. Tiêu chí chính là lần nhập viện đầu tiên vì suy tim.",
     "Phương pháp.")
para(f"Tỷ lệ nhập viện tích luỹ sau 24 tháng là {vi(r['cuminc24_intervention'])}% ở nhóm can thiệp và "
     f"{vi(r['cuminc24_control'])}% ở nhóm chứng ({r['events_intervention']} so với {r['events_control']} biến cố; "
     f"tỷ số tỷ suất {vi(r['rr'], 2)}, KTC 95% {vi(r['rr_lo'], 2)}–{vi(r['rr_hi'], 2)}). Chênh lệch tuyệt đối "
     f"{vi(r['arr24'])} điểm phần trăm, số cần điều trị {r['nnt24']} trong 24 tháng.", "Kết quả.")
para("Trong mô phỏng này, theo dõi có cấu trúc làm giảm nhập viện vì suy tim; các ước lượng chỉ mang tính "
     "minh hoạ.", "Kết luận.")
para("heart failure; readmission; randomised trial; simulation", "Keywords:", size=9.5)

doc.add_heading("Results", 1)
para(f"Baseline characteristics were similar between groups (Table 1). During 24 months, "
     f"{r['events_intervention']} patients in the intervention group and {r['events_control']} in the control "
     "group were admitted for heart failure (Figure 1).")
cap = para("Table 1. Baseline characteristics", size=9.5)
cap.runs[0].bold = True
rows = [("Characteristic", f"Intervention (n = {r['n_arm']})", f"Control (n = {r['n_arm']})"),
        ("Age, years, mean (SD)", f"{r['age_mean'][I]} ({r['age_sd'][I]})", f"{r['age_mean'][C]} ({r['age_sd'][C]})"),
        ("Women, %", f"{r['female_pct'][I]}", f"{r['female_pct'][C]}"),
        ("Diabetes, %", f"{r['diabetes_pct'][I]}", f"{r['diabetes_pct'][C]}"),
        ("Ejection fraction, %, mean", f"{r['ef_mean'][I]}", f"{r['ef_mean'][C]}")]
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
cap = para("Figure 1. Cumulative incidence of first admission for heart failure (Kaplan–Meier), simulated data.",
           size=9.5)
cap.runs[0].bold = True
doc.save(str(D / "manuscript" / "demo-hf.docx"))
print("ok")
