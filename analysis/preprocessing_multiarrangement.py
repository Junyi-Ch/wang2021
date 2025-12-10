#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preprocessing for Multiarrangement Data (Behavioral Only)

- Loads cleaned participant CSV files (one per participant), each containing:
    * one full 90-word trial ("all_words")
    * 5 subset trials (animals, body_parts, artifacts,
      emotional_nonobject, nonemotional_nonobject)
    * columns: participant_number, trial_category, n_words,
      placements, dissimilarity_vector, distance_matrix

- For each participant:
    * Reconstructs per-trial distance matrices from dissimilarity_vector
    * Maps them into a single 90x90 RDM using the 90-word trial
      as the master word order
    * Averages distances across trials where a pair co-occurs

- Across participants:
    * Computes mean pairwise distance (MPD) for each RDM
    * Excludes participants whose MPD > (group mean + 3 SD)
      to remove random/chaotic responders

- Saves (FILTERED):
    * <output_folder>/all_rdms.npy          (shape: n_subj x 90 x 90)
    * <output_folder>/participant_info.csv  (participant_id)
    * <output_folder>/word_order.csv        (word, length = 90)
    * optional: dismx_<id>.mat files with vectorized RDMs

Usage:
    python preprocessing_multiarrangement.py <data_folder> [output_folder]

Example:
    python preprocessing_multiarrangement.py cleaned preprocessed
"""

import os
import sys
import glob
import json

import numpy as np
import pandas as pd
from scipy.spatial.distance import squareform
from tqdm import tqdm

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------

N_WORDS = 90                     # Total number of words in full set
JSON_COLUMN_NAME = "dissimilarity_vector"
ENCODING = "utf-8-sig"           # Keep Chinese characters intact


# ---------------------------------------------------------------------
# CORE FUNCTIONS
# ---------------------------------------------------------------------


def load_and_combine_multiarrangement_trials(data_folder, equal_weights=True):
    """
    Loads all participant CSV files and combines full + subset trials into
    one RDM per participant.

    Parameters
    ----------
    data_folder : str
        Folder containing participant CSV files (e.g. cleaned_*.csv)
    equal_weights : bool
        If True, use equal weights for all trials (simple averaging).
        If False, weight trials by mean(dissim)^2.

    Returns
    -------
    all_rdms : np.ndarray
        Array of shape (n_participants, N_WORDS, N_WORDS).
    participant_ids : list of str
        List of participant IDs, same order as all_rdms.
    master_words : list of str
        The word order corresponding to RDM rows/columns (length N_WORDS).
    """
    # Load only cleaned_*.csv from top folder
    csv_files = [
        f for f in glob.glob(os.path.join(data_folder, "cleaned_*.csv"))
        if os.path.isfile(f)
]

    if not csv_files:
        raise FileNotFoundError(f"No .csv files found in folder: {data_folder}")

    print(f"Found {len(csv_files)} cleaned CSV files. Processing...")

    all_rdms = []
    participant_ids = []
    all_wordlists = []

    for csv_file in tqdm(csv_files, desc="Processing participants"):
        df = pd.read_csv(csv_file, encoding=ENCODING)

        # Keep only rows that have dissimilarity data (arrangement trials)
        if JSON_COLUMN_NAME not in df.columns:
            print(f"  Warning: {os.path.basename(csv_file)} missing '{JSON_COLUMN_NAME}', skipping.")
            continue

        data_rows = df[df[JSON_COLUMN_NAME].notna()].copy()

        if len(data_rows) == 0:
            print(f"  Warning: No arrangement data in {os.path.basename(csv_file)}")
            continue

        if "participant_number" not in data_rows.columns:
            print(f"  Warning: 'participant_number' missing in {os.path.basename(csv_file)}, skipping.")
            continue

        participant_id = str(data_rows["participant_number"].iloc[0])

        try:
            rdm, wordlist = combine_trials_for_participant(data_rows, equal_weights=equal_weights)
        except Exception as e:
            print(f"  Error processing {participant_id} in {os.path.basename(csv_file)}: {e}")
            continue

        all_rdms.append(rdm)
        participant_ids.append(participant_id)
        all_wordlists.append(wordlist)

    if len(all_rdms) == 0:
        raise ValueError("No participants were successfully processed.")

    # --- Verify that the word order is identical across participants ---
    print("\nChecking consistency of word order across participants...")
    first = all_wordlists[0]
    for i, wl in enumerate(all_wordlists[1:], start=1):
        if wl != first:
            raise ValueError(
                f"Word order mismatch for participant {participant_ids[i]}. "
                "All participants must share the same 90-word order."
            )
    master_words = first
    print("Word order is consistent across all participants.")

    print(f"\nSuccessfully processed {len(all_rdms)} participants.")
    return np.array(all_rdms), participant_ids, master_words


def combine_trials_for_participant(data_rows, equal_weights=True):
    """
    Combines full + subset trials for a single participant into one 90x90 RDM.

    Parameters
    ----------
    data_rows : pd.DataFrame
        Rows containing trial data for one participant.
    equal_weights : bool
        If True, all trials get weight=1.0.
        If False, weight = (mean(dissim_vec))^2 per trial.

    Returns
    -------
    final_rdm : np.ndarray
        90x90 dissimilarity matrix averaged across all trials.
    master_word_list : list of str
        Word order used for this participant's RDM (length N_WORDS).
    """
    # --- Step 1: Get master word list from the full trial (90 words) ---
    full_trial = data_rows[data_rows["n_words"] == N_WORDS]

    if len(full_trial) == 0:
        raise ValueError(f"No full trial ({N_WORDS} words) found for this participant")

    if len(full_trial) > 1:
        print("  Warning: Multiple full trials found, using the first one.")
        full_trial = full_trial.iloc[:1]

    placements_json = full_trial["placements"].iloc[0]
    placements = json.loads(placements_json)
    master_word_list = [p["word"] for p in placements]

    if len(master_word_list) != N_WORDS:
        raise ValueError(
            f"Master word list has {len(master_word_list)} words, expected {N_WORDS}"
        )

    word_to_idx = {w: i for i, w in enumerate(master_word_list)}

    # --- Initialize accumulation matrices ---
    sum_matrix = np.zeros((N_WORDS, N_WORDS), dtype=float)
    count_matrix = np.zeros((N_WORDS, N_WORDS), dtype=float)

    # --- Step 2: Process each trial (full + subsets) ---
    for _, row in data_rows.iterrows():
        n_words = int(row["n_words"])

        # Words in this trial
        placements = json.loads(row["placements"])
        trial_words = [p["word"] for p in placements]

        # Dissimilarity vector for this trial
        dissim_vec = json.loads(row[JSON_COLUMN_NAME])

        expected_len = n_words * (n_words - 1) // 2
        if len(dissim_vec) != expected_len:
            print(
                f"  Warning: Trial with {n_words} words has vector length "
                f"{len(dissim_vec)}, expected {expected_len}. Skipping trial."
            )
            continue

        trial_matrix = squareform(dissim_vec)

        # Determine weight for this trial
        if equal_weights:
            weight = 1.0
        else:
            # Kriegeskorte & Mur style: larger distances → more evidence
            weight = (np.mean(dissim_vec) ** 2) if len(dissim_vec) > 0 else 0.0
            if weight <= 0:
                weight = 1.0

        # Map trial distances into the full 90x90 matrix
        for i in range(n_words):
            for j in range(i + 1, n_words):
                w_i = trial_words[i]
                w_j = trial_words[j]

                try:
                    mi = word_to_idx[w_i]
                    mj = word_to_idx[w_j]
                except KeyError as e:
                    print(f"  Warning: Word {e} not in master list; skipping pair.")
                    continue

                d = trial_matrix[i, j]
                sum_matrix[mi, mj] += weight * d
                sum_matrix[mj, mi] += weight * d
                count_matrix[mi, mj] += weight
                count_matrix[mj, mi] += weight

    # --- Step 3: Compute weighted average RDM ---
    with np.errstate(divide="ignore", invalid="ignore"):
        final_rdm = sum_matrix / count_matrix

    # Set diagonal to 0 (self-dissimilarity)
    np.fill_diagonal(final_rdm, 0.0)

    # Fill any NaNs (pairs never co-occurred) with mean of observed distances
    if np.isnan(final_rdm).any():
        mean_val = np.nanmean(final_rdm)
        final_rdm = np.nan_to_num(final_rdm, nan=mean_val)

    return final_rdm, master_word_list


def compute_mean_pairwise_distance(rdm):
    """
    Computes mean pairwise distance (MPD) for one RDM, ignoring diagonal.

    Parameters
    ----------
    rdm : np.ndarray
        Square dissimilarity matrix (N_WORDS x N_WORDS).

    Returns
    -------
    float
        Mean of off-diagonal entries.
    """
    n = rdm.shape[0]
    mask = ~np.eye(n, dtype=bool)
    vals = rdm[mask]
    vals = vals[~np.isnan(vals)]
    return float(vals.mean())


def filter_participants_by_mpd(all_rdms, participant_ids, z_threshold=3.0):
    """
    Exclude participants whose mean pairwise distance (MPD) is greater than
    (group mean + z_threshold * SD).

    Parameters
    ----------
    all_rdms : np.ndarray
        Array of shape (n_participants, N_WORDS, N_WORDS).
    participant_ids : list of str
        Participant IDs in the same order.
    z_threshold : float
        Number of standard deviations above mean to define outliers.

    Returns
    -------
    rdms_filtered : np.ndarray
        Filtered RDMs.
    ids_filtered : np.ndarray
        Filtered participant IDs.
    mpd : np.ndarray
        MPD values for all participants (unfiltered).
    bad_idx : np.ndarray
        Indices of excluded participants (0-based).
    """
    rdms = np.asarray(all_rdms)
    ids = np.asarray(participant_ids)

    mpd = np.array([compute_mean_pairwise_distance(r) for r in rdms])
    mean_mpd = mpd.mean()
    std_mpd = mpd.std(ddof=0)
    threshold = mean_mpd + z_threshold * std_mpd

    print("\n=== Mean Pairwise Distance (MPD) Filtering ===")
    print(f"Mean MPD: {mean_mpd:.4f}")
    print(f"Std  MPD: {std_mpd:.4f}")
    print(f"Threshold (mean + {z_threshold} SD): {threshold:.4f}")

    bad_idx = np.where(mpd > threshold)[0]
    print("Excluded participant indices (0-based):", bad_idx.tolist())
    print("Excluded participant IDs:", ids[bad_idx].tolist())

    rdms_filtered = np.delete(rdms, bad_idx, axis=0)
    ids_filtered = np.delete(ids, bad_idx, axis=0)

    print(f"Remaining participants after filtering: {len(ids_filtered)}")
    return rdms_filtered, ids_filtered, mpd, bad_idx


def save_rdms_to_mat_files(all_rdms, participant_ids, output_folder):
    """
    Optionally save RDMs as .mat files for MATLAB compatibility.

    Each file will contain a vectorized lower-triangular form of the RDM
    in the variable 'estimate_dissimMat_ltv'.
    """
    try:
        import scipy.io as sio
    except ImportError:
        print("scipy.io not available, skipping .mat file export.")
        return

    os.makedirs(output_folder, exist_ok=True)

    for rdm, pid in zip(all_rdms, participant_ids):
        vec = squareform(rdm, checks=False)  # lower triangle, no diagonal
        mat_path = os.path.join(output_folder, f"dismx_{pid}.mat")
        sio.savemat(mat_path, {"estimate_dissimMat_ltv": vec})

    print(f"Saved {len(all_rdms)} .mat files to {output_folder}")


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preprocessing_multiarrangement.py <data_folder> [output_folder]")
        print("\nExample:")
        print("  python preprocessing_multiarrangement.py ./cleaned ./preprocessed")
        sys.exit(1)

    data_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "./preprocessed"

    # 1) Load & combine trials into RDMs, and get the word order
    all_rdms, participant_ids, master_words = load_and_combine_multiarrangement_trials(
        data_folder,
        equal_weights=True,
    )

    # 2) Filter by MPD (exclude random/chaotic responders)
    rdms_filtered, ids_filtered, mpd_values, bad_idx = filter_participants_by_mpd(
        all_rdms,
        participant_ids,
        z_threshold=3.0,
    )

    # 3) Save filtered outputs
    os.makedirs(output_folder, exist_ok=True)

    # 3a. RDMs + participant info (filtered)
    np.save(os.path.join(output_folder, "all_rdms.npy"), rdms_filtered)
    pd.DataFrame({"participant_id": ids_filtered}).to_csv(
        os.path.join(output_folder, "participant_info.csv"),
        index=False,
    )

    # 3b. Word order (one list, same for all participants)
    pd.DataFrame({"word": master_words}).to_csv(
        os.path.join(output_folder, "word_order.csv"),
        index=False,
        encoding="utf-8-sig", 
    )

    # 3c. MPD diagnostics (optional but useful)
    pd.DataFrame({
        "participant_id": participant_ids,
        "mpd_value": mpd_values,
        "excluded": [i in bad_idx for i in range(len(participant_ids))]
    }).to_csv(
        os.path.join(output_folder, "mpd_values_all.csv"),
        index=False,
    )

    # 4) Optional: MATLAB .mat files for filtered participants
    save_rdms_to_mat_files(rdms_filtered, ids_filtered, output_folder)

    print("\nPreprocessing complete! Filtered files saved to", output_folder)
    print(f"  - all_rdms.npy: shape {rdms_filtered.shape}")
    print(f"  - participant_info.csv: {len(ids_filtered)} participants")
    print(f"  - word_order.csv: {len(master_words)} words")
    print("  - mpd_values_all.csv (MPD diagnostics)")
