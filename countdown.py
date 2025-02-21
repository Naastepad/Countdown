import os
import datetime
import time
import io
import imageio
from flask import Flask, Response, request
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import unquote

app = Flask(__name__)

def parse_end_time(end_string):
    """ Converteert een datum-string naar een UNIX-timestamp en verwerkt URL-encoding """
    try:
        end_string = unquote(end_string).replace("+", " ")  # Spaties verwerken
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())  # Zet om naar UNIX timestamp
    except ValueError:
        return None  # Ongeldige invoer

def generate_countdown_image(remaining_time):
    """ Genereert een countdown afbeelding met maçonnieke symboliek en dynamische labels """
    remaining_time = max(0, remaining_time)  # Zorg dat er geen negatieve tijd is

    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # 🔹 Aanpassen van labels als waarden 0 bereiken
    day_label = "🌙 DAGEN" if days > 0 else "⚠️ DAGEN"
    hour_label = "⭐️ UREN" if hours > 0 else "⌛️ UREN"
    minute_label = "✨ MINUTEN" if minutes > 0 else "⌛️ MINUTEN"
    second_label = "☀️ SECONDEN"

    # 🔹 Afmetingen verbeteren voor een strakkere weergave
    width, height = 600, 250
    img = Image.new('RGB', (width, height), color=(0, 87, 183))  # Blauw
    draw = ImageDraw.Draw(img)

    # 🔹 Betere lettergroottes voor betere leesbaarheid
    try:
    font_large = ImageFont.truetype("NotoSansSymbols-Regular.ttf", 60)
    font_small = ImageFont.truetype("NotoSansSymbols-Regular.ttf", 22)
except IOError:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # 🔹 Bovenste regel met tijdseenheid labels
    labels = [day_label, hour_label, minute_label, second_label]
    label_positions = [width // 8, 3 * width // 8, 5 * width // 8, 7 * width // 8]

    for i in range(4):
        draw.text((label_positions[i] - 40, 20), labels[i], font=font_small, fill=(255, 255, 255))

    # 🔹 Countdown waarden en maçonnieke scheidingstekens
    values = [f"{days:02}", f"{hours:02}", f"{minutes:02}", f"{seconds:02}"]
    symbols = ["🪨", "∴", "◻️"]

    time_text = f"{values[0]} {symbols[0]} {values[1]} {symbols[1]} {values[2]} {symbols[2]} {values[3]}"
    draw.text((width // 4, 100), time_text, font=font_large, fill=(255, 255, 255))

    # 🔹 Onderste regel met instructie
    if remaining_time > 0:
        instruction_text = "Aanmelden O∴ L∴ van [?end= datum en tijd]"
    else:
        instruction_text = "🔒 Tempus Fugit | aanmelden niet mogelijk"

    draw.text((width // 6, 190), instruction_text, font=font_small, fill=(255, 255, 255))

    return img

@app.route('/countdown.png')
def countdown_png():
    """ API endpoint om een statische countdown afbeelding te genereren """
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_timestamp = parse_end_time(end_string)

    if end_timestamp is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_timestamp - now)

    img = generate_countdown_image(remaining_time)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')

def generate_countdown_gif(end_time):
    """ Genereert een GIF van 30 seconden met 1 seconde per frame en oneindige loop """
    frames = []
    duration_per_frame = 1000  # 🔹 1000ms = 1 seconde per frame

    for i in range(30):  # 30 frames (30 seconden)
        remaining_time = max(0, end_time - int(time.time()) - i)  # 🔹 Tel per seconde af
        frame = generate_countdown_image(remaining_time)

        # Opslaan in geheugen
        img_io = io.BytesIO()
        frame.save(img_io, format="PNG")
        img_io.seek(0)

        frames.append(imageio.imread(img_io))

    # 🔹 GIF genereren met correcte snelheid en oneindige loop
    gif_io = io.BytesIO()
    imageio.mimsave(gif_io, frames, format="GIF", duration=duration_per_frame / 1000, loop=0)  # 🔹 1 sec per frame & oneindige looping
    gif_io.seek(0)

    return gif_io

@app.route('/countdown.gif')
def countdown_gif():
    """ API endpoint om een countdown GIF te genereren """
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_timestamp = parse_end_time(end_string)

    if end_timestamp is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    gif_io = generate_countdown_gif(end_timestamp)
    return Response(gif_io, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
