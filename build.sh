#!/bin/bash
set -e

# Use break-system-packages to override uv's protection
pip install --upgrade pip
pip install --break-system-packages -r requirements.txt

echo "Build completed successfully"
