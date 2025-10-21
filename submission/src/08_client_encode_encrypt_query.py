#!/usr/bin/env python3
"""
client_encode_encrypt_query.py - Encrypt query for homomorphic computation
"""
import sys
import os
import numpy as np
import torch
import json
import base64

from lattica_query.serialization.api_serialization_utils import dumps_proto_tensor
import lattica_query.query_toolkit as toolkit_interface
from harness.params import InstanceParams
from lib.server_logger import server_print
from lib.server_timer import ServerTimer


def main():
    # Parse arguments
    size = int(sys.argv[1])

    # Get instance parameters
    params = InstanceParams(size)
    record_dim = params.get_record_dim()

    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    dataset_dir = f"datasets/{instance_name}"
    io_dir = f"io/{instance_name}"
    key_dir = f"{io_dir}/keys"
    encrypted_dir = f"{io_dir}/encrypted"

    # Ensure directories exist
    os.makedirs(encrypted_dir, exist_ok=True)

    # Read the query vector
    query_path = f"{dataset_dir}/query.bin"
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"Query file not found: {query_path}. Make sure the harness has generated the query.")

    query_tensor = torch.from_numpy(np.fromfile(query_path, dtype=np.float32))
    server_print(f"Loaded query with shape: {query_tensor.shape}")

    # Load context and secret key from step 3
    context_path = f"{key_dir}/context.bin"
    sk_path = f"{key_dir}/sk.json"

    if not os.path.exists(context_path):
        raise FileNotFoundError(f"Context file not found: {context_path}. Make sure step 3 (key generation) was run first.")
    if not os.path.exists(sk_path):
        raise FileNotFoundError(f"Secret key file not found: {sk_path}. Make sure step 3 (key generation) was run first.")

    # Load context
    with open(context_path, "rb") as f:
        context = f.read()

    # Load secret key (decode from base64 JSON format)
    with open(sk_path, "r") as f:
        sk_data = json.load(f)

    secret_key = (
        base64.b64decode(sk_data[0]),
        base64.b64decode(sk_data[1])
    )

    timer = ServerTimer()
    n_slots = 2**9  # TODO: get from context
    query_tensor = query_tensor.expand(n_slots // record_dim, record_dim).reshape(n_slots)
    timer.log_step(8.1, "Expand and reshape")

    # Encrypt the query
    serialized_pt = dumps_proto_tensor(query_tensor)

    server_print("Encrypting query...")
    serialized_ct = toolkit_interface.enc(
        context,
        secret_key,
        serialized_pt,
        pack_for_transmission=True,
        n_axis_external=0
    )
    timer.log_step(8.2, "Encrypt query")

    # Save encrypted query
    encrypted_query_path = f"{encrypted_dir}/query.bin"
    with open(encrypted_query_path, "wb") as f:
        f.write(serialized_ct)

    server_print(f"Encrypted query saved to {encrypted_query_path}")

if __name__ == "__main__":
    main()
