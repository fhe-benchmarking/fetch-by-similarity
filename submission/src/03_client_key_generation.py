#!/usr/bin/env python3
"""
client_key_generation.py - Generate and save FHE keys
"""
import sys
import os
import base64
import json

from lib.server_logger import server_print
from lib.utils import get_query_client


def main():
    # Parse arguments
    size = int(sys.argv[1])
    count_only = len(sys.argv) > 2 and sys.argv[2] == "--count_only"
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    key_dir = f"io/{instance_name}/keys"
    os.makedirs(key_dir, exist_ok=True)
    os.environ["LATTICA_EVK_PATHNAME"] = f"{key_dir}/evk.lpk"
    
    # Generate keys (this also uploads the evaluation key automatically)
    client = get_query_client()
    context, secret_key, _ = client.generate_key()
    
    # Save secret key for later use in decryption (following Lattica client standard format)
    sk_data = [
        base64.b64encode(secret_key[0]).decode('utf-8'),
        base64.b64encode(secret_key[1]).decode('utf-8')
    ]
    
    sk_path = f"{key_dir}/sk.json"
    with open(sk_path, "w") as f:
        json.dump(sk_data, f)
    
    # Save context for later use
    context_path = f"{key_dir}/context.bin"
    with open(context_path, "wb") as f:
        f.write(context)

    server_print(f"Keys generated and saved to {key_dir}/")


if __name__ == "__main__":
    main()
