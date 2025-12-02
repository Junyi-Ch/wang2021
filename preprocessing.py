#!/usr/bin/env python3
"""
Clean jsPsych circle-arrangement CSVs for ISC analysis.

For each CSV in ./data:
- Read with UTF-8 (keeping Chinese correctly)
- Keep only trials with placements (arrangement trials)
- Infer the TRUE category by matching word sets:
    all_words, animals, body_parts, artifacts,
    emotional_nonobject, nonemotional_nonobject
- Overwrite trial_category with the inferred category
- Drop duplicate rows per participant × inferred_category
  (fixes the "extra last row" problem)
- Keep only relevant columns
- Write cleaned_<original>.csv to ./cleaned
"""

import os
import glob
import json
import pandas as pd

# -------- CONFIG --------
DATA_DIR = "data"
OUTPUT_DIR = "cleaned"

# Columns we actually need for ISC
KEEP_COLS = [
    "participant_number",
    "trial_category",
    "n_words",
    "placements",
    "dissimilarity_vector",
    "distance_matrix",
]

# -------- CATEGORY WORD SETS (from your experiment.js, zh only) --------
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

all_words_zh = animals_zh | body_parts_zh | artifacts_zh | emotional_zh | nonemotional_zh


def infer_category_from_words(words):
    """
    Given a list of Chinese words from placements, infer which category they belong to.
    Returns one of:
        "all_words", "animals", "body_parts", "artifacts",
        "emotional_nonobject", "nonemotional_nonobject",
        or "unknown_<n>" if not matched.
    """
    s = set(words)
    n = len(s)

    if n == 90 and s == all_words_zh:
        return "all_words"
    if n == 10:
        if s == animals_zh:
            return "animals"
        if s == body_parts_zh:
            return "body_parts"
    if n == 20:
        if s == artifacts_zh:
            return "artifacts"
        if s == nonemotional_zh:
            return "nonemotional_nonobject"
    if n == 30 and s == emotional_zh:
        return "emotional_nonobject"

    return f"unknown_{n}"


def clean_file(path):
    print(f"\nProcessing: {path}")
    # Read with BOM-safe encoding so Chinese stays correct
    df = pd.read_csv(path, encoding="utf-8-sig")

    if "placements" not in df.columns:
        print("  WARNING: no 'placements' column; skipping.")
        return None

    # Keep only rows with placements (arrangement trials)
    df_arr = df[df["placements"].notna()].copy()
    print(f"  Found {len(df_arr)} arrangement rows (with placements).")

    if df_arr.empty:
        print("  No usable arrangement rows; skipping file.")
        return None

    # Sort by trial_index if present (so we keep first occurrence later)
    if "trial_index" in df_arr.columns:
        df_arr = df_arr.sort_values("trial_index")

    # Infer category from the actual word sets
    inferred_categories = []
    inferred_n_words = []

    for i, row in df_arr.iterrows():
        try:
            placements = json.loads(row["placements"])
        except Exception as e:
            print(f"  WARNING: could not parse placements in row {i}: {e}")
            inferred_categories.append("parse_error")
            inferred_n_words.append(None)
            continue

        words = [p["word"] for p in placements]
        cat = infer_category_from_words(words)
        inferred_categories.append(cat)
        inferred_n_words.append(len(set(words)))

    df_arr["trial_category"] = inferred_categories  # overwrite old labels
    df_arr["n_words"] = inferred_n_words           # ensure consistent count

    # Drop any rows where category inference failed (unknown or parse_error)
    before = len(df_arr)
    df_arr = df_arr[~df_arr["trial_category"].str.startswith("unknown_")]
    df_arr = df_arr[df_arr["trial_category"] != "parse_error"]
    after = len(df_arr)
    if after < before:
        print(f"  Dropped {before - after} rows with unknown/invalid categories.")

    if df_arr.empty:
        print("  All arrangement rows were invalid; skipping file.")
        return None

    # Now drop duplicates: one row per participant × trial_category
    # (this removes the extra duplicated last row you saw)
    if "participant_number" not in df_arr.columns:
        print("  WARNING: no 'participant_number' column; skipping file.")
        return None

    before = len(df_arr)
    df_arr = df_arr.drop_duplicates(
        subset=["participant_number", "trial_category"],
        keep="first"
    )
    after = len(df_arr)
    if after < before:
        print(f"  Removed {before - after} duplicate rows (same participant × category).")

    # Keep only useful columns
    cols_found = [c for c in KEEP_COLS if c in df_arr.columns]
    missing = [c for c in KEEP_COLS if c not in df_arr.columns]
    if missing:
        print(f"  NOTE: missing columns {missing} in this file; they will be omitted.")

    df_arr = df_arr[cols_found]

    return df_arr


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not files:
        print(f"No CSV files found in {DATA_DIR}/")
        return

    for fpath in files:
        cleaned = clean_file(fpath)
        if cleaned is None:
            continue

        base = os.path.basename(fpath)
        out_path = os.path.join(OUTPUT_DIR, f"cleaned_{base}")
        cleaned.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"  Saved cleaned file → {out_path}")


if __name__ == "__main__":
    main()
