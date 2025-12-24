#!/usr/bin/env python3
"""
client_postprocess.py - Post-process decrypted results - convert payload back from float64 to int16.
"""
import sys
import os
import numpy as np
import torch

from harness.params import PAYLOAD_DIM

from lib.server_logger import server_print
from lib.server_timer import ServerTimer
from lib.constants import PRECISION


def _post_process(raw_result, n_cols, payload_dim):
    def _sort_results(a):
        # Sort by the second column (index 1)
        a = a[a[:, 1].argsort()]
        return a

    def _extract_final_results(a):
        a = a.reshape(-1, payload_dim, n_cols).moveaxis(-1, -2).reshape(-1, payload_dim)
        # Create a mask for rows that have any nonzero element
        MAX_VAL = 256
        valid_rows_mask = a[:, 0] > MAX_VAL * 1.4  # the marker row is expected to be 2 * MAX_VAL
        a = a[valid_rows_mask]
        scale = 2 * MAX_VAL * PRECISION / a[:, 0]  # scale each row by the expected marker value
        a = (a * scale[:, None]).round().to(torch.int64)
        return a

    raw_result = _extract_final_results(raw_result)
    raw_result = _sort_results(raw_result)

    return raw_result


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
    raw_results = torch.from_numpy(np.fromfile(f"{io_dir}/raw-result.bin", dtype=np.float64))
    server_print(f"Loaded raw_results: shape: {raw_results.shape}, dtype: {raw_results.dtype}")

    # Post-processing
    n_cols = 8 if instance_name == 'toy' else 512  # n_cols = n_slots / 64
    results = _post_process(raw_results, n_cols, PAYLOAD_DIM + 1)
    server_print(f"results shape: {results.shape}")

    # Remove marker from results
    results_np = results[:, 1:].to(torch.int16).numpy()

    # Check if apply_clear is enabled via environment variable
    apply_clear_enabled = os.getenv('LATTICA_APPLY_CLEAR', '').lower() == 'true'
    if apply_clear_enabled:
        # Read results from clear computation
        clear_results_raw = torch.from_numpy(np.fromfile(f"{io_dir}/clear-result.bin", dtype=np.float64))
        server_print(f"Loaded clear_results: shape: {clear_results_raw.shape}, dtype: {clear_results_raw.dtype}")

        # Post-processing
        clear_results = _post_process(clear_results_raw, n_cols, PAYLOAD_DIM + 1)
        server_print(f"clear_results shape: {clear_results.shape}")

        # Check that number of elements match after post-processing
        if results.shape != clear_results.shape:
            raise ValueError(
                f"Post-processing: Number of matches mismatch: {results.shape=}, {clear_results.shape=}"
            )

        assert torch.equal(results, clear_results), "Post-processing: Results from raw_result and clear_result do not match"

    if count_only:
        # Extract count and save as np.int_ (system-dependent integer size)
        results_np = np.array([results_np.shape[0]], dtype=np.int_)

    results_np.tofile(f"{io_dir}/results.bin")

    # Log completion of postprocessing
    timer.log_step(10.2, "Postprocessing")


if __name__ == "__main__":
    main()
