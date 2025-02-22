#!/usr/bin/env bash
set -eux

# Maak de fonts-map als die nog niet bestaat
mkdir -p /usr/share/fonts/truetype/noto

# Download NotoColorEmoji als het niet bestaat
if [ ! -f /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf ]; then
    wget -O /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf https://github.com/google/fonts/raw/main/ofl/notocoloremoji/NotoColorEmoji.ttf
    fc-cache -f -v  # Forceer herladen van font-cache
fi

# Installeer Cairo via pip (apt-get werkt niet op Render.com)
pip install --no-cache-dir cairocffi pycairo