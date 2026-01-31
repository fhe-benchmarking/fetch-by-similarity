"""
server_encrypted_compute.py - Run homomorphic computation on Lattica server
"""
import pickle
import sys

import submission_utils

local_file_paths, _ = submission_utils.init(sys.argv, mute_logs=False)

# Load encrypted query from step 8
ct = pickle.load(open(local_file_paths.get_ct_upload_path("query"), "rb"))

# Run homomorphic computation
client = submission_utils.get_lattica_client(local_file_paths)
ct_res = client.worker_api.apply_hom_pipeline(ct, block_index=1, return_new_state=True)

# Save encrypted result
pickle.dump(ct_res, open(local_file_paths.get_ct_download_path("query"), "wb"))
