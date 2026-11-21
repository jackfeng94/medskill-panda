"""Chart gallery for the DEMO-HF example: eight common medical chart types, EN and VI, as SVG.

Every value is simulated here or taken from out/results.json; nothing is typed in by hand.
The extra variables (KCCQ, ejection fraction, NYHA class, NT-proBNP cohort, screening counts) use
their own seed, so the numbers on the slides and in the manuscript do not change.

    python make_charts.py            -> out/charts/en/*.svg, out/charts/vi/*.svg, out/charts/values.json
"""
import json
import math
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "charts"
INT, CTL, INK, MUTE, GRID, TEAL = "#C8372D", "#56677F", "#18222D", "#6B7785", "#E6ECF0", "#0F5E7A"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12.5, "axes.edgecolor": MUTE, "axes.labelcolor": INK,
                     "xtick.color": MUTE, "ytick.color": MUTE, "svg.fonttype": "none", "axes.titleweight": "bold",
                     "axes.titlesize": 14, "axes.titlelocation": "left", "axes.titlecolor": INK})

# ------------------------------------------------------------------ the same trial as make_data.py
rng = np.random.default_rng(7)
N = 2000
arm = np.repeat([0, 1], N // 2)
age = rng.normal(68, 9, N).round()
female = rng.random(N) < 0.38
diabetes = rng.random(N) < 0.41
ef = rng.normal(31, 6, N).round()
rate = 0.0145 * np.exp(0.02 * (age - 68) + 0.25 * diabetes) * np.where(arm == 1, 0.75, 1.0)
t_event = rng.exponential(1 / rate)
t_cens = rng.uniform(18, 30, N)
time = np.minimum(t_event, np.minimum(t_cens, 24))
event = (t_event <= np.minimum(t_cens, 24)).astype(int)

# extra simulated variables, own seed
r2 = np.random.default_rng(11)
visits = np.array([0, 3, 6, 12, 24])
base_kccq = r2.normal(58, 16, N)
gain = np.where(arm[:, None] == 1, np.array([0, 4.5, 6.5, 7.5, 7.8]), np.array([0, 1.2, 1.8, 2.0, 1.6]))
kccq = np.clip(base_kccq[:, None] + gain + r2.normal(0, 9, (N, 5)), 0, 100)
ef_change = r2.normal(np.where(arm == 1, 4.1, 1.6), 6.5)
nyha_base = r2.choice([1, 2, 3, 4], N, p=[0.05, 0.55, 0.35, 0.05])
shift = np.where(arm == 1, r2.choice([-1, 0, 1], N, p=[0.38, 0.52, 0.10]), r2.choice([-1, 0, 1], N, p=[0.24, 0.58, 0.18]))
nyha_12 = np.clip(nyha_base + shift, 1, 4)
# a separate diagnostic cohort for the ROC example: breathless patients, NT-proBNP vs. heart failure
dx_hf = r2.random(600) < 0.42
dx_ntprobnp = np.exp(np.where(dx_hf, r2.normal(7.6, 1.0, 600), r2.normal(5.6, 1.1, 600)))
screened, not_eligible, declined = 2874, 611, 263   # screened = randomised + excluded

values = {}


def km(t, e):
    order = np.argsort(t)
    t, e = t[order], e[order]
    s, xs, ys, n = 1.0, [0.0], [1.0], len(t)
    for i, (ti, ei) in enumerate(zip(t, e)):
        if ei:
            s *= 1 - 1 / (n - i)
            xs.append(ti)
            ys.append(s)
    return np.array(xs), np.array(ys)


def mean_ci(x):
    m = float(np.mean(x))
    h = 1.96 * float(np.std(x, ddof=1)) / math.sqrt(len(x))
    return m, m - h, m + h


def auc(score, y):
    pos, neg = score[y == 1], score[y == 0]
    ranks = np.argsort(np.argsort(np.concatenate([pos, neg]))) + 1
    return (ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


L = {
 "en": dict(ctl="Control", int="Intervention", months="Months since randomisation", adm="HF admission (%)",
            risk_tbl="Number at risk", t1="Kaplan–Meier curve with numbers at risk",
            t2="Forest plot of subgroups", rr="Rate ratio (log scale)", overall="Overall",
            sub={"Age < 70": "Age < 70", "Age ≥ 70": "Age ≥ 70", "Women": "Women", "Men": "Men", "Diabetes": "Diabetes",
                 "No diabetes": "No diabetes"},
            t3="CONSORT flow diagram", screened="Assessed for eligibility", excl="Excluded", ne="not eligible", dec="declined",
            rand="Randomised", alloc="Allocated", lost="Follow-up < 24 months", anal="Analysed",
            t4="Line chart with 95% CI bands", kccq="KCCQ score (mean, 95% CI)", visit="Month",
            t5="Grouped bars with 95% CI", rate="24-month admission (%)", groups=["No diabetes", "Diabetes", "Age < 70", "Age ≥ 70"],
            t6="Box plot with individual points", efc="Change in LVEF at 12 months (points)",
            t7="Stacked bars: NYHA class shift", share="Patients (%)", base="Baseline", m12="Month 12", cls="Class",
            t8="ROC curve: NT-proBNP for heart failure", fpr="1 − specificity", tpr="Sensitivity", auc="AUC"),
 "vi": dict(ctl="Chứng", int="Can thiệp", months="Tháng kể từ phân nhóm ngẫu nhiên", adm="Nhập viện vì suy tim (%)",
            risk_tbl="Số còn theo dõi", t1="Đường Kaplan–Meier kèm số còn theo dõi",
            t2="Forest plot theo phân nhóm", rr="Tỷ số tỷ suất (thang log)", overall="Chung",
            sub={"Age < 70": "Dưới 70 tuổi", "Age ≥ 70": "Từ 70 tuổi", "Women": "Nữ", "Men": "Nam", "Diabetes": "Đái tháo đường",
                 "No diabetes": "Không ĐTĐ"},
            t3="Sơ đồ CONSORT", screened="Được đánh giá", excl="Loại", ne="không đủ tiêu chuẩn", dec="từ chối",
            rand="Phân nhóm ngẫu nhiên", alloc="Phân bổ", lost="Theo dõi < 24 tháng", anal="Phân tích",
            t4="Biểu đồ đường kèm dải KTC 95%", kccq="Điểm KCCQ (trung bình, KTC 95%)", visit="Tháng",
            t5="Cột nhóm kèm KTC 95%", rate="Nhập viện sau 24 tháng (%)", groups=["Không ĐTĐ", "Đái tháo đường", "Dưới 70 tuổi", "Từ 70 tuổi"],
            t6="Box plot kèm từng bệnh nhân", efc="Thay đổi LVEF sau 12 tháng (điểm)",
            t7="Cột chồng: thay đổi phân độ NYHA", share="Bệnh nhân (%)", base="Ban đầu", m12="Tháng 12", cls="Độ",
            t8="Đường ROC: NT-proBNP chẩn đoán suy tim", fpr="1 − độ đặc hiệu", tpr="Độ nhạy", auc="AUC"),
}


def fmt(v, lang, nd=2):
    s = f"{v:.{nd}f}"
    return s.replace(".", ",") if lang == "vi" else s


def tidy(ax, grid="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=1)
        ax.set_axisbelow(True)


def decimal_axis(ax, lang, axis="y", nd=1):
    if lang == "vi":
        def f_(v, _):
            s = f"{v:.{nd}f}".replace(".", ",")
            return s[:-2] if s.endswith(",0") else s
        f = FuncFormatter(f_)
        (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def save(fig, lang, name):
    d = OUT / lang
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / f"{name}.svg", format="svg")
    plt.close(fig)


def chart_km(lang, t):
    fig = plt.figure(figsize=(6.4, 4.6))
    ax = fig.add_axes([0.25, 0.37, 0.55, 0.53])
    tab = fig.add_axes([0.25, 0.04, 0.55, 0.16])
    marks = [0, 6, 12, 18, 24]
    for k, (a, col, lab) in enumerate(((0, CTL, t["ctl"]), (1, INT, t["int"]))):
        xs, ys = km(time[arm == a], event[arm == a])
        ax.step(np.append(xs, 24), 100 * (1 - np.append(ys, ys[-1])), where="post", color=col, lw=2.6)
        ax.text(24.4, 100 * (1 - ys[-1]), lab, color=col, va="center", fontsize=11.5, fontweight="bold")
        at_risk = [int((time[arm == a] >= m).sum()) for m in marks]
        values.setdefault("at_risk", {})[["control", "intervention"][a]] = at_risk
        for m, n in zip(marks, at_risk):
            tab.text(m, 1 - k, f"{n}", ha="center", va="center", color=col, fontsize=10.5)
        tab.text(-3.2, 1 - k, lab, ha="right", va="center", color=col, fontsize=10.5, fontweight="bold")
    ax.set(xlim=(0, 24), ylim=(0, 36), xticks=marks, xlabel=t["months"], ylabel=t["adm"])
    fig.suptitle(t["t1"], x=0.03, y=0.98, ha="left", fontsize=14, fontweight="bold", color=INK)
    tidy(ax)
    tab.set(xlim=(0, 24), ylim=(-0.6, 1.6))
    tab.axis("off")
    tab.text(-3.2, 1.55, t["risk_tbl"], ha="right", va="center", color=MUTE, fontsize=10)
    save(fig, lang, "1-kaplan-meier")


def chart_forest(lang, t, res):
    rows = res["subgroups"] + [{"label": "Overall", "rr": res["rr"], "lo": res["rr_lo"], "hi": res["rr_hi"]}]
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    for i, r in enumerate(rows[::-1]):
        ov = r["label"] == "Overall"
        lab = t["overall"] if ov else t["sub"][r["label"]]
        ax.plot([r["lo"], r["hi"]], [i, i], color=INK if ov else CTL, lw=2)
        ax.plot(r["rr"], i, marker="D" if ov else "s", color=INT if ov else CTL, ms=9 if ov else 6.5)
        ax.text(0.36, i, lab, va="center", fontsize=11, fontweight="bold" if ov else "normal", color=INK)
        ax.text(1.75, i, f'{fmt(r["rr"], lang)} ({fmt(r["lo"], lang)}–{fmt(r["hi"], lang)})', va="center", ha="right",
                fontsize=10.5, color=MUTE)
    ax.axvline(1, color=MUTE, lw=1, ls="--")
    ax.set_xscale("log")
    ax.set(xlim=(0.36, 1.75), yticks=[], xlabel=t["rr"], title=t["t2"])
    ax.set_xticks([0.5, 0.75, 1.0, 1.25])
    ax.set_xticklabels([fmt(v, lang, 2 if v == 0.75 or v == 1.25 else 1) for v in (0.5, 0.75, 1.0, 1.25)])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, lang, "2-forest")


def chart_consort(lang, t):
    lost = [int(((t_cens < 24) & (event == 0) & (arm == a)).sum()) for a in (1, 0)]
    values["consort"] = dict(screened=screened, not_eligible=not_eligible, declined=declined, randomised=N,
                             short_followup_intervention=lost[0], short_followup_control=lost[1])
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.02)
    ax.set(xlim=(0, 100), ylim=(0, 100), title=t["t3"])
    ax.axis("off")

    def box(x, y, w, h, text, col=TEAL, bold=False):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.3,rounding_size=1.8",
                                    fc="white", ec=col, lw=1.8))
        ax.text(x, y, text, ha="center", va="center", fontsize=11, color=INK, fontweight="bold" if bold else "normal",
                linespacing=1.25)

    def arrow(x0, y0, x1, y1):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", color=MUTE, lw=1.4))

    box(30, 91, 50, 10, f"{t['screened']}\nn = {screened}", bold=True)
    box(78, 75, 42, 15, f"{t['excl']}: n = {not_eligible + declined}\n{not_eligible} {t['ne']}\n{declined} {t['dec']}", MUTE)
    box(30, 59, 46, 10, f"{t['rand']}\nn = {N}", INK, True)
    arrow(30, 85.5, 30, 64.5)
    arrow(30, 75, 56.5, 75)
    for x, col, lab, lo in ((24, INT, t["int"], lost[0]), (76, CTL, t["ctl"], lost[1])):
        arrow(30 if x < 50 else 40, 53.5, x, 44.5)
        box(x, 39, 44, 10, f"{t['alloc']}: {lab}\nn = {N // 2}", col)
        box(x, 22, 44, 9, f"{t['lost']}\nn = {lo}", MUTE)
        box(x, 5.5, 44, 9, f"{t['anal']}\nn = {N // 2}", col, True)
        arrow(x, 33.5, x, 27)
        arrow(x, 17, x, 10.5)
    save(fig, lang, "3-consort")


def chart_line(lang, t):
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    values["kccq"] = {}
    for a, col, lab in ((0, CTL, t["ctl"]), (1, INT, t["int"])):
        stats = [mean_ci(kccq[arm == a, j]) for j in range(len(visits))]
        values["kccq"][["control", "intervention"][a]] = [[round(v, 1) for v in s] for s in stats]
        m = [s[0] for s in stats]
        ax.fill_between(visits, [s[1] for s in stats], [s[2] for s in stats], color=col, alpha=.16, lw=0)
        ax.plot(visits, m, color=col, lw=2.6, marker="o", ms=5.5)
        ax.text(24.6, m[-1], lab, color=col, va="center", fontsize=11, fontweight="bold")
    ax.set(xlim=(0, 24), xticks=visits, xlabel=t["visit"], ylabel=t["kccq"], title=t["t4"])
    decimal_axis(ax, lang, nd=0)
    tidy(ax)
    fig.subplots_adjust(right=0.77, left=0.13, bottom=0.14)
    save(fig, lang, "4-line")


def chart_bars(lang, t):
    masks = [~diabetes, diabetes, age < 70, age >= 70]
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    w = 0.36
    values["bars"] = {}
    for k, (a, col, lab) in enumerate(((0, CTL, t["ctl"]), (1, INT, t["int"]))):
        pts = []
        for m in masks:
            sel = m & (arm == a)
            p = event[sel].mean()
            h = 1.96 * math.sqrt(p * (1 - p) / sel.sum())
            pts.append((100 * p, 100 * h))
        values["bars"][["control", "intervention"][a]] = [[round(p, 1), round(h, 1)] for p, h in pts]
        x = np.arange(4) + (k - .5) * w
        ax.bar(x, [p for p, _ in pts], w * .92, color=col, label=lab)
        ax.errorbar(x, [p for p, _ in pts], yerr=[h for _, h in pts], fmt="none", ecolor=INK, elinewidth=1.2, capsize=3)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(t["groups"])
    ax.set(ylabel=t["rate"], title=t["t5"], ylim=(0, 40))
    ax.legend(frameon=False, loc="upper left", ncol=2)
    tidy(ax)
    fig.tight_layout()
    save(fig, lang, "5-bars")


def chart_box(lang, t):
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    data = [ef_change[arm == 0], ef_change[arm == 1]]
    values["ef_change_median"] = [round(float(np.median(d)), 1) for d in data]
    jit = np.random.default_rng(3)
    for i, (d, col) in enumerate(zip(data, (CTL, INT))):
        sample = jit.choice(d, 260, replace=False)
        ax.scatter(i + 1 + jit.uniform(-.18, .18, len(sample)), sample, s=9, color=col, alpha=.35, lw=0)
    bp = ax.boxplot(data, widths=.42, patch_artist=True, showfliers=False, medianprops=dict(color=INK, lw=2))
    for patch, col in zip(bp["boxes"], (CTL, INT)):
        patch.set(facecolor="white", edgecolor=col, lw=2, alpha=.85)
    for k, item in enumerate(bp["whiskers"] + bp["caps"]):
        item.set(color=MUTE)
    ax.axhline(0, color=MUTE, lw=1, ls="--")
    ax.set_xticks([1, 2])
    ax.set_xticklabels([t["ctl"], t["int"]])
    ax.set(ylabel=t["efc"], title=t["t6"])
    tidy(ax)
    fig.tight_layout()
    save(fig, lang, "6-box")


def chart_stacked(lang, t):
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    cols = ["#D7E9F1", "#8FC1D6", "#3A8DB0", "#0B4F67"]
    bars = [(f"{t['ctl']}\n{t['base']}", nyha_base[arm == 0]), (f"{t['ctl']}\n{t['m12']}", nyha_12[arm == 0]),
            (f"{t['int']}\n{t['base']}", nyha_base[arm == 1]), (f"{t['int']}\n{t['m12']}", nyha_12[arm == 1])]
    xs = [0, 1, 2.4, 3.4]
    values["nyha"] = {}
    for x, (lab, d) in zip(xs, bars):
        bottom = 0
        shares = [100 * float((d == c).mean()) for c in (1, 2, 3, 4)]
        values["nyha"][lab.replace("\n", " ")] = [round(s, 1) for s in shares]
        for c, s in enumerate(shares):
            ax.bar(x, s, .78, bottom=bottom, color=cols[c], edgecolor="white", lw=1)
            if s >= 7:
                ax.text(x, bottom + s / 2, f"{s:.0f}", ha="center", va="center", fontsize=10,
                        color="white" if c >= 2 else INK)
            bottom += s
    ax.set_xticks(xs)
    ax.set_xticklabels([b[0] for b in bars], fontsize=10.5)
    ax.set(ylabel=t["share"], ylim=(0, 100), title=t["t7"], xlim=(-.6, 4.3))
    for c in range(4):
        ax.bar(0, 0, color=cols[c], label=f"{t['cls']} {'I' * (c + 1) if c < 3 else 'IV'}")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(.5, -.2), fontsize=10)
    tidy(ax)
    fig.tight_layout()
    save(fig, lang, "7-stacked")


def chart_roc(lang, t):
    y, score = dx_hf.astype(int), dx_ntprobnp
    a = auc(score, y)
    values["auc_ntprobnp"] = round(float(a), 2)
    thr = np.sort(np.unique(score))[::-1]
    tpr = [((score >= c) & (y == 1)).sum() / (y == 1).sum() for c in thr]
    fpr = [((score >= c) & (y == 0)).sum() / (y == 0).sum() for c in thr]
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.plot([0, 1], [0, 1], color=MUTE, lw=1, ls="--")
    ax.plot([0] + fpr, [0] + tpr, color=TEAL, lw=2.6)
    ax.fill_between([0] + fpr, [0] + tpr, color=TEAL, alpha=.08)
    ax.text(.58, .22, f"{t['auc']} = {fmt(a, lang)}", fontsize=14, fontweight="bold", color=TEAL)
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel=t["fpr"], ylabel=t["tpr"], title=t["t8"])
    ax.set_aspect("equal", adjustable="box")
    decimal_axis(ax, lang, "x")
    decimal_axis(ax, lang, "y")
    tidy(ax, grid="both")
    fig.tight_layout()
    save(fig, lang, "8-roc")


if __name__ == "__main__":
    res = json.loads((HERE / "out" / "results.json").read_text(encoding="utf-8"))
    for lang, t in L.items():
        chart_km(lang, t)
        chart_forest(lang, t, res)
        chart_consort(lang, t)
        chart_line(lang, t)
        chart_bars(lang, t)
        chart_box(lang, t)
        chart_stacked(lang, t)
        chart_roc(lang, t)
    (OUT / "values.json").write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(values, ensure_ascii=False))
