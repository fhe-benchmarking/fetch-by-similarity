#!/usr/bin/env python3
"""
client_key_generation.py - Generate and save FHE keys
"""
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from lattica_query.lattica_query_client import QueryClient
from lattica_query.auth import get_demo_token

def main():
    # Parse arguments
    size = int(sys.argv[1])
    count_only = len(sys.argv) > 2 and sys.argv[2] == "--count_only"
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    key_dir = f"io/{instance_name}/keys"
    os.makedirs(key_dir, exist_ok=True)
    
    # Get demo token - using sketchToNumber temporarily until similarity model is deployed
    # TODO: Change to "similarity" once the model is deployed to Lattica cloud
    model_id = "4d15ae30-18e4-43e9-83d0-2d5ca4f7a0a2"  # Temporary - using existing model for key generation
    token = get_demo_token(model_id)
    
    # Initialize QueryClient
    client = QueryClient(token)
    
    # Generate keys (this also uploads the evaluation key automatically)
    context, secret_key, homseq = client.generate_key()
    
    # Save the evaluation key locally (it was already uploaded in generate_key())
    # The generate_key() method creates a temp file, uploads it, then deletes it
    # We need to regenerate it to save locally
    import lattica_query.query_toolkit as toolkit_interface
    _, evaluation_key = toolkit_interface.generate_key(homseq, context)
    
    # Save evaluation key
    pk_path = f"{key_dir}/pk.lpk"
    with open(pk_path, "wb") as f:
        f.write(evaluation_key)
    
    # Save secret key for later use in decryption (following Lattica client standard format)
    import base64
    import json
    
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
    
    print(f"Keys generated and saved to {key_dir}/")
    
if __name__ == "__main__":
    main()
