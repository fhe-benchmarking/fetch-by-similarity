#!/usr/bin/env python3
"""
run_submission.py - run the entire submission process, from build to verify
"""
# Copyright (c) 2025, Amazon Web Services
# All rights reserved.
#
# This software is licensed under the terms of the Apache v2 License.
# See the LICENSE.md file for details.
import sys
import argparse
import subprocess
import numpy as np
import utils
from params import InstanceParams, TOY, LARGE, instance_name

def main():
    """
    Run the entire submission process, from build to verify
    """
    # Parse arguments using argparse
    parser = argparse.ArgumentParser(description='Run the fetch-by-similarity FHE benchmark.')
    parser.add_argument('size', type=int, choices=range(TOY, LARGE+1),
                        help='Instance size (0-toy/1-small/2-medium/3-large)')
    parser.add_argument('--num_runs', type=int, default=1,
                        help='Number of times to run steps 4-9 (default: 1)')
    parser.add_argument('--seed', type=int,
                        help='Random seed for dataset and query generation')
    parser.add_argument('--count_only', action='store_true',
                        help='Only count # of matches, do not return payloads')
    parser.add_argument('--remote', action='store_true',
                        help='Run example submission in remote backend mode')

    args = parser.parse_args()
    size = args.size
    remote_be = args.remote

    # Use params.py to get instance parameters
    params = InstanceParams(size)


    # Ensure the required directories exist
    utils.ensure_directories(params.rootdir)

    # Verify dependencies and build the submission, if not built already
    utils.build_submission(params.rootdir/"scripts", remote_be)

    # The harness scripts are in the 'harness' directory,
    # the submission code is either in submission or submission_remote
    harness_dir = params.rootdir/"harness"
    exec_dir = params.rootdir/ ("submission_remote/src" if remote_be else "submission")

    print(f"\n[harness] Running submission for {instance_name(size)} dataset")
    if args.count_only:
        print("          only counting matches")
    else:
        print("          returning matching payloads")

    # 0. Generate the dataset (and centers) using harness/generate_dataset.py

    # Remove and re-create IO directory
    io_dir = params.iodir()
    if io_dir.exists():
        subprocess.run(["rm", "-rf", str(io_dir)], check=True)
    io_dir.mkdir(parents=True)

    if args.seed is not None:
        np.random.seed(args.seed)
        rng = np.random.default_rng(args.seed)
    utils.log_step(0, "Init", True)

    # Common command-line arguments for all steps
    cmd_args = [str(size), ]
    if args.seed is not None:  # Use seed if provided
        gendata_seed = rng.integers(0,0x7fffffff)
        cmd_args.extend(["--seed", str(gendata_seed)])
    if args.count_only:
        cmd_args.extend(["--count_only"])

    # 1. Client-side: Generate the datasets
    utils.run_exe_or_python(harness_dir, "generate_dataset", *cmd_args)
    utils.log_step(1, "Dataset generation")

    # 1.1 Communication: Get cryptographic context
    if remote_be:
        utils.run_exe_or_python(exec_dir, "server_get_params", str(size))
        utils.log_step(1.1 , "Communication: Get cryptographic context")

    # 2. Client-side: Preprocess the dataset using exec_dir/client_preprocess_dataset
    utils.run_exe_or_python(exec_dir, "client_preprocess_dataset", *cmd_args)
    utils.log_step(2, "Dataset preprocessing")

    # 3. Client-side: Generate the cryptographic keys
    # Note: this does not use the rng seed above, it lets the implementation
    #   handle its own prg needs. It means that even if called with the same
    #   seed multiple times, the keys and ciphertexts will still be different.
    utils.run_exe_or_python(exec_dir, "client_key_generation", *cmd_args)
    utils.log_step(3, "Key Generation")


    # 3.1 Communication: Upload evaluation key
    if remote_be:
        utils.run_exe_or_python(exec_dir, "server_upload_ek", str(size))
        utils.log_step(3.1 , "Communication: Upload evaluation key")

    # 4. Client-side: Encode and encrypt the dataset
    utils.run_exe_or_python(exec_dir, "client_encode_encrypt_db", *cmd_args)
    utils.log_step(4, "Dataset encoding and encryption")

    # 4.1 Communication: Upload encrypted database
    if remote_be:
        utils.run_exe_or_python(exec_dir, "server_upload_db", str(size))
        utils.log_step(4.1 , "Communication: Upload encrypted database")

    # Report size of keys and encrypted data
    utils.log_size(io_dir / "keys", "Public and evaluation keys")
    utils.log_size(io_dir / "encrypted", "Encrypted database")

    # 5. Server-side: Preprocess the encrypted dataset using exec_dir/server_preprocess_dataset
    utils.run_exe_or_python(exec_dir, "server_preprocess_dataset", *cmd_args)
    utils.log_step(5, "Encrypted dataset preprocessing")

    # Run steps 6-11 multiple times if requested
    for run in range(args.num_runs):
        if args.num_runs > 1:
            print(f"\n         [harness] Run {run+1} of {args.num_runs}")

        # 6. Client-side: Generate a new random query using harness/generate_query.py
        utils.run_exe_or_python(harness_dir, "generate_query", *cmd_args)
        utils.log_step(6, "Query generation")

        # 7. Client-side: preprocess query
        utils.run_exe_or_python(exec_dir, "client_preprocess_query", *cmd_args)
        utils.log_step(7, "Query preprocessing")

        # 8. Client-side: Encrypt the query
        utils.run_exe_or_python(exec_dir, "client_encode_encrypt_query", *cmd_args)
        utils.log_step(8, "Query encryption")
        utils.log_size(io_dir / "encrypted" / "query.bin" , "Encrypted query")

        # 9. Server-side: run exec_dir/server_encrypted_compute
        utils.run_exe_or_python(exec_dir, "server_encrypted_compute", *cmd_args)
        utils.log_step(9, "Encrypted computation")


        # 10. Client-side: decrypt and postprocess
        utils.run_exe_or_python(exec_dir, "client_decrypt_decode", *cmd_args)
        utils.run_exe_or_python(exec_dir, "client_postprocess", *cmd_args)
        utils.log_step(10, "Result decryption and postprocessing")

        # remove seed arg
        cmd_args = [x for i, x in enumerate(cmd_args)
                if not (x == "--seed" or (i > 0 and cmd_args[i - 1] == "--seed"))]

        # 11. Run the plaintext processing in cleartext_impl.py and verify_results
        utils.run_exe_or_python(harness_dir, "cleartext_impl", *cmd_args)

        # 12. Verify results
        expected_file = params.datadir() / "expected.bin"
        result_file = io_dir / "results.bin"

        if not result_file.exists():
            print(f"Error: Result file {result_file} not found")
            sys.exit(1)

        utils.run_exe_or_python(harness_dir, "verify_result", str(expected_file), str(result_file), *cmd_args[1:])  # skip size arg

        # 13. Store measurements
        run_path = params.measuredir() / f"results-{run+1}.json"
        run_path.parent.mkdir(parents=True, exist_ok=True)
        submission_report_path = io_dir / "server_reported_steps.json"
        utils.save_run(run_path, submission_report_path)

    print(f"\nAll steps completed for the {instance_name(size)} dataset!")

if __name__ == "__main__":
    main()
