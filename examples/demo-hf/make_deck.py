"""Write the DEMO-HF slides (EN and VI) from out/results.json and out/charts/values.json.

Run make_data.py and make_charts.py first. The output is build/slides.html + build/deck.css
for each language, ready for html-deck-building's compose_deck.py and build_deck.py.
"""
import json
import shutil
import sys
from pathlib import Path

D = Path(sys.argv[1])
ROOT = D.resolve().parents[1]
r = json.loads((D / "out" / "results.json").read_text(encoding="utf-8"))
v = json.loads((D / "out" / "charts" / "values.json").read_text(encoding="utf-8"))
k_int, k_ctl = v["kccq"]["intervention"], v["kccq"]["control"]
gain_int, gain_ctl = k_int[-1][0] - k_int[0][0], k_ctl[-1][0] - k_ctl[0][0]
c = v["consort"]


def num(x, lang, nd=1):
    s = f"{x:.{nd}f}"
    return s.replace(".", ",") if lang == "vi" else s


def thousands(n, lang):
    return f"{n:,}".replace(",", "." if lang == "vi" else ",")


S = {
 "en": dict(
  t1="In the simulated DEMO-HF trial, structured follow-up cut heart-failure admissions by a quarter",
  sub="Journal club · a demonstration built from simulated data", who="Medskill Panda demo",
  whos="Built end to end with medical-deck",
  t2=f"{thousands(r['n'], 'en')} patients were randomised 1:1 and followed for up to 24 months",
  design=[("Population", "Heart failure with reduced ejection fraction, after a hospital stay"),
          ("Intervention", "Structured post-discharge follow-up vs usual care"),
          ("Primary endpoint", "First admission for heart failure")],
  t3=f"Admissions diverged early and reached {num(r['cuminc24_intervention'], 'en')}% vs {num(r['cuminc24_control'], 'en')}% by month 24",
  big3=f"−{num(r['arr24'], 'en')}", lbl3="percentage points at 24 months",
  more3=[f"Number needed to treat: {r['nnt24']}", f"{r['events_intervention']} vs {r['events_control']} admissions"],
  t4="The effect held across age, sex and diabetes subgroups",
  p4=[f"Overall rate ratio {num(r['rr'], 'en', 2)} (95% CI {num(r['rr_lo'], 'en', 2)}–{num(r['rr_hi'], 'en', 2)})",
      "Every subgroup estimate lies below 1",
      f"Age ≥ 70: interval reaches {num(r['subgroups'][1]['hi'], 'en', 2)}, with fewer events",
      "Subgroups are exploratory"],
  t5="Quality of life improved by month 3 and the gain held to month 24",
  big5=f"+{num(gain_int, 'en')}", lbl5="KCCQ points with the intervention",
  more5=[f"+{num(gain_ctl, 'en')} points with usual care", "Higher scores mean better health status"],
  t6=f"Treating {r['nnt24']} patients for two years prevents one admission",
  facts=[(f"{num(r['cuminc24_control'], 'en')}% → {num(r['cuminc24_intervention'], 'en')}%", "24-month admission rate", "#56677F"),
         (num(r["rr"], "en", 2), f"rate ratio, 95% CI {num(r['rr_lo'], 'en', 2)}–{num(r['rr_hi'], 'en', 2)}", "#C8372D"),
         (str(r["nnt24"]), "number needed to treat for 24 months", "#0F5E7A")],
  caveat="Simulated example for demonstration: not evidence for practice.",
  credit2="Source: simulated DEMO-HF data (seed 7); CONSORT flow",
  credit3="Source: simulated DEMO-HF data (seed 7); Kaplan–Meier estimate",
  credit4="Source: simulated DEMO-HF data (seed 7); Poisson rate ratios",
  credit5="Source: simulated DEMO-HF data (seed 11); mean and 95% CI",
  cite="Simulated data for demonstration · DEMO-HF, seed 7",
  km="km.svg", forest="forest.svg",
 ),
 "vi": dict(
  t1="Trong thử nghiệm mô phỏng DEMO-HF, theo dõi có cấu trúc giảm một phần tư số lần nhập viện vì suy tim",
  sub="Journal club · ví dụ minh hoạ dựng từ dữ liệu mô phỏng", who="Medskill Panda demo",
  whos="Dựng trọn quy trình bằng medical-deck",
  t2=f"{thousands(r['n'], 'vi')} bệnh nhân được phân nhóm ngẫu nhiên 1:1 và theo dõi đến 24 tháng",
  design=[("Đối tượng", "Suy tim phân suất tống máu giảm, sau một đợt nằm viện"),
          ("Can thiệp", "Theo dõi có cấu trúc sau xuất viện so với chăm sóc thường quy"),
          ("Tiêu chí chính", "Lần nhập viện đầu tiên vì suy tim")],
  t3=f"Tách biệt sớm: {num(r['cuminc24_intervention'], 'vi')}% so với {num(r['cuminc24_control'], 'vi')}% nhập viện sau 24 tháng",
  big3=f"−{num(r['arr24'], 'vi')}", lbl3="điểm phần trăm sau 24 tháng",
  more3=[f"Số cần điều trị: {r['nnt24']}", f"{r['events_intervention']} so với {r['events_control']} lần nhập viện"],
  t4="Hiệu quả nhất quán theo tuổi, giới và đái tháo đường",
  p4=[f"Tỷ số tỷ suất chung {num(r['rr'], 'vi', 2)} (KTC 95% {num(r['rr_lo'], 'vi', 2)}–{num(r['rr_hi'], 'vi', 2)})",
      "Mọi phân nhóm đều có ước lượng dưới 1",
      f"Từ 70 tuổi: khoảng tin cậy chạm {num(r['subgroups'][1]['hi'], 'vi', 2)}, ít biến cố hơn",
      "Phân tích phân nhóm chỉ mang tính thăm dò"],
  t5="Chất lượng sống cải thiện từ tháng 3 và duy trì đến tháng 24",
  big5=f"+{num(gain_int, 'vi')}", lbl5="điểm KCCQ ở nhóm can thiệp",
  more5=[f"+{num(gain_ctl, 'vi')} điểm ở nhóm chăm sóc thường quy", "Điểm càng cao, tình trạng sức khoẻ càng tốt"],
  t6=f"Điều trị {r['nnt24']} bệnh nhân trong hai năm tránh được một lần nhập viện",
  facts=[(f"{num(r['cuminc24_control'], 'vi')}% → {num(r['cuminc24_intervention'], 'vi')}%", "tỷ lệ nhập viện sau 24 tháng", "#56677F"),
         (num(r["rr"], "vi", 2), f"tỷ số tỷ suất, KTC 95% {num(r['rr_lo'], 'vi', 2)}–{num(r['rr_hi'], 'vi', 2)}", "#C8372D"),
         (str(r["nnt24"]), "số cần điều trị trong 24 tháng", "#0F5E7A")],
  caveat="Ví dụ mô phỏng để minh hoạ: không phải bằng chứng cho thực hành.",
  credit2="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 7); sơ đồ CONSORT",
  credit3="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 7); ước lượng Kaplan–Meier",
  credit4="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 7); tỷ số tỷ suất Poisson",
  credit5="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 11); trung bình và KTC 95%",
  cite="Dữ liệu mô phỏng để minh hoạ · DEMO-HF, seed 7",
  km="km_vi.svg", forest="forest_vi.svg",
 ),
}

CSS = """:root{--primary:#0F5E7A;--primary-d:#0A4257;--int:#C8372D;--ctl:#56677F;--bg:#F4F7F9;--ink:#15202B;--ink2:#33414D;
  --font:'Inter','Segoe UI',Arial,sans-serif;--title-size:50px}
.slide{background:var(--bg)}
.slide h2.t{left:96px;right:96px;top:56px;padding-left:30px;border-left:10px solid var(--primary);letter-spacing:-.01em}
.slide .body{top:206px;bottom:104px}
.panel{background:#fff;border:1px solid #C9D3DA;padding:26px 34px;height:100%;
  display:flex;flex-direction:column;justify-content:center}
.panel svg{width:100%;height:auto;max-height:640px}
.panel .credit{font-size:18px;color:var(--muted);margin-top:10px}
.take{background:var(--primary);color:#fff;padding:44px 46px;height:100%;display:flex;flex-direction:column;justify-content:center}
.take .big{color:#fff;font-size:128px}
.take .lbl{font-size:28px;margin-top:10px;color:#D3E8EF}
.take hr{border:0;border-top:2px solid rgba(255,255,255,.28);margin:34px 0 26px;width:100%}
.take .sm{font-size:25px;color:#E8F3F7;margin:8px 0}
.take ul.pts{font-size:27px;line-height:1.4;color:#fff}.take ul.pts li::marker{color:#F2B8B2}
.design{display:grid;grid-template-columns:1.25fr 1fr;gap:40px;height:100%}
.design .row{display:flex;flex-direction:column;justify-content:center;gap:22px}
.design .item{background:#fff;border:1px solid #C9D3DA;padding:24px 28px;border-left:8px solid var(--primary)}
.design .item b{display:block;font-size:22px;color:var(--primary);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
.design .item span{font-size:28px;color:var(--ink);line-height:1.3}
.facts{display:grid;grid-template-columns:1.35fr 1fr 1fr;gap:34px;margin-top:70px}
.fact{background:#fff;border:1px solid #C9D3DA;padding:70px 44px;border-top:12px solid var(--c)}
.fact .big{font-size:104px;color:var(--c);white-space:nowrap}
.fact div{font-size:27px;color:var(--ink2);margin-top:16px;line-height:1.3}
.caveat{margin-top:90px;font-size:26px;color:#8A5B00;background:#FFF4D6;padding:18px 26px;display:inline-block}
.slide.title{background:#0F5E7A}
.slide.title h1{color:#fff;top:330px;font-size:70px;right:260px;letter-spacing:-.01em}
.slide.title .sub{color:#CFE6EE;top:620px}
.slide.title .who{color:#fff}.slide.title .who span{color:#BBD9E3}
.slide.title .mark{position:absolute;left:120px;top:120px;width:132px;height:132px;overflow:hidden;}
.slide.title .rule{position:absolute;left:120px;top:300px;width:140px;height:10px;background:var(--int)}
.slide.title .ftr{color:rgba(255,255,255,.65)}.slide.title .ftr .pg b{color:#fff}
"""


def take(big, lbl, more, bullets=False):
    rest = ("<ul class=\"pts\">" + "".join(f"<li>{m}</li>" for m in more) + "</ul>") if bullets else "".join(f'<div class="sm">{m}</div>' for m in more)
    head = f'<span class="big">{big}</span><div class="lbl">{lbl}</div><hr>' if big else ""
    return f'<div class="take a-in" style="--d:.35s">{head}{rest}</div>'


for lang, s in S.items():
    b = D / f"deck_{lang}" / "build"
    if b.exists():
        shutil.rmtree(b)
    b.mkdir(parents=True)
    for f in (s["km"], s["forest"]):
        shutil.copy(D / "out" / f, b / f)
    for f in ("3-consort.svg", "4-line.svg"):
        shutil.copy(D / "out" / "charts" / lang / "slide" / f, b / f)
    shutil.copy(ROOT / "assets" / "logo.svg", b / "logo.svg")
    design = "".join(f'<div class="item"><b>{h}</b><span>{t}</span></div>' for h, t in s["design"])
    facts = "".join(f'<div class="fact" style="--c:{col}"><span class="big">{val}</span><div>{lab}</div></div>' for val, lab, col in s["facts"])
    slides = f"""<section class="slide title" data-name="Title">
  <img class="mark a-in" src="logo.svg" alt="Medskill Panda">
  <div class="rule a-in" style="--d:.05s"></div>
  <h1 class="a-in" style="--d:.1s">{s['t1']}</h1>
  <div class="sub a-in" style="--d:.3s">{s['sub']}</div>
  <div class="who a-in" style="--d:.5s">{s['who']}<span>{s['whos']}</span></div>
  <aside class="notes">Introduce DEMO-HF as a teaching example with simulated data.</aside>
</section>
<section class="slide" data-name="Design">
  <h2 class="t a-in">{s['t2']}</h2>
  <div class="body"><div class="design">
    <figure class="panel fig a-in" style="--d:.2s"><!--include: 3-consort.svg--><div class="credit">{s['credit2']}</div></figure>
    <div class="row a-in" style="--d:.35s">{design}</div>
  </div></div>
  <aside class="notes">Walk through the flow from screening to analysis.</aside>
</section>
<section class="slide" data-name="Primary outcome">
  <h2 class="t a-in">{s['t3']}</h2>
  <div class="body"><div class="cols wide-left">
    <figure class="panel fig a-in" style="--d:.2s"><!--include: {s['km']}--><div class="credit">{s['credit3']}</div></figure>
    {take(s['big3'], s['lbl3'], s['more3'])}
  </div></div>
  <aside class="notes">[click] Point to the separation of the curves before month 6.</aside>
</section>
<section class="slide" data-name="Subgroups">
  <h2 class="t a-in">{s['t4']}</h2>
  <div class="body"><div class="cols wide-left">
    <figure class="panel fig a-in" style="--d:.2s"><!--include: {s['forest']}--><div class="credit">{s['credit4']}</div></figure>
    {take('', '', s['p4'], bullets=True)}
  </div></div>
  <aside class="notes">Subgroups are exploratory; say so.</aside>
</section>
<section class="slide" data-name="Quality of life">
  <h2 class="t a-in">{s['t5']}</h2>
  <div class="body"><div class="cols wide-left">
    <figure class="panel fig a-in" style="--d:.2s"><!--include: 4-line.svg--><div class="credit">{s['credit5']}</div></figure>
    {take(s['big5'], s['lbl5'], s['more5'])}
  </div></div>
  <aside class="notes">Mention that KCCQ ranges from 0 to 100.</aside>
</section>
<section class="slide" data-name="Bottom line">
  <h2 class="t a-in">{s['t6']}</h2>
  <div class="body"><div class="facts a-in" style="--d:.2s">{facts}</div>
    <div class="caveat a-in" style="--d:.4s">{s['caveat']}</div></div>
  <aside class="notes">Close with the absolute effect, not only the ratio.</aside>
</section>
"""
    (b / "slides.html").write_text(slides, encoding="utf-8")
    (b / "deck.css").write_text(CSS, encoding="utf-8")
    (b.parent / "cite.txt").write_text(s["cite"], encoding="utf-8")
print("ok")
