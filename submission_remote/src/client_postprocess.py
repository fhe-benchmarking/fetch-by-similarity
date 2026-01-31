import pickle
import sys
from submission_utils import PRECISION, MAX_VAL

import submission_utils
import numpy as np
import torch

local_file_paths, instance_params = submission_utils.init(sys.argv)

def _extract_final_results(a):
    full_payload_dim = instance_params.payload_dim + 1
    a = a.reshape(-1, full_payload_dim, instance_params.n_cols).moveaxis(-1, -2).reshape(-1, full_payload_dim)
    # Create a mask for rows that have any nonzero element
    valid_rows_mask = a[:, 0] > MAX_VAL * 1.4  # the marker row is expected to be 2 * MAX_VAL
    a = a[valid_rows_mask]
    scale = 2 * MAX_VAL * PRECISION / a[:, 0]  # scale each row by the expected marker value
    a = (a * scale[:, None]).round().to(torch.int64)
    return a


raw_result = pickle.load(open(local_file_paths.PATH_RAW_RESULT, "rb"))
results = _extract_final_results(raw_result)

# Sort by the second column (index 1)
results = results[results[:, 1].argsort()]
# Remove marker
results_np = results[:, 1:].to(torch.int16).numpy()

if instance_params.count_only:
    # Extract count and save as np.int_ (system-dependent integer size)
    results_np = np.array([results_np.shape[0]], dtype=np.int_)

results_np.tofile(local_file_paths.PREDICTIONS_PATH)
