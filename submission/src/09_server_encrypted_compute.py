#!/usr/bin/env python3
"""
server_encrypted_compute.py - Run homomorphic computation on Lattica server
"""
import sys
import os

from lattica_query.worker_api import LatticaWorkerAPI
from lib.server_logger import server_print
from lib.server_timer import ServerTimer
from lib.constants import TOKEN


def main():
    # Parse arguments
    size = int(sys.argv[1])
    count_only = len(sys.argv) > 2 and sys.argv[2] == "--count_only"

    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    io_dir = f"io/{instance_name}"
    encrypted_dir = f"{io_dir}/encrypted"

    # Load encrypted query from step 8
    encrypted_query_path = f"{encrypted_dir}/query.bin"
    if not os.path.exists(encrypted_query_path):
        raise FileNotFoundError(f"Encrypted query not found: {encrypted_query_path}. Make sure step 8 was run first.")

    server_print(f"Loading encrypted query from {encrypted_query_path}")
    with open(encrypted_query_path, "rb") as f:
        serialized_ct = f.read()

    # Initialize timer
    timer = ServerTimer()

    # Initialize worker API
    server_print("Initializing LatticaWorkerAPI...")
    worker_api = LatticaWorkerAPI(TOKEN)

    # Run homomorphic computation
    server_print("Running homomorphic computation on Lattica server...")
    serialized_ct_res = worker_api.apply_hom_pipeline(
        serialized_ct,
        block_index=1,
        return_new_state=True
    )
    timer.log_step(9.1, "Homomorphic computation")

    # Save encrypted result
    encrypted_result_path = f"{encrypted_dir}/results.bin"
    with open(encrypted_result_path, "wb") as f:
        f.write(serialized_ct_res)

    server_print(f"Encrypted results saved to {encrypted_result_path}")


if __name__ == "__main__":
    main()
