#!/usr/bin/env bash
set -eux

pip install --upgrade pip
pip install --no-cache-dir cairocffi pycairo Pillow imageio flask gunicorn
