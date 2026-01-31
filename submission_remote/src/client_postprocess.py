"""
client_postprocess.py - Post-process decrypted results - convert payload back from float64 to int16.
"""
import pickle
import sys
import numpy as np
import torch

from submission_utils import PRECISION, MAX_VAL
from lattica_query.serialization.api_serialization_utils import load_proto_tensor
import submission_utils

def _sort_results(a):
    # Sort by the second column (index 1)
    a = a[a[:, 1].argsort()]
    return a

def _extract_final_results(a):
    full_payload_dim = instance_params.payload_dim + 1
    a = a.reshape(-1, full_payload_dim, instance_params.n_cols).moveaxis(-1, -2).reshape(-1, full_payload_dim)
    # Create a mask for rows that have any nonzero element
    valid_rows_mask = a[:, 0] > MAX_VAL * 1.4  # the marker row is expected to be 2 * MAX_VAL
    a = a[valid_rows_mask]
    scale = 2 * MAX_VAL * PRECISION / a[:, 0]  # scale each row by the expected marker value
    a = (a * scale[:, None]).round().to(torch.int64)
    return a

local_file_paths, instance_params = submission_utils.init(sys.argv)

# Read raw results and post-process
raw_result = pickle.load(open(local_file_paths.PATH_RAW_RESULT, "rb"))
raw_result = load_proto_tensor(raw_result)
raw_result = _extract_final_results(raw_result)
results    = _sort_results(raw_result)

# Remove marker from results
results_np = results[:, 1:].to(torch.int16).numpy()

if instance_params.count_only:
    # Extract count and save as np.int_ (system-dependent integer size)
    results_np = np.array([results_np.shape[0]], dtype=np.int_)

print(f'{results_np=}')
results_np.tofile(local_file_paths.PREDICTIONS_PATH)
