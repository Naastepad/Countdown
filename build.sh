#!/usr/bin/env bash
set -eux

# Installeer alleen de essentiële dependencies
pip install --no-cache-dir cairocffi pycairo Pillow imageio flask gunicorn