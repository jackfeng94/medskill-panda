"""Synthetic DEMO-CRS trial (ENT): simulate data, compute every number shown in the demo, draw figures.

Chronic rhinosinusitis with nasal polyps after endoscopic sinus surgery: structured postoperative
care (steroid irrigation and scheduled endoscopic visits) versus usual care; primary outcome, endoscopic
polyp recurrence within 24 months.

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

N = 600
arm = np.repeat([0, 1], N // 2)                       # 0 control, 1 intervention
age = rng.normal(48, 13, N).clip(18, 85).round()
female = rng.random(N) < 0.40
asthma = rng.random(N) < 0.33
lmk = rng.normal(15, 4, N).clip(4, 24).round()        # Lund–Mackay CT score before surgery
base_rate = 0.0185 * np.exp(-0.008 * (age - 48) + 0.35 * asthma)
rate = base_rate * np.where(arm == 1, 0.65, 1.0)
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
res["asthma_pct"] = {k: round(100 * float(asthma[arm == a].mean()), 1) for a, k in ((1, "intervention"), (0, "control"))}
res["lmk_mean"] = {k: round(float(lmk[arm == a].mean()), 1) for a, k in ((1, "intervention"), (0, "control"))}
subgroups = [("Age < 50", age < 50), ("Age ≥ 50", age >= 50), ("Women", female), ("Men", ~female),
             ("Asthma", asthma), ("No asthma", ~asthma)]
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
    ax.set_ylim(0, 45)
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
        ax.text(-0.02, i, lab, va="center", ha="right", fontsize=15, fontweight="bold" if overall else "normal", color=INK,
                transform=ax.get_yaxis_transform())
        ax.text(2.1, i, f'{f(r["rr"])} ({f(r["lo"])}–{f(r["hi"])})', va="center", ha="right", fontsize=14, color=MUTE)
    ax.axvline(1, color=MUTE, lw=1.2, ls="--")
    ax.set_xscale("log")
    ax.set_xlim(0.3, 2.1)
    ax.set_xticks([0.5, 0.75, 1.0, 1.25])
    ax.set_xticklabels([s.replace(".", dec) for s in ("0.5", "0.75", "1.0", "1.25")])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_yticks([])
    ax.set_xlabel(xlabel)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.subplots_adjust(left=0.25, right=0.98, bottom=0.14, top=0.97)
    fig.savefig(path, format=fmt, dpi=220, transparent=(fmt == "svg"))
    plt.close(fig)


km_fig(OUT / "km.svg", ("Control", "Intervention"), "Months since surgery", "Polyp recurrence (%)", "svg")
km_fig(OUT / "km.png", ("Control", "Intervention"), "Months since surgery", "Polyp recurrence (%)", "png")
km_fig(OUT / "km_vi.svg", ("Chứng", "Can thiệp"), "Tháng sau phẫu thuật", "Tái phát polyp (%)", "svg")


def title_km(path, labels):
    """The same Kaplan–Meier curves, in light lines, for the dark title slide."""
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    for name, col, lab in (("control", "#FFFFFF", labels[0]), ("intervention", "#F4A79E", labels[1])):
        xs, ys = curves[name]
        ax.step(np.append(xs, 24), 100 * (1 - np.append(ys, ys[-1])), where="post", color=col, lw=4)
        ax.text(24.4, 100 * (1 - ys[-1]), lab, color=col, va="center", fontsize=17, fontweight="bold")
    ax.set(xlim=(0, 24), ylim=(0, 46), xticks=[0, 12, 24], yticks=[0, 10, 20, 30, 40])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#9CC3D2")
    ax.tick_params(colors="#BFD9E3", labelsize=14)
    fig.subplots_adjust(left=0.1, right=0.7, bottom=0.1, top=0.97)
    fig.savefig(path, format="svg", transparent=True)
    plt.close(fig)


title_km(OUT / "km_title.svg", ("Control", "Intervention"))
title_km(OUT / "km_title_vi.svg", ("Chứng", "Can thiệp"))
forest_fig(OUT / "forest.svg", "Overall", "Rate ratio (log scale)", "svg")
VI_LABELS = {"Age < 50": "Dưới 50 tuổi", "Age ≥ 50": "Từ 50 tuổi", "Women": "Nữ", "Men": "Nam",
             "Asthma": "Hen phế quản", "No asthma": "Không hen", "Overall": "Chung"}
forest_fig(OUT / "forest_vi.svg", "Overall", "Tỷ số tỷ suất (thang log)", "svg", labels=VI_LABELS, dec=",")
print(json.dumps(res, ensure_ascii=False))
