#!/usr/bin/env bash
set -eux

# Installeer Cairo en FreeType voor HarfBuzz
apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libharfbuzz-dev \
    libfreetype6-dev \
    libffi-dev \
    python3-cffi

# Installeer Python packages
pip install --no-cache-dir cairocffi pycairo harfbuzz freetype-py Pillow