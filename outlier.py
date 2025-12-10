import numpy as np
import pandas as pd
from scipy.stats import pearsonr

# --- Load data ---
all_rdms = np.load("preprocessed/all_rdms.npy")  # shape: (n_subj, 90, 90)
participants = pd.read_csv("preprocessed/participant_info.csv")

n_subj, n_words, _ = all_rdms.shape
print("all_rdms shape:", all_rdms.shape)

# helper: flatten upper triangle (excluding diagonal)
def vec_from_rdm(rdm):
    triu_idx = np.triu_indices(n_words, k=1)
    return rdm[triu_idx]

# --- Compute leave-one-out correlation for each subject ---
subj_quality = []

for s in range(n_subj):
    rdm_s = all_rdms[s]
    vec_s = vec_from_rdm(rdm_s)

    # mean RDM of all other subjects
    others = np.delete(all_rdms, s, axis=0)
    mean_rdm_others = others.mean(axis=0)
    vec_mean = vec_from_rdm(mean_rdm_others)

    r, _ = pearsonr(vec_s, vec_mean)
    subj_quality.append(r)

subj_quality = np.array(subj_quality)
participants["rdm_group_corr"] = subj_quality

print(participants)
