#!/usr/bin/env bash
set -eux

# Installeer Cairo en afhankelijkheden
apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libffi-dev \
    python3-cffi

# Installeer Python-pakketten
pip install --no-cache-dir cairocffi pycairo