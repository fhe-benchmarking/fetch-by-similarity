#!/usr/bin/env python3

# Copyright (c) 2025 HomomorphicEncryption.org
# All rights reserved.
#
# This software is licensed under the terms of the Apache v2 License.
# See the LICENSE.md file for details.

"""
utils.py - Scaffolding code for running the submission.
"""

import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Global variable to track the last timestamp
_last_timestamp: datetime = None
# Global variable to store measured times
_timestamps = {}
_timestampsStr = {}
# Global variable to store measured sizes
_bandwidth = {}

def ensure_directories(rootdir: Path):
    """ Check that the current directory has the rquired sub-directories
    """
    required_dirs = ['harness', 'scripts', 'submission']
    for dir_name in required_dirs:
        if not (rootdir / dir_name).exists():
            print(f"Error: Required directory '{dir_name}'",
                  f"not found in {rootdir}")
            sys.exit(1)


def log_step(step_num: int, step_name: str, start: bool = False):
    """ 
    Helper function to print timestamp after each step with second precision 
    """
    global _last_timestamp
    global _timestamps
    global _timestampsStr
    now = datetime.now()
    # Format with milliseconds precision
    timestamp = now.strftime("%H:%M:%S")

    # Calculate elapsed time if this isn't the first call
    elapsed_str = ""
    elapsed_seconds = 0
    if _last_timestamp is not None:
        elapsed_seconds = (now - _last_timestamp).total_seconds()
        elapsed_str = f" (elapsed: {round(elapsed_seconds, 4)}s)"

    # Update the last timestamp for the next call
    _last_timestamp = now

    if not start:
        print(f"{timestamp} [harness] {step_num}: {step_name} completed{elapsed_str}")
        _timestampsStr[step_name] = f"{round(elapsed_seconds, 4)}s"
        _timestamps[step_name] = elapsed_seconds

def log_size(path: Path, object_name: str, flag: bool = False, previous: int = 0):
    """Measure the size of a directory or file on disk
    """
    global _bandwidth

    if not path.exists():
        size = 0
    else:
        size = int(subprocess.run(["du", "-sb", path], check=True,
                           capture_output=True, text=True).stdout.split()[0])
        if flag:
            size -= previous

    print("         [harness]", object_name, "size:", human_readable_size(size))

    _bandwidth[object_name] = human_readable_size(size)
    return size

def human_readable_size(n: int):
    """Pretty print for size in bytes"""
    for unit in ["B","K","M","G","T"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}P"

def save_run(path: Path):
    """Save the timing from the current run to disk"""
    global _timestamps
    global _timestampsStr
    global _bandwidth

    json.dump({
        "total_latency_s": round(sum(_timestamps.values()), 4),
        "per_stage": _timestampsStr,
        "bandwidth": _bandwidth,
    }, open(path,"w"), indent=2)

    print("[total latency]", f"{round(sum(_timestamps.values()), 4)}s")
