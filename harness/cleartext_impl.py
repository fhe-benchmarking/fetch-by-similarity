"""
Dummy cleartext result
"""
import argparse
from params import InstanceParams

def main():
    # Parse arguments using argparse
    parser = argparse.ArgumentParser(description='Create a results file.')
    parser.add_argument('size', type=int, help='Instance size (0-3)')
    args = parser.parse_args()    
    size = args.size

    # Use params.py to get instance parameters
    expected = InstanceParams(size).datadir() / "expected.bin"
    expected.touch()

if __name__ == "__main__":
    main()
