"""
client_preprocess_dataset.py - Adjust db.bin and payloads.bin as numpy files
"""
import pickle
import sys
import numpy as np
import torch

from submission_utils import PRECISION, MARKER_VALUE
import submission_utils

local_file_paths, instance_params = submission_utils.init(sys.argv)

# Get instance parameters for dimensions
db_size     = instance_params.get_db_size()
record_dim  = instance_params.get_record_dim()
payload_dim = instance_params.payload_dim

# Read database vectors (float32)
db = np.fromfile(local_file_paths.DB_PATH, dtype=np.float32)
db = db.reshape((db_size, record_dim))
db = torch.from_numpy(db)

# Read payload vectors (int16)
payloads = np.fromfile(local_file_paths.PAYLOAD_PATH, dtype=np.int16)
payloads = payloads.reshape((db_size, payload_dim))

# Add marker value (8192) to each payload to make it 8 int16 values
marker = np.full((db_size, 1), MARKER_VALUE, dtype=np.int16)
extended_payloads = np.concatenate([marker, payloads], axis=1)
extended_payloads = extended_payloads / PRECISION
payload = torch.from_numpy(extended_payloads)

# Save
pickle.dump(db,      open(local_file_paths.PROCESSED_DB_PATH,      "wb"))
pickle.dump(payload, open(local_file_paths.PROCESSED_PAYLOAD_PATH, "wb"))
