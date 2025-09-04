#!/usr/bin/env bash
# ----------------------------------------------------------------------
# Usage: ./scripts/build_task.sh <task>/submission
# Copies Python scripts from src/ to build/ and makes them executable
# Strips numeric prefixes (e.g., 02_script.py -> script)

set -euo pipefail

ROOT="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd )"
TASK_DIR="$1"
BUILD="$TASK_DIR/build"

echo "Building Python submission..."

# Clean and recreate build directory
if [ -d "$BUILD" ]; then
    echo "  Cleaning existing build directory..."
    rm -rf "$BUILD"
fi
mkdir -p "$BUILD"

# List of all required executables
# Updated to include client_preprocess_query for the new framework
SCRIPTS=(
    "client_preprocess_dataset"
    "client_key_generation"
    "client_encode_encrypt_db"
    "server_preprocess_dataset"
    "client_preprocess_query"
    "client_encode_encrypt_query"
    "server_encrypted_compute"
    "client_decrypt_decode"
    "client_postprocess"
)

# Copy Python scripts from src/ to build/ and make them executable
# Now handles files with numeric prefixes (e.g., 02_script.py)
for script in "${SCRIPTS[@]}"; do
    # Look for files matching either pattern: script.py or XX_script.py
    src_file="$TASK_DIR/src/${script}.py"
    prefixed_file="$TASK_DIR/src/"*"_${script}.py"
    dest_file="$BUILD/${script}"
    
    # Check for prefixed version first
    if ls $prefixed_file 2>/dev/null | head -1 | grep -q .; then
        src_file=$(ls $prefixed_file 2>/dev/null | head -1)
        cp "$src_file" "$dest_file"
        chmod +x "$dest_file"
        echo "  ✓ Copied and made executable: $(basename "$src_file") -> $script"
    elif [ -f "$src_file" ]; then
        cp "$src_file" "$dest_file"
        chmod +x "$dest_file"
        echo "  ✓ Copied and made executable: $script"
    else
        echo "  ✗ Warning: Missing source file for: $script"
    fi
done

# Copy library files if they exist
if [ -d "$TASK_DIR/lib" ]; then
    cp -r "$TASK_DIR/lib" "$BUILD/"
    echo "  ✓ Copied library files to build/lib/"
fi

# Copy requirements.txt if it exists
if [ -f "$TASK_DIR/requirements.txt" ]; then
    cp "$TASK_DIR/requirements.txt" "$BUILD/"
    echo "  ✓ Copied requirements.txt"
fi

echo "Build complete!"
