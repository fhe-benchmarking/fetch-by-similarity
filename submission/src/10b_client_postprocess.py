#!/usr/bin/env python3
"""
client_postprocess.py - Post-process decrypted results - convert payload back from float64 to int16.
"""
import sys
import os
import numpy as np

from harness.params import PAYLOAD_DIM
from lib.server_logger import server_print
from lib.server_timer import ServerTimer


def main():
    # Initialize timer for logging
    timer = ServerTimer()

    # Parse arguments
    size = int(sys.argv[1])
    count_only = len(sys.argv) > 2 and sys.argv[2] == "--count_only"
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    io_dir = f"io/{instance_name}"
    
    # Read raw results as float64 (the actual dtype saved by step 8)
    raw_results = np.fromfile(f"{io_dir}/raw-result.bin", dtype=np.float64)
    server_print(f"Loaded raw_results: shape: {raw_results.shape}, dtype: {raw_results.dtype}")
    server_print(f"First 10 row results: {raw_results[:10] if len(raw_results) >= 10 else raw_results}...")

    if count_only:
        # Extract count and save as np.int_ (system-dependent integer size)
        count = int(raw_results[0])
        payloads = np.array([count], dtype=np.int_)
    else:
        # Extract payload vectors, convert to int16, sort lexicographically, and save
        # Shape: (n_matches, PAYLOAD_DIM)
        n_matches = len(raw_results) // PAYLOAD_DIM

        if n_matches == 0:
            server_print(f"Zero matches found")
            payloads = np.array([], dtype=np.int16).reshape(0,
                                                            PAYLOAD_DIM)
        else:
            server_print(f"Reshape to {PAYLOAD_DIM} columns")
            payloads_float = raw_results[:n_matches * PAYLOAD_DIM].reshape(
                n_matches, PAYLOAD_DIM)
            server_print(f"First 3 float64 payloads:\n{payloads_float[:3]}...")

            # Check for invalid values before conversion
            if not np.all(np.isfinite(payloads_float)):
                bad_vals = payloads_float[~np.isfinite(payloads_float)]
                raise ValueError(
                    f"Invalid float values in raw results: {bad_vals[:5]}...")
            server_print("Convert to int16")
            payloads = np.round(payloads_float).astype(np.int16)
            server_print(f"First 5 int16 rows:\n{payloads[:5]}...")

            server_print("Sort lexicographically (sort by columns from right to left)")
            payloads = payloads[np.lexsort(payloads.T[::-1])]

            server_print(f"result shape: {payloads.shape}")
            server_print(f"Sorted int16 payloads first 5 elements: \n{payloads[:5]}...")

    payloads.tofile(f"{io_dir}/results.bin")

    # Log completion of postprocessing
    timer.log_step(10.2, "Postprocessing")

if __name__ == "__main__":
    main()
