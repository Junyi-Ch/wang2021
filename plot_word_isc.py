#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plot Fisher-transformed ISC per word (Wang & Bi-style),
with ENGLISH labels taken from experiment.js.

Inputs:
- preprocessed/word_order.csv                (Chinese words in RDM order)
- results/step1_subject_bootstrap_stats.csv  (ISC stats per word_index)
- experiment.js                              (contains zh/en mapping in word_categories)

Output:
- results/word_ISC_barplot_english.png
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ===============================================================
# CONFIG: file paths (adjust if your structure is different)
# ===============================================================
WORD_ORDER_FILE = "preprocessed/word_order.csv"
ISC_FILE = "results/step1_subject_bootstrap_stats.csv"
EXPERIMENT_JS_FILE = "experiment.js"
OUTPUT_FIG = "results/word_ISC_barplot_english.png"

# ===============================================================
# 1. Build zh → en mapping from experiment.js
# ===============================================================

def load_zh_en_mapping(js_path):
    """
    Parse experiment.js and extract all { zh: "...", en: "..." } pairs.
    Returns a dict: { zh: en } with 90 unique entries.
    """
    with open(js_path, "r", encoding="utf-8") as f:
        text = f.read()

    # regex: { zh: "xxxx", en: "yyyy" }
    pairs = re.findall(r'\{\s*zh:\s*"([^"]+)"\s*,\s*en:\s*"([^"]+)"\s*\}', text)
    mapping = {}
    for zh, en in pairs:
        mapping[zh] = en
    return mapping

cn2en = load_zh_en_mapping(EXPERIMENT_JS_FILE)
print(f"Loaded {len(cn2en)} zh→en mappings from {EXPERIMENT_JS_FILE}")

# ===============================================================
# 2. Category definitions (still using Chinese words internally)
# ===============================================================

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

def get_category(word_zh):
    if word_zh in animals_zh:
        return "Animal"
    if word_zh in body_parts_zh:
        return "Face/Body Part"
    if word_zh in artifacts_zh:
        return "Artifact"
    if word_zh in emotional_zh:
        return "Emotional Nonobject"
    if word_zh in nonemotional_zh:
        return "Nonemotional Nonobject"
    return "Unknown"

CATEGORY_COLORS = {
    "Animal":               "#b2182b",
    "Face/Body Part":       "#ef8a62",
    "Artifact":             "#fddbc7",
    "Emotional Nonobject":  "#4393c3",
    "Nonemotional Nonobject":"#2166ac",
    "Unknown":              "#999999",
}

# ===============================================================
# 3. Load word order + ISC stats, attach labels and categories
# ===============================================================

# word_order.csv: one column "word" with Chinese words
words = pd.read_csv(WORD_ORDER_FILE, encoding="utf-8-sig")
words = words.reset_index().rename(columns={"index": "word_index", "word": "word_zh"})

# attach English translation
words["word_en"] = words["word_zh"].map(cn2en)

# ISC stats (Fisher-z)
isc = pd.read_csv(ISC_FILE)

# merge on word_index
df = isc.merge(words, on="word_index", how="left")

# category from Chinese labels
df["category"] = df["word_zh"].apply(get_category)

# sanity check
unknown_cat = df[df["category"] == "Unknown"]
if len(unknown_cat) > 0:
    print("⚠️ Warning: some words didn't match any category:")
    print(unknown_cat[["word_index", "word_zh", "word_en"]])

missing_en = df[df["word_en"].isna()]
if len(missing_en) > 0:
    print("⚠️ Warning: some words have no English translation in experiment.js:")
    print(missing_en[["word_index", "word_zh"]])

# ===============================================================
# 4. Sort by mean ISC (Fisher-z) and prepare for plotting
# ===============================================================

df_sorted = df.sort_values("mean", ascending=False).reset_index(drop=True)

x = np.arange(len(df_sorted))
y = df_sorted["mean"].values  # Fisher-transformed ISC (z)
ci_low = df_sorted["ci_2.5"].values
ci_high = df_sorted["ci_97.5"].values
yerr = np.vstack([y - ci_low, ci_high - y])
colors = df_sorted["category"].map(CATEGORY_COLORS).values

# ===============================================================
# 5. Plot with ENGLISH x-axis labels
# ===============================================================

plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(18, 6))

# bars
ax.bar(x, y, color=colors, edgecolor="black", linewidth=0.5)

# error bars
ax.errorbar(
    x, y, yerr=yerr,
    fmt="none",
    ecolor="black",
    elinewidth=0.8,
    capsize=2,
)

# x-axis labels: English words
ax.set_xticks(x)
ax.set_xticklabels(
    df_sorted["word_en"],
    rotation=90,
    fontsize=7,
)

ax.set_ylabel("Fisher-transformed ISC", fontsize=12)
ax.set_xlabel("Words (sorted by ISC)", fontsize=12)

ax.set_xlim(-0.5, len(x) - 0.5)
ax.set_ylim(bottom=0.0)
plt.tight_layout()

# legend
handles = [
    Patch(facecolor=CATEGORY_COLORS[k], edgecolor="black", label=k)
    for k in ["Animal", "Face/Body Part", "Artifact",
              "Emotional Nonobject", "Nonemotional Nonobject"]
]
ax.legend(handles=handles, loc="upper right", frameon=False)

# save figure
os.makedirs(os.path.dirname(OUTPUT_FIG), exist_ok=True)
plt.savefig(OUTPUT_FIG, dpi=300)
plt.close()

print(f"🎉 Saved English-label ISC plot to: {OUTPUT_FIG}")
