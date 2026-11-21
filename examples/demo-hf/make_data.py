"""Synthetic DEMO-HF trial: simulate data, compute every number shown in the demo, draw figures.

All numbers in the demo deck and manuscript come from this file's output (results.json).
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)

N = 2000
arm = np.repeat([0, 1], N // 2)                       # 0 control, 1 intervention
age = rng.normal(68, 9, N).round()
female = rng.random(N) < 0.38
diabetes = rng.random(N) < 0.41
ef = rng.normal(31, 6, N).round()
base_rate = 0.0145 * np.exp(0.02 * (age - 68) + 0.25 * diabetes)
rate = base_rate * np.where(arm == 1, 0.75, 1.0)
t_event = rng.exponential(1 / rate)                   # months
t_cens = rng.uniform(18, 30, N)
time = np.minimum(t_event, np.minimum(t_cens, 24))
event = (t_event <= np.minimum(t_cens, 24)).astype(int)


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


def at(xs, ys, m):
    return ys[np.searchsorted(xs, m, side="right") - 1]


def rate_ratio(mask):
    ev = [event[mask & (arm == a)].sum() for a in (1, 0)]
    py = [time[mask & (arm == a)].sum() for a in (1, 0)]
    rr = (ev[0] / py[0]) / (ev[1] / py[1])
    se = math.sqrt(1 / ev[0] + 1 / ev[1])
    return rr, rr * math.exp(-1.96 * se), rr * math.exp(1.96 * se), int(mask.sum())


res = {"n": int(N), "n_arm": int(N // 2)}
curves = {}
for a, name in ((0, "control"), (1, "intervention")):
    xs, ys = km(time[arm == a], event[arm == a])
    curves[name] = (xs, ys)
    res[f"events_{name}"] = int(event[arm == a].sum())
    res[f"cuminc24_{name}"] = round(100 * (1 - at(xs, ys, 24)), 1)
rr, lo, hi, _ = rate_ratio(np.ones(N, bool))
res.update(rr=round(rr, 2), rr_lo=round(lo, 2), rr_hi=round(hi, 2))
res["arr24"] = round(res["cuminc24_control"] - res["cuminc24_intervention"], 1)
res["nnt24"] = math.ceil(100 / res["arr24"])
res["age_mean"] = {k: round(float(age[arm == a].mean()), 1) for a, k in ((1, "intervention"), (0, "control"))}
res["age_sd"] = {k: round(float(age[arm == a].std(ddof=1)), 1) for a, k in ((1, "intervention"), (0, "control"))}
res["female_pct"] = {k: round(100 * float(female[arm == a].mean()), 1) for a, k in ((1, "intervention"), (0, "control"))}
res["diabetes_pct"] = {k: round(100 * float(diabetes[arm == a].mean()), 1) for a, k in ((1, "intervention"), (0, "control"))}
res["ef_mean"] = {k: round(float(ef[arm == a].mean()), 1) for a, k in ((1, "intervention"), (0, "control"))}
subgroups = [("Age < 70", age < 70), ("Age ≥ 70", age >= 70), ("Women", female), ("Men", ~female),
             ("Diabetes", diabetes), ("No diabetes", ~diabetes)]
res["subgroups"] = [dict(zip(("label", "rr", "lo", "hi", "n"), (lab, *[round(v, 2) for v in rate_ratio(m)[:3]], rate_ratio(m)[3])))
                    for lab, m in subgroups]
(OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------- figures
INT, CTL, INK, MUTE = "#C8372D", "#56677F", "#18222D", "#6B7785"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 15, "axes.edgecolor": MUTE, "axes.labelcolor": INK,
                     "xtick.color": MUTE, "ytick.color": MUTE, "svg.fonttype": "none"})


def km_fig(path, labels, xlabel, ylabel, fmt):
    fig, ax = plt.subplots(figsize=(9.6, 6.9))
    for name, col, lab in (("control", CTL, labels[0]), ("intervention", INT, labels[1])):
        xs, ys = curves[name]
        ax.step(np.append(xs, 24), 100 * (1 - np.append(ys, ys[-1])), where="post", color=col, lw=3.2)
        ax.text(24.3, 100 * (1 - ys[-1]), lab, color=col, va="center", fontsize=15, fontweight="bold")
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 35)
    ax.set_xticks([0, 6, 12, 18, 24])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#E6ECF0", lw=1)
    fig.subplots_adjust(left=0.09, right=0.82, bottom=0.14, top=0.96)
    fig.savefig(path, format=fmt, dpi=220, transparent=(fmt == "svg"))
    plt.close(fig)


def forest_fig(path, overall_label, xlabel, fmt, labels=None, dec="."):
    f = lambda v: f"{v:.2f}".replace(".", dec)
    rows = res["subgroups"] + [{"label": overall_label, "rr": res["rr"], "lo": res["rr_lo"], "hi": res["rr_hi"], "n": N}]
    fig, ax = plt.subplots(figsize=(9.6, 6.6))
    for i, r in enumerate(rows[::-1]):
        lab = (labels or {}).get(r["label"], r["label"])
        overall = r["label"] == overall_label
        col = INK if overall else CTL
        ax.plot([r["lo"], r["hi"]], [i, i], color=col, lw=2.4)
        ax.plot(r["rr"], i, marker="D" if overall else "s", color=INT if overall else col, ms=11 if overall else 8)
        ax.text(0.33, i, lab, va="center", ha="left", fontsize=15, fontweight="bold" if overall else "normal", color=INK)
        ax.text(1.62, i, f'{f(r["rr"])} ({f(r["lo"])}–{f(r["hi"])})', va="center", ha="right", fontsize=14, color=MUTE)
    ax.axvline(1, color=MUTE, lw=1.2, ls="--")
    ax.set_xscale("log")
    ax.set_xlim(0.33, 1.62)
    ax.set_xticks([0.5, 0.75, 1.0, 1.25])
    ax.set_xticklabels([s.replace(".", dec) for s in ("0.5", "0.75", "1.0", "1.25")])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_yticks([])
    ax.set_xlabel(xlabel)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.axvspan(0.33, 0.62, color="white", zorder=-1)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.14, top=0.97)
    fig.savefig(path, format=fmt, dpi=220, transparent=(fmt == "svg"))
    plt.close(fig)


km_fig(OUT / "km.svg", ("Control", "Intervention"), "Months since randomisation", "HF admission (%)", "svg")
km_fig(OUT / "km.png", ("Control", "Intervention"), "Months since randomisation", "HF admission (%)", "png")
km_fig(OUT / "km_vi.svg", ("Chứng", "Can thiệp"), "Tháng kể từ phân nhóm ngẫu nhiên", "Nhập viện vì suy tim (%)", "svg")
forest_fig(OUT / "forest.svg", "Overall", "Rate ratio (log scale)", "svg")
VI_LABELS = {"Age < 70": "Dưới 70 tuổi", "Age ≥ 70": "Từ 70 tuổi", "Women": "Nữ", "Men": "Nam",
             "Diabetes": "Đái tháo đường", "No diabetes": "Không đái tháo đường", "Overall": "Chung"}
forest_fig(OUT / "forest_vi.svg", "Overall", "Tỷ số tỷ suất (thang log)", "svg", labels=VI_LABELS, dec=",")
print(json.dumps(res, ensure_ascii=False))
