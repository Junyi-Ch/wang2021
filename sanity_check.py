import numpy as np
import pandas as pd

# Load data
all_rdms = np.load("processed_explo/all_rdms.npy")
words = pd.read_csv("processed_explo/word_order.csv")
participants = pd.read_csv("processed_explo/participant_info.csv")

print("RDM shape:", all_rdms.shape)
print("Words shape:", words.shape)
print(words.head())

# 'word' is the only column: use dataframe index as word index
def idx(w):
    matches = words[words["word"] == w]
    if matches.empty:
        print(f"[!] Word not found in word_order.csv: {w}")
        print("Here are some example words:", words["word"].head(20).tolist())
        raise SystemExit
    return matches.index[0]

# Your 10 target pairs
pairs = [
    ("胳膊", "肩膀"),
    ("嘴唇", "鼻子"),
    ("眼睛", "鼻子"),
    ("脚踝", "大腿"),
    ("嘴唇", "眼睛"),
    ("耳朵", "鼻子"),
    ("脚踝", "膝盖"),
    ("耳朵", "嘴唇"),
    ("桌子", "椅子"),
    ("手指", "胳膊"),
]

threshold = 0.3
n_subjects = all_rdms.shape[0]

# ---------- collect all distances + flag bad participants ----------
records = []
flagged = []  # participants with >= half relations above threshold

for s in range(n_subjects):
    pid = participants.loc[s, "participant_id"]
    count_above = 0
    pair_distances = []

    for pair_num, (a, b) in enumerate(pairs, start=1):
        i, j = idx(a), idx(b)
        d = all_rdms[s, i, j]
        pair_distances.append((pair_num, a, b, d))

        if d > threshold:
            count_above += 1

        # store for CSV
        records.append({
            "subject_index": s,
            "participant_id": pid,
            "pair_number": pair_num,
            "word1": a,
            "word2": b,
            "distance": d,
        })

    # check the criterion: at least half of the 10 relations above threshold
    if count_above >= len(pairs) / 2:
        flagged.append((s, pid, count_above, pair_distances))

# ---------- print flagged participants ----------
print(f"\nParticipants with at least half of the {len(pairs)} pairs having distance > {threshold}:")
if not flagged:
    print("  None.")
else:
    for s, pid, count_above, pair_distances in flagged:
        print(f"\nSubject {s} (participant_id = {pid})")
        print(f"  {count_above} out of {len(pairs)} pairs > {threshold}")
        for pair_num, a, b, d in pair_distances:
            mark = " *" if d > threshold else ""
            print(f"    {pair_num:2d}. {a} – {b}: {d:.4f}{mark}")

# ---------- save all pair distances to CSV ----------
df_pairs = pd.DataFrame(records)
df_pairs.to_csv("sanity_body_furniture_pairs_by_subject.csv", index=False)
print("\nSaved pair distances to sanity_body_furniture_pairs_by_subject.csv")
