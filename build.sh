#!/usr/bin/env bash
set -eux

# Update package list en installeer Cairo en afhankelijkheden
apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libffi-dev \
    python3-cffi

# Installeer Cairo via pip
pip install cairocffi
