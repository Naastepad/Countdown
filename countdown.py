import os
import logging

logging.basicConfig(level=logging.INFO)

def generate_countdown_image(remaining_time):
    """ Genereert een countdown afbeelding met verbeterde breedte en layout """
    
    font_path = "fonts/NotoColorEmoji.ttf"
    
    # Controleer of het bestand bestaat
    if not os.path.exists(font_path):
        logging.error(f"Fontbestand niet gevonden: {font_path}")
    else:
        logging.info(f"Fontbestand gevonden: {font_path}")

    # Probeer het lettertype te laden
    try:
        font_large = ImageFont.truetype(font_path, 28)
        font_small = ImageFont.truetype(font_path, 12)
        logging.info("Lettertype correct geladen!")
    except IOError:
        logging.error("Kon het lettertype niet laden, standaard lettertype wordt gebruikt.")
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Verder met de bestaande functie...
import datetime
import time
import io
import imageio
from flask import Flask, Response, request
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import unquote

app = Flask(__name__)

# Pad naar het lettertypebestand
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoColorEmoji.ttf')

def parse_end_time(end_string):
    """ Converteert een datum-string naar een UNIX-timestamp en verwerkt URL-encoding """
    try:
        end_string = unquote(end_string).replace("+", " ")  # Spaties verwerken
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp()), dt.strftime("%d-%m-%Y %H:%M:%S")  # UNIX timestamp en geformatteerde datum
    except ValueError:
        return None, None  # Ongeldige invoer

def generate_countdown_image(remaining_time, end_string):
    """ Genereert een countdown afbeelding met verbeterde layout en maçonnieke symbolen """
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # Dynamische aanpassing van symbolen bij aftellen
    day_label = "🌙 DAGEN" if days > 0 else "⚠️ DAGEN"
    hour_label = "⭐️ UREN" if hours > 0 else "⌛️ UREN"
    minute_label = "✨ MINUTEN" if minutes > 0 else "⌛️ MINUTEN"
    second_label = "☀️ SECONDEN" if seconds > 0 else "⌛️ SECONDEN"

    # Afbeeldingsgrootte en kleuren
    width, height = 600, 220
    img = Image.new('RGB', (width, height), color=(0, 87, 183))  # Blauw
    draw = ImageDraw.Draw(img)

    # Lettertypes instellen
    try:
        font_large = ImageFont.truetype(FONT_PATH, 40)
        font_small = ImageFont.truetype(FONT_PATH, 18)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Labels boven de cijfers
    labels = [day_label, hour_label, minute_label, second_label]
    values = [f"{days:02} 🪨", f"{hours:02} ∴", f"{minutes:02} ◻️", f"{seconds:02}"]

    block_width = width // 4
    for i in range(4):
        x_pos = i * block_width + (block_width // 2) - 30  # Centraal uitlijnen

        # Teken de labels bovenaan
        draw.text((x_pos, 10), labels[i], font=font_small, fill=(255, 255, 255))

        # Teken de waarden
        draw.text((x_pos, 70), values[i], font=font_large, fill=(255, 255, 255))

    # Onderste regel met aanmeldtekst
    register_text = f"Aanmelden voor de O∴ L∴ is mogelijk tot {end_string}"
    draw.text((width // 2 - 140, 180), register_text, font=font_small, fill=(255, 255, 255))

    return img

@app.route('/countdown.png')
def countdown_png():
    """ API endpoint om een statische countdown afbeelding te genereren """

    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_timestamp, formatted_end = parse_end_time(end_string)

    if end_timestamp is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_timestamp - now)

    img = generate_countdown_image(remaining_time, formatted_end)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')

def generate_countdown_gif(end_time, formatted_end):
    """ Genereert een GIF van 30 seconden met exact 1 seconde per frame en oneindige looping """
    frames = []
    duration_per_frame = 1000  # 1 seconde per frame

    for i in range(30):  # 30 frames (30 seconden)
        remaining_time = max(0, end_time - int(time.time()) - i)  # Tel per seconde af
        frame = generate_countdown_image(remaining_time, formatted_end)

        # Opslaan in geheugen
        img_io = io.BytesIO()
        frame.save(img_io, format="PNG")
        img_io.seek(0)

        frames.append(imageio.imread(img_io))

    # GIF genereren met oneindige looping
    gif_io = io.BytesIO()
    imageio.mimsave(gif_io, frames, format="GIF", duration=duration_per_frame, loop=0)  # Loop = 0 maakt het oneindig
    gif_io.seek(0)

    return gif_io

@app.route('/countdown.gif')
def countdown_gif():
    """ API endpoint om een countdown GIF te genereren """

    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_timestamp, formatted_end = parse_end_time(end_string)

    if end_timestamp is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    gif_io = generate_countdown_gif(end_timestamp, formatted_end)
    return Response(gif_io, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
