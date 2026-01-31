import pickle
import sys

from lattica_query.serialization.api_serialization_utils import load_proto_tensor
import lattica_query.query_toolkit as toolkit_interface
import submission_utils
from submission_utils import PRECISION, MAX_VAL
import numpy as np
import torch

local_file_paths, instance_params = submission_utils.init(sys.argv)

#====================== Decrypt ==============================

ct_res     = pickle.load(open(local_file_paths.get_ct_download_path("query"), "rb"))
context    = pickle.load(open(local_file_paths.PATH_CONTEXT, "rb"))
secret_key = pickle.load(open(local_file_paths.PATH_SK, "rb"))

serialized_res = toolkit_interface.dec(context, secret_key, ct_res,)
raw_result = load_proto_tensor(serialized_res)


#============ Post-process decrypted results =================

def _extract_final_results(a):
    full_payload_dim = instance_params.payload_dim + 1
    a = a.reshape(-1, full_payload_dim, instance_params.n_cols).moveaxis(-1, -2).reshape(-1, full_payload_dim)
    # Create a mask for rows that have any nonzero element
    valid_rows_mask = a[:, 0] > MAX_VAL * 1.4  # the marker row is expected to be 2 * MAX_VAL
    a = a[valid_rows_mask]
    scale = 2 * MAX_VAL * PRECISION / a[:, 0]  # scale each row by the expected marker value
    a = (a * scale[:, None]).round().to(torch.int64)
    return a

results = _extract_final_results(raw_result)

# Sort by the second column (index 1)
results = results[results[:, 1].argsort()]
# Remove marker
results_np = results[:, 1:].to(torch.int16).numpy()

if instance_params.count_only:
    # Extract count and save as np.int_ (system-dependent integer size)
    results_np = np.array([results_np.shape[0]], dtype=np.int_)

results_np.tofile(local_file_paths.PREDICTIONS_PATH)
