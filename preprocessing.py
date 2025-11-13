import pandas as pd
import numpy as np
import json
import os
import glob
from scipy.spatial.distance import squareform
from tqdm import tqdm

N_WORDS = 90 # Your new word count
JSON_COLUMN_NAME = 'dissimilarity_vector_json'
N_TRIALS = 6 # Your new trial count

def load_and_average_data(data_folder, output_folder):
    """
    Loads all .csv files, averages the 6 trials for each participant,
    and saves the final averaged RDMs.
    
    This function assumes you have ONE big CSV with all participant data,
    or multiple CSVs that, when combined, contain 6 rows per participant.
    """
    
    # --- 1. Load all data into one big DataFrame ---
    csv_files = glob.glob(os.path.join(data_folder, '*.csv'))
    if not csv_files:
        raise FileNotFoundError(f"No .csv files found in folder: {data_folder}")
        
    all_data_df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)
    
    # Filter for only the rows that have the data we need
    data_df = all_data_df[all_data_df[JSON_COLUMN_NAME].notna()].copy()
    
    # Group by participant
    grouped = data_df.groupby('participant_number')
    print(f"Found {len(grouped)} unique participants.")
    
    final_rdm_list = []
    
    # --- 2. Loop through each participant ---
    for participant_id, rows in tqdm(grouped, desc="Averaging Participant Trials"):
        
        if len(rows) != N_TRIALS:
            print(f"Warning: Participant {participant_id} has {len(rows)} trials, not {N_TRIALS}. Skipping.")
            continue
            
        try:
            participant_rdms = []
            # --- 3. Load all 6 trials for this participant ---
            for json_string in rows[JSON_COLUMN_NAME]:
                vector = json.loads(json_string)
                
                # Check vector length
                expected_length = (N_WORDS * (N_WORDS - 1)) // 2
                if len(vector) != expected_length:
                    raise ValueError(f"Incorrect vector length ({len(vector)}), expected {expected_length}")
                
                # Convert vector to full 90x90 matrix
                rdm = squareform(vector)
                participant_rdms.append(rdm)
            
            # --- 4. Average the 6 matrices ---
            # Stack into a 3D array (6, 90, 90) and average along axis 0
            avg_rdm = np.mean(np.array(participant_rdms), axis=0)
            
            # --- 5. Save the final averaged RDM ---
            # This is the single RDM that represents the participant
            final_rdm_list.append(avg_rdm)
            
            # (Optional: Save as .mat files for the MATLAB scripts)
            # vector_form = squareform(avg_rdm, checks=False)
            # mat_file_path = os.path.join(output_folder, f'dismx_{participant_id}.mat')
            # sio.savemat(mat_file_path, {'estimate_dissimMat_ltv': vector_form})
            
        except Exception as e:
            print(f"Error processing participant {participant_id}: {e}. Skipping.")
            
    # --- 6. Return the final 3D array (n_subjects, 90, 90) ---
    print(f"\nSuccessfully processed {len(final_rdm_list)} participants.")
    return np.array(final_rdm_list)

# --- Example of how to run this function ---
# output_folder = './averaged_mat_files' # Create this folder
# os.makedirs(output_folder, exist_ok=True)
# all_averaged_rdms = load_and_average_data('./data', output_folder)
#
# Now 'all_averaged_rdms' is the (n_subjects, 90, 90) array
# that the rest of the Python analysis script (`run_step1...`) can use.