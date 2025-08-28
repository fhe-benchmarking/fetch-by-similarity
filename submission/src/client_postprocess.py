"""
Dummy output for the workload
"""

import argparse
from pathlib import Path

def instance_name(size):
    """Return the string name of the instance size."""
    if size > 3:
        return "unknown"
    names = ["toy", "small", "medium", "large"]
    return names[size]

def main():
    parser = argparse.ArgumentParser(description='Create a results file.')
    parser.add_argument('size', type=int, help='Instance size (0-3)')
    args = parser.parse_args()
    size = args.size

    result = Path("io") / instance_name(size) / "results.bin"
    result.touch()

if __name__ == "__main__":
    main()
