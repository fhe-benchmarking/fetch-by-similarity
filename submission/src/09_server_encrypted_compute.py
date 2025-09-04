#!/usr/bin/env python3
"""
server_encrypted_compute.py - Perform homomorphic similarity search
"""
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from server_timer import ServerTimer
# from lattica_client import LatticaClient

def main():
    # Parse arguments
    size = int(sys.argv[1])
    count_only = len(sys.argv) > 2 and sys.argv[2] == "--count_only"
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    encrypted_dir = f"io/{instance_name}/encrypted"
    
    # Initialize timer for logging
    timer = ServerTimer()
    
    # Step 0: Loading keys
    timer.log_step(0, "Loading keys")
    # TODO: Load keys from io/<size>/keys/
    
    # TODO: Load encrypted query
    # with open(f"{encrypted_dir}/query.bin", "rb") as f:
    #     encrypted_query = f.read()
    
    # Step 1: Matrix-vector product
    # TODO: Perform homomorphic computation
    # results = worker_api.compute_similarity(encrypted_query)
    timer.log_step(1, "Matrix-vector product")
    
    # Step 2: Compare to threshold
    # TODO: Compare similarities to 0.8 threshold
    timer.log_step(2, "Compare to threshold")
    
    # Step 3: Running sums
    # TODO: Compute running sums if needed
    timer.log_step(3, "Running sums")
    
    # Step 4: Output compression
    # TODO: Compress and save results
    # with open(f"{encrypted_dir}/results.bin", "wb") as f:
    #     f.write(compressed_results)
    timer.log_step(4, "Output compression")
    
    # Create placeholder for now (remove in real implementation)
    open(f"{encrypted_dir}/results.bin", 'wb').close()
    
if __name__ == "__main__":
    main()
