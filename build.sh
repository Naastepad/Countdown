#!/usr/bin/env bash
set -eux

# Installeer Cairo en Pango
apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libffi-dev \
    python3-cffi \
    python3-gi \
    gir1.2-pango-1.0 \
    gir1.2-gtk-3.0

# Installeer Python dependencies
pip install --no-cache-dir cairocffi pycairo pygobject