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

def _post_process(raw_result, clear_result_tensor):
    def _sort_results(a):
        # Sort by the second column (index 1)
        a = a[a[:, 1].argsort()]
        return a

    def _extract_final_results(a):
        a = a.reshape(-1, 8).moveaxis(0, -1).reshape(8, -1, 8).moveaxis(1, 0).reshape(-1, 8)
        # Create a mask for rows that have any nonzero element
        MAX_VAL = 256
        valid_rows_mask = a[:, 0] > MAX_VAL * 1.4  # the marker row is expected to be 2 * MAX_VAL
        a = a[valid_rows_mask]
        scale = 2 * MAX_VAL * PRECISION / a[:, 0]  # scale each row by the expected marker value
        a = (a * scale[:, None]).round().to(torch.int64)
        return a

    raw_result = _extract_final_results(raw_result)
    raw_result = _sort_results(raw_result)

    clear_result_tensor = _extract_final_results(clear_result_tensor)
    clear_result_tensor = _sort_results(clear_result_tensor)

    return raw_result, clear_result_tensor

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

    # Read results from clear computation
    clear_results = np.fromfile(f"{io_dir}/clear-result.bin", dtype=np.float64)

    if count_only:
        # Extract count and save as np.int_ (system-dependent integer size)
        count = int(raw_results[0])
        raw_results = np.array([count], dtype=np.int_)
    else:

        raw_results = torch.from_numpy(raw_results)
        clear_results = torch.from_numpy(clear_results)

        # Check that number of elements match
        if raw_results.numel() != clear_results.numel():
            raise ValueError(
                f"Number of elements mismatch: raw_result {raw_results.numel()} != clear_result {clear_results.numel()}"
            )
        server_print(
            "✓ Number of elements check passed: raw_result and clear_result have the same number of elements")

        # Post-processing
        raw_results, clear_results = _post_process(raw_results, clear_results)
        server_print(f"raw_results shape: {raw_results.shape}")
        server_print(f"clear_results shape: {clear_results.shape}")

        n_matches = raw_results.shape[0]

        if n_matches == 0:
            server_print(f"Zero matches found")
            raw_results = np.array([], dtype=np.int16).reshape(0, PAYLOAD_DIM)
            raw_results.tofile(f"{io_dir}/results.bin")
            return

        # Check that number of elements match after post-processing
        if raw_results.numel() != clear_results.numel():
            raise ValueError(
                f"Post-processing: Number of elements mismatch: raw_result {raw_results.numel()} != clear_result {clear_results.numel()}"
            )
        server_print(
            "✓ Post-processing: Number of elements check passed: raw_result and clear_result have the same number of elements")

        tolerance = 1 / 2 ** 10
        max_diff = torch.max(torch.abs(raw_results.round() - clear_results.round()))
        server_print(f"Maximum difference between raw and clear results: {max_diff}")

        torch.testing.assert_close(raw_results.round(),
                                   clear_results.round(),
                                   rtol=tolerance,
                                   atol=tolerance,
                                   msg=f"Content mismatch: exceeds tolerance {tolerance}")

        server_print(f"✓ Content check passed: raw_result and clear_result match within tolerance {tolerance}")

        # Remove marker from results
        raw_results = raw_results[:, 1:].to(torch.int16).numpy()

    raw_results.tofile(f"{io_dir}/results.bin")

    # Log completion of postprocessing
    timer.log_step(10.2, "Postprocessing")

if __name__ == "__main__":
    main()
