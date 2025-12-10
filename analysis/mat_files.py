import glob
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.spatial.distance import squareform

# ---------- 1. Load all .mat RDMs ----------
# adjust the pattern/path if they’re in a subfolder
mat_files = sorted(glob.glob("BehavioralSemanticDistanceMatrix/dismx_*.mat"))
print(f"Found {len(mat_files)} .mat files")

rdms = []
for f in mat_files:
    mat = loadmat(f)
    # adjust key name if different
    vec = mat["estimate_dissimMat_ltv"].ravel()
    rdm = squareform(vec)        # (90, 90)
    rdms.append(rdm)

rdms = np.stack(rdms, axis=0)    # (n_participants, 90, 90)
print("RDM array shape:", rdms.shape)

# ---------- 2. Mean distance matrix across participants ----------
mean_rdm = rdms.mean(axis=0)     # (90, 90)

# ---------- 3. Get lower-triangular pairs and find 10 smallest ----------
n_words = mean_rdm.shape[0]
i_idx, j_idx = np.tril_indices(n_words, k=-1)  # i < j
pair_dists = mean_rdm[i_idx, j_idx]           # 4005 values

# sort ascending (smallest distance = most similar)
sort_idx = np.argsort(pair_dists)
top_k = 10
best_idx = sort_idx[:top_k]

# ---------- 4. Load word list from Excel ----------
# inspect columns the first time if you’re unsure
words_df = pd.read_excel("Behav_Neural_word_ISC.xlsx")
print("Columns in word file:", words_df.columns)

# CHANGE this column name if needed to match your file
# e.g. 'Chinese', 'Word', 'word_zh', etc.
word_col = "Chinese"   # <-- adjust to actual column name
words = words_df[word_col].tolist()

assert len(words) == n_words, "Word list length must match RDM size (90)."

# ---------- 5. Print 10 most similar pairs ----------
print("\nTop 10 most similar word pairs (lowest mean distance):\n")
for rank, idx in enumerate(best_idx, start=1):
    i = i_idx[idx]
    j = j_idx[idx]
    dist = pair_dists[idx]
    w1 = words[i]
    w2 = words[j]
    print(f"{rank:2d}. {w1}  –  {w2}   (mean distance = {dist:.6f})")
