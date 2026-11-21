"""Write the DEMO-HF slides (EN and VI) from results.json, ready for compose_deck.py."""
import json
import shutil
import sys
from pathlib import Path

D = Path(sys.argv[1])
r = json.loads((D / "out" / "results.json").read_text(encoding="utf-8"))


def num(x, lang, nd=1):
    s = f"{x:.{nd}f}"
    return s.replace(".", ",") if lang == "vi" else s


S = {
 "en": dict(
  t1="In the simulated DEMO-HF trial, the intervention cut heart-failure admissions by a quarter",
  sub="Journal club · demonstration built with simulated data",
  who="Medskill Panda demo", whos="Built end to end with medical-deck",
  t2=f"Admissions diverged early and reached {num(r['cuminc24_intervention'],'en')}% vs {num(r['cuminc24_control'],'en')}% by month 24",
  big2=f"−{num(r['arr24'],'en')}", big2l=f"percentage points at 24 months<br>number needed to treat {r['nnt24']}",
  ev=f"{r['events_intervention']} vs {r['events_control']} admissions · {r['n_arm']} patients per arm",
  t3="The effect held across age, sex and diabetes subgroups",
  p3=[f"Overall rate ratio {num(r['rr'],'en',2)} (95% CI {num(r['rr_lo'],'en',2)}–{num(r['rr_hi'],'en',2)})",
      "Every subgroup estimate lies below 1",
      f"Age ≥ 70: interval reaches {num(r['subgroups'][1]['hi'],'en',2)}, fewer events"],
  t4=f"Treating {r['nnt24']} patients for two years prevents one admission",
  k=[(f"{num(r['cuminc24_control'],'en')}% → {num(r['cuminc24_intervention'],'en')}%", "24-month admission rate"),
     (num(r['rr'], 'en', 2), f"rate ratio, 95% CI {num(r['rr_lo'],'en',2)}–{num(r['rr_hi'],'en',2)}"),
     (str(r['nnt24']), "number needed to treat for 24 months")],
  credit="Source: simulated DEMO-HF data (seed 7); Kaplan–Meier estimate",
  credit3="Source: simulated DEMO-HF data (seed 7); Poisson rate ratios",
  cite="Simulated data for demonstration · DEMO-HF, seed 7",
  km="km.svg", forest="forest.svg",
 ),
 "vi": dict(
  t1="DEMO-HF mô phỏng: can thiệp giảm một phần tư số lần nhập viện vì suy tim",
  sub="Journal club · ví dụ minh hoạ dựng từ dữ liệu mô phỏng",
  who="Medskill Panda demo", whos="Dựng trọn quy trình bằng medical-deck",
  t2=f"Tách biệt sớm: {num(r['cuminc24_intervention'],'vi')}% so với {num(r['cuminc24_control'],'vi')}% nhập viện sau 24 tháng",
  big2=f"−{num(r['arr24'],'vi')}", big2l=f"điểm phần trăm sau 24 tháng<br>số cần điều trị {r['nnt24']}",
  ev=f"{r['events_intervention']} so với {r['events_control']} lần nhập viện · {r['n_arm']} bệnh nhân mỗi nhóm",
  t3="Hiệu quả nhất quán theo tuổi, giới và đái tháo đường",
  p3=[f"Tỷ số tỷ suất chung {num(r['rr'],'vi',2)} (KTC 95% {num(r['rr_lo'],'vi',2)}–{num(r['rr_hi'],'vi',2)})",
      "Mọi phân nhóm đều có ước lượng dưới 1",
      f"Từ 70 tuổi: khoảng tin cậy chạm {num(r['subgroups'][1]['hi'],'vi',2)}, ít biến cố hơn"],
  t4=f"Điều trị {r['nnt24']} bệnh nhân trong hai năm giúp tránh một lần nhập viện",
  k=[(f"{num(r['cuminc24_control'],'vi')}% → {num(r['cuminc24_intervention'],'vi')}%", "tỷ lệ nhập viện sau 24 tháng"),
     (num(r['rr'], 'vi', 2), f"tỷ số tỷ suất, KTC 95% {num(r['rr_lo'],'vi',2)}–{num(r['rr_hi'],'vi',2)}"),
     (str(r['nnt24']), "số cần điều trị trong 24 tháng")],
  credit="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 7); ước lượng Kaplan–Meier",
  credit3="Nguồn: dữ liệu mô phỏng DEMO-HF (seed 7); tỷ số tỷ suất Poisson",
  cite="Dữ liệu mô phỏng để minh hoạ · DEMO-HF, seed 7",
  km="km_vi.svg", forest="forest_vi.svg",
 ),
}

CSS = """:root{--primary:#0F5E7A;--int:#C8372D;--ctl:#56677F}
.slide.title h1{font-size:66px;top:280px}
.stat{display:flex;flex-direction:column;justify-content:center;height:100%}
.stat .ev{font-size:var(--small);color:var(--muted);margin-top:36px}
.kpis{display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:64px;margin-top:150px}
.kpis .big{white-space:nowrap}
.kpis .big{font-size:84px}
.kpis div div{font-size:28px;color:var(--muted);margin-top:14px;line-height:1.3}
.fig svg{width:100%;height:auto}
"""

for lang, s in S.items():
    b = D / f"deck_{lang}" / "build"
    b.mkdir(parents=True, exist_ok=True)
    for f in ("km.svg", "forest.svg"):
        shutil.copy(D / "out" / f, b / f)
    if lang == "vi":
        for f in ("km_vi.svg", "forest_vi.svg"):
            shutil.copy(D / "out" / f, b / f)
    pts = "".join(f"<li>{p}</li>" for p in s["p3"])
    kpis = "".join(f'<div><span class="big">{v}</span><div>{lab}</div></div>' for v, lab in s["k"])
    slides = f"""<section class="slide title" data-name="Title">
  <h1 class="a-in" style="--d:.1s">{s['t1']}</h1>
  <div class="sub a-in" style="--d:.3s">{s['sub']}</div>
  <div class="who a-in" style="--d:.5s">{s['who']}<span>{s['whos']}</span></div>
  <aside class="notes">Introduce DEMO-HF as a teaching example with simulated data.</aside>
</section>
<section class="slide" data-name="Primary outcome">
  <h2 class="t a-in">{s['t2']}</h2>
  <div class="body"><div class="cols wide-left">
    <figure class="fig a-in" style="--d:.2s"><!--include: {s['km']}--><div class="credit">{s['credit']}</div></figure>
    <div class="stat a-in" style="--d:.35s"><span class="big">{s['big2']}</span><div class="big-label">{s['big2l']}</div><div class="ev">{s['ev']}</div></div>
  </div></div>
  <aside class="notes">[click] Point to the separation of the curves before month 6.</aside>
</section>
<section class="slide" data-name="Subgroups">
  <h2 class="t a-in">{s['t3']}</h2>
  <div class="body"><div class="cols wide-left">
    <figure class="fig a-in" style="--d:.2s"><!--include: {s['forest']}--><div class="credit">{s['credit3']}</div></figure>
    <div class="a-in" style="--d:.35s"><ul class="pts">{pts}</ul></div>
  </div></div>
  <aside class="notes">Subgroups are exploratory; say so.</aside>
</section>
<section class="slide" data-name="Bottom line">
  <h2 class="t a-in">{s['t4']}</h2>
  <div class="body"><div class="kpis a-in" style="--d:.2s">{kpis}</div></div>
  <aside class="notes">Close with the absolute effect, not only the ratio.</aside>
</section>
"""
    (b / "slides.html").write_text(slides, encoding="utf-8")
    (b / "deck.css").write_text(CSS, encoding="utf-8")
    (b.parent / "cite.txt").write_text(s["cite"], encoding="utf-8")
print("ok")
