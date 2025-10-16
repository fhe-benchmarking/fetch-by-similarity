#!/usr/bin/env python3
"""
client_key_generation.py - Generate and save FHE keys
"""
import sys
import os
import base64
import json

from lattica_query.lattica_query_client import QueryClient
from lattica_query.auth import get_demo_token
from lib.constants import MODEL_ID
from lib.server_logger import server_print

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
    # Get demo token using shared model ID constant
    token = get_demo_token(MODEL_ID)
    
    # Initialize QueryClient
    if os.getenv('LATTICA_RUN_MODE') == 'LOCAL':
        from lattica_query.dev_utils.lattica_query_client_local import \
            LocalQueryClient
        client = LocalQueryClient(token)
    else:
        client = QueryClient(token)
    
    # Generate keys (this also uploads the evaluation key automatically)
    context, secret_key, homseq = client.generate_key()
    
    # Save homseq for use in later steps
    homseq_path = f"{key_dir}/homseq.bin"
    with open(homseq_path, "wb") as f:
        f.write(homseq)
    
    # Save secret key for later use in decryption (following Lattica client standard format)
    sk_data = [
        base64.b64encode(secret_key[0]).decode('utf-8'),
        base64.b64encode(secret_key[1]).decode('utf-8'),
    ]
    
    sk_path = f"{key_dir}/sk.json"
    with open(sk_path, "w") as f:
        json.dump(sk_data, f)
    
    # Save context for later use
    context_path = f"{key_dir}/context.bin"
    with open(context_path, "wb") as f:
        f.write(context)
    
    # Save token for use in later steps (step 5 and step 9)
    server_dir = f"io/{instance_name}/server"
    os.makedirs(server_dir, exist_ok=True)
    token_path = f"{server_dir}/token.txt"
    with open(token_path, "w") as f:
        f.write(token)
    
    server_print(f"Keys generated and saved to {key_dir}/")
    server_print(f"Token saved to {token_path}")
    
if __name__ == "__main__":
    main()
