#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reconstruct 2D semantic maps per subject (like Wang & Bi Fig. 1C / 2C).

Inputs:
- preprocessed/all_rdms.npy        (n_subjects x 90 x 90 dissimilarity matrices)
- preprocessed/word_order.csv      (the 90 words, Chinese)
- experiment.js                    (contains zh/en mapping for labels)

Outputs:
- figures/subject_map_subjXX.png   (one plot per subject)
- figures/subject_maps_example.png (4-panel example for a few subjects)
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import MDS

RDM_FILE = "preprocessed/all_rdms.npy"
WORD_ORDER_FILE = "preprocessed/word_order.csv"
EXPERIMENT_JS_FILE = "experiment.js"
OUT_DIR = "figures"

os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------
# Load RDMs and word list
# -------------------------------------------------------
all_rdms = np.load(RDM_FILE)              # shape: n_subj x 90 x 90
n_subj, n_words, _ = all_rdms.shape
print(f"Loaded RDMs: {all_rdms.shape}")

words = pd.read_csv(WORD_ORDER_FILE, encoding="utf-8-sig")
words = words.reset_index().rename(columns={"index": "word_index", "word": "word_zh"})
print("Shape of all_rdms:", all_rdms.shape)


# Load participant info; order must match all_rdms
participants = pd.read_csv("preprocessed/participant_info.csv")
print("Shape of participants:", participants.shape)

assert participants.shape[0] == all_rdms.shape[0], "Participants vs RDM count mismatch!"


# -------------------------------------------------------
# Paths (change if needed)
# -------------------------------------------------------


# -------------------------------------------------------
# zh -> en mapping from experiment.js
# -------------------------------------------------------
with open(EXPERIMENT_JS_FILE, "r", encoding="utf-8") as f:
    js = f.read()

pairs = re.findall(r'\{\s*zh:\s*"([^"]+)"\s*,\s*en:\s*"([^"]+)"\s*\}', js)
zh2en = {zh: en for zh, en in pairs}

words["word_en"] = words["word_zh"].map(zh2en).fillna(words["word_zh"])

# -------------------------------------------------------
# Category definitions (Chinese)
# -------------------------------------------------------
animals_zh = {
    "蚂蚁","猫","大象","长颈鹿","熊猫","兔子","老鼠","麻雀","老虎","乌龟"
}
body_parts_zh = {
    "脚踝","胳膊","耳朵","眼睛","手指","膝盖","嘴唇","鼻子","肩膀","大腿"
}
artifacts_zh = {
    "空调","斧头","床","扫帚","柜子","椅子","筷子","鼠标","锤子","钥匙",
    "微波炉","铅笔","冰箱","剪刀","沙发","勺子","桌子","电视","牙刷","洗衣机"
}
emotional_zh = {
    "愤怒","反感","冷漠","慈善","舒心","死亡","债务","沮丧","疾病","纠纷",
    "错误","兴奋","缘分","过失","恐惧","骗局","友情","快乐","天堂","敌意",
    "爱心","魔力","婚姻","奇迹","骄傲","难过","风景","光彩","创伤","暴力"
}
nonemotional_zh = {
    "协议","买卖","性质","概念","内容","数据","纪律","作用","身份","方法",
    "义务","现象","过程","原因","关系","结果","社会","地位","制度","团队"
}

def get_category(w):
    if w in animals_zh: return "Animal"
    if w in body_parts_zh: return "Face/Body Part"
    if w in artifacts_zh: return "Artifact"
    if w in emotional_zh: return "Emotional Nonobject"
    if w in nonemotional_zh: return "Nonemotional Nonobject"
    return "Unknown"

words["category"] = words["word_zh"].apply(get_category)

CATEGORY_COLORS = {
    "Animal": "#b2182b",
    "Face/Body Part": "#ef8a62",
    "Artifact": "#fddbc7",
    "Emotional Nonobject": "#4393c3",
    "Nonemotional Nonobject": "#2166ac",
    "Unknown": "#999999",
}

# -------------------------------------------------------
# Helper: embed one subject's RDM in 2D with MDS
# -------------------------------------------------------
def embed_subject(rdm, random_state=0):
    """
    Metric MDS on a single subject's 90x90 dissimilarity matrix.
    Returns: coords (90 x 2).
    """
    mds = MDS(
        n_components=2,
        dissimilarity="precomputed",
        random_state=random_state,
        n_init=4,
        max_iter=300,
    )
    coords = mds.fit_transform(rdm)
    return coords

# -------------------------------------------------------
# Helper: plot one subject's space
# -------------------------------------------------------
def plot_subject_space(subj_idx, highlight_word_en=None, ax=None):
    """
    subj_idx: 0-based index into all_rdms
    highlight_word_en: optional English word to box/highlight (e.g., "scenery")
    """
    rdm = all_rdms[subj_idx]
    coords = embed_subject(rdm, random_state=42)

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
        own_fig = True
    else:
        own_fig = False

    # Scatter points by category
    for cat, grp in words.groupby("category"):
        mask = grp["word_index"].values
        ax.scatter(
            coords[mask, 0],
            coords[mask, 1],
            s=40,
            color=CATEGORY_COLORS.get(cat, "#999999"),
            alpha=0.7,
            label=cat,
        )

    # Add text labels
    for i, row in words.iterrows():
        x, y = coords[i]
        label = row["word_en"]
        ax.text(x, y, label, fontsize=7, ha="center", va="center")

    # Optionally highlight one word (like "scenery")
    if highlight_word_en is not None:
        # find index of this word
        match = words[words["word_en"] == highlight_word_en]
        if len(match) == 1:
            idx = int(match["word_index"].iloc[0])
            x, y = coords[idx]
            ax.scatter([x], [y], s=80, facecolors="none", edgecolors="black", linewidths=1.5)
            ax.text(x, y, highlight_word_en, fontsize=8, fontweight="bold",
                    ha="center", va="center")

    ax.set_xticks([])
    ax.set_yticks([])
    pid = participants.loc[subj_idx, "participant_id"]
    ax.set_title(f"Participant {pid}")


    if own_fig:
        # legend once per figure if you want
        handles = [
            plt.Line2D([0], [0], marker='o', linestyle='', color=c, label=cat)
            for cat, c in CATEGORY_COLORS.items() if cat != "Unknown"
        ]
        ax.legend(handles=handles, fontsize=8, frameon=False)
        plt.tight_layout()
        plt.show()

    return ax

# -------------------------------------------------------
# 1) Make a map for each subject (optional)
# -------------------------------------------------------
for s in range(n_subj):
    pid = participants.loc[s, "participant_id"]

    fig, ax = plt.subplots(figsize=(6, 6))
    plot_subject_space(s, highlight_word_en="scenery", ax=ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{pid}.png"), dpi=300)
    plt.close(fig)

print("Saved per-participant maps using participant_id-based filenames.")


# -------------------------------------------------------
# 2) Example figure with 4 chosen subjects (like in the paper)
# -------------------------------------------------------
# -------------------------------------------------------
# 2) Big figure: 4 rows × 8 columns = 32 subjects
# -------------------------------------------------------
rows, cols = 4, 8
max_panels = rows * cols

# if you have fewer than 32 participants, adjust automatically
n_to_plot = min(n_subj, max_panels)
subjects_to_plot = list(range(n_to_plot))   # [0, 1, 2, ..., n_to_plot-1]

fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
axes = axes.flatten()

for ax, s in zip(axes, subjects_to_plot):
    plot_subject_space(s, highlight_word_en="scenery", ax=ax)
    pid = participants.loc[s, "participant_id"]
    ax.set_title(f"Participant {pid}", fontsize=8)

# hide any unused axes (if n_subj < 32)
for ax in axes[n_to_plot:]:
    ax.axis("off")

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "subject_maps_4x8.png"), dpi=300)
plt.close(fig)
print("Saved 4x8 subject map figure (up to 32 participants).")

