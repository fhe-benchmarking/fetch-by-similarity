import pickle
import sys
from submission_utils import PAYLOAD_MAX, PAYLOAD_PRECISION

import submission_utils
import numpy as np
import torch

local_file_paths, instance_params = submission_utils.init(sys.argv)


def _extract_final_results(a):
    full_payload_dim = instance_params.payload_dim + 1
    a = a.reshape(-1, full_payload_dim, instance_params.n_cols).moveaxis(-1, -2).reshape(-1, full_payload_dim)
    # Create a mask for rows that have any nonzero element
    max_val = PAYLOAD_MAX / PAYLOAD_PRECISION
    valid_rows_mask = a[:, 0] > max_val * 1.4  # the marker row is expected to be 2 * MAX_VAL
    a = a[valid_rows_mask]
    scale = 2 * PAYLOAD_MAX / a[:, 0]  # scale each row by the expected marker value
    a = (a * scale[:, None]).round().to(torch.int16).numpy()
    return a[:, 1:]


raw_result = pickle.load(open(local_file_paths.PATH_RAW_RESULT, "rb"))
results_np = _extract_final_results(raw_result)

results_np = results_np[np.lexsort(results_np.T[::-1])]

if instance_params.count_only:
    # Extract count and save as np.int_ (system-dependent integer size)
    results_np = np.array([results_np.shape[0]], dtype=np.int_)

results_np.tofile(local_file_paths.PREDICTIONS_PATH)
