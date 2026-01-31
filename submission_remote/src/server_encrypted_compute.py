"""
server_encrypted_compute.py - Run homomorphic computation on Lattica server
"""
import json
import pickle
import sys

import submission_utils

local_file_paths, _ = submission_utils.init(sys.argv, mute_logs=False)

# Redirect stdout to capture server timing report
real_stdout = sys.stdout
sys.stdout = submission_utils.StdoutListener("apply_hom_pipeline timing: ")

# Load encrypted query from step 8
ct = pickle.load(open(local_file_paths.get_ct_upload_path("query"), "rb"))

# Run homomorphic computation
client = submission_utils.get_lattica_client(local_file_paths)
ct_res = client.worker_api.apply_hom_pipeline(ct, block_index=1, return_new_state=True)

# Save encrypted result
pickle.dump(ct_res, open(local_file_paths.get_ct_download_path("query"), "wb"))

# Parse and save server timing report
server_report = sys.stdout.saved_report
server_report_for_harness = {
    "GPU time":      server_report["worker"]                             / 1000.0,
    "Queue time":   (server_report["logic"]   - server_report["worker"]) / 1000.0,
    "Network time": (server_report["network"]  - server_report["logic"]) / 1000.0,
}
with open(local_file_paths.SERVER_TIMES_PATH, "w") as f:
    json.dump(server_report_for_harness, f)
