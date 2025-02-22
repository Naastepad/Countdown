import os
import datetime
import time
import io
import imageio
import flask
from flask import Flask, Response, request
from urllib.parse import unquote
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Zorg ervoor dat je NotoColorEmoji.ttf in de fonts-map hebt staan
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "NotoColorEmoji.ttf")

def parse_end_time(end_string):
    """ Converteert een datum-string naar een UNIX-timestamp """
    try:
        end_string = unquote(end_string).replace("+", " ")
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
    except ValueError:
        return None

def generate_countdown_image(remaining_time):
    """ Genereert een countdown afbeelding met Pillow en HarfBuzz voor emoji's """
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # Afbeeldingsgrootte
    width, height = 600, 200
    img = Image.new("RGB", (width, height), color=(0, 87, 183))
    draw = ImageDraw.Draw(img)

    # Laad emoji compatibel lettertype
    if os.path.exists(FONT_PATH):
        font_large = ImageFont.truetype(FONT_PATH, 48)
        font_small = ImageFont.truetype(FONT_PATH, 24)
    else:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Labels met emoji’s
    labels = ["🌙 DAGEN", "⭐ UREN", "✨ MINUTEN", "☀️ SECONDEN"]
    values = [
        f"{days:02d} 🪨",
        f"{hours:02d} ∴",
        f"{minutes:02d} ◻️",
        f"{seconds:02d}"
    ]

    # Teken labels
    for i, label in enumerate(labels):
        draw.text((40 + i * 140, 40), label, font=font_small, fill="white")

    # Teken waarden
    for i, value in enumerate(values):
        draw.text((40 + i * 140, 100), value, font=font_large, fill="white")

    # Teken ondertekst
    draw.text((50, 180), "Aanmelden voor de O∴ L∴ is mogelijk tot", font=font_small, fill="white")
    draw.text((320, 180), datetime.datetime.fromtimestamp(end_time).strftime("%d-%m-%Y %H:%M:%S"), font=font_small, fill="white")

    # Opslaan als PNG
    img_io = io.BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return img_io

@app.route('/countdown.png')
def countdown_png():
    """ API endpoint om een countdown afbeelding te genereren """
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    global end_time
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_time - now)

    img_io = generate_countdown_image(remaining_time)
    return Response(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))