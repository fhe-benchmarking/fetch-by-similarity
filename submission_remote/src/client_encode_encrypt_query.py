"""
client_encode_encrypt_query.py - Encrypt query for homomorphic computation
"""
import pickle
import sys
import numpy as np
import torch

from lattica_query.serialization.api_serialization_utils import dumps_proto_tensor
import lattica_query.query_toolkit as toolkit_interface
from harness.params import InstanceParams
import submission_utils

local_file_paths, instance_params = submission_utils.init(sys.argv)
record_dim = InstanceParams(instance_params.size).get_record_dim()

# Load context and secret key from step 3
context =    pickle.load(open(local_file_paths.PATH_CONTEXT, "rb"))
secret_key = pickle.load(open(local_file_paths.PATH_SK,      "rb"))

# Read the query vector
query_tensor = torch.from_numpy(np.fromfile(local_file_paths.QUERY_PATH, dtype=np.float32))
# Pad the query to match the number of slots and encrypt
query_tensor = query_tensor.expand(
    instance_params.n_slots // record_dim, record_dim).reshape(instance_params.n_slots)
ct = toolkit_interface.enc(
    context,
    secret_key,
    dumps_proto_tensor(query_tensor),
    pack_for_transmission=True,
    n_axis_external=0
)
pickle.dump(ct, open(local_file_paths.get_ct_upload_path("query"), "wb"))
