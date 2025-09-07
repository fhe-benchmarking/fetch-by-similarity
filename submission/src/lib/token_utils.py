#!/usr/bin/env python3
"""
token_utils.py - JWT token utilities
"""
import json
import base64


def extract_token_id(token: str) -> str:
    """
    Extract tokenId from JWT token payload.
    """
    header_b64, payload_b64, signature_b64 = token.split('.')
    return json.loads(base64.urlsafe_b64decode(payload_b64 + '=='))['tokenId']