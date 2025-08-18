#!/usr/bin/env python3
"""
params.py - Parameters and directory structure for similarity search.
"""
# Copyright (c) 2025, Amazon Web Services
# All rights reserved.
#
# This software is licensed under the terms of the Apache v2 License.
# See the LICENSE.md file for details.
from pathlib import Path

# Enum for benchmark size
TOY = 0
SMALL = 1
MEDIUM = 2
LARGE = 3

def instance_name(size):
    """Return the string name of the instance size."""
    if size > LARGE:
        return "unknown"
    names = ["toy", "small", "medium", "large"]
    return names[size]

# The payloads are vectors of 7 int16 numbers in the range [0,4095)
PAYLOAD_DIM = 7

class InstanceParams:
    """Parameters that differ for different instance sizes."""

    def __init__(self, size, rootdir=None):
        """Constructor."""
        self.size = size
        self.rootdir = Path(rootdir) if rootdir else Path.cwd()

        if size > LARGE:
            raise ValueError("Invalid instance size")

        # parameters for sizes:   toy  small   medium     large
        rec_dims =              [ 128,   128,     256,      512]
        db_sizes =              [1000, 50000, 1000000, 20000000]

        self.record_dim = rec_dims[size]
        self.db_size = db_sizes[size]

    def get_size(self):
        """Return the instance size."""
        return self.size

    def get_record_dim(self):
        """Return the dimension of the plaintext record."""
        return self.record_dim

    def get_db_size(self):
        """Return the number of records in the dataset."""
        return self.db_size

    # Directory structure methods
    def subdir(self):
        """Return the submission directory of this repository."""
        return self.rootdir

    def datadir(self):
        """Return the dataset directory path."""
        return self.rootdir / "datasets" / instance_name(self.size)

    def iodir(self):
        """Return the I/O directory path."""
        return self.rootdir / "io" / instance_name(self.size)

    def measuredir(self):
        """Return the measurements directory path."""
        return self.rootdir / "measurements" / instance_name(self.size)
