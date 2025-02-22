#!/usr/bin/env bash
set -eux

# Installeer alleen de essentiële dependencies
apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libffi-dev \
    python3-cffi

# Installeer Python packages
pip install --no-cache-dir cairocffi pycairo