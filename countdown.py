import os
import datetime
import time
import io
import cairo
from flask import Flask, Response, request
from urllib.parse import unquote

app = Flask(__name__)

def parse_end_time(end_string):
    """ Converteert een datum-string naar een UNIX-timestamp """
    try:
        end_string = unquote(end_string).replace("+", " ")  # Spaties verwerken
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())  # Zet om naar UNIX timestamp
    except ValueError:
        return None  # Ongeldige invoer

def generate_countdown_image(remaining_time, end_string):
    """ Genereert een countdown afbeelding met Cairo + Kleur Emoji's """

    # Bereken tijd
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # 🔹 Afbeeldingsgrootte instellen
    width, height = 600, 250
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # 🔹 Achtergrondkleur (Blauw)
    ctx.set_source_rgb(0, 87, 183)  # RGB voor blauw
    ctx.rectangle(0, 0, width, height)
    ctx.fill()

    # 🔹 Emoji's en Labels
    labels = ["🌙 DAGEN", "⭐️ UREN", "✨ MINUTEN", "☀️ SECONDEN"]
    values = [f"{days:02}", f"{hours:02}", f"{minutes:02}", f"{seconds:02}"]
    symbols = ["🪨", "∴", "◻️", "⌛️"]

    # 🔹 Lettertype instellen (Noto Emoji)
    font_path = "fonts/NotoColorEmoji.ttf"
    if os.path.exists(font_path):
        ctx.select_font_face(font_path, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    else:
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    ctx.set_font_size(30)

    # 🔹 Labels tekenen
    ctx.set_source_rgb(1, 1, 1)  # Wit
    for i, label in enumerate(labels):
        ctx.move_to(50 + i * 150, 50)
        ctx.show_text(label)

    # 🔹 Cijfers + symbolen tekenen
    ctx.set_font_size(50)
    for i, value in enumerate(values):
        ctx.move_to(60 + i * 150, 120)
        ctx.show_text(value + " " + symbols[i])

    # 🔹 Aanmeldtekst
    ctx.set_font_size(20)
    ctx.move_to(50, 200)
    ctx.show_text(f"Aanmelden voor de O∴ L∴ is mogelijk tot {end_string}")

    # 🔹 Afbeelding opslaan in geheugen
    img_io = io.BytesIO()
    surface.write_to_png(img_io)
    img_io.seek(0)

    return img_io

@app.route('/countdown.png')
def countdown_png():
    """ API endpoint om een countdown PNG te genereren """

    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_timestamp = parse_end_time(end_string)

    if end_timestamp is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_timestamp - now)

    img_io = generate_countdown_image(remaining_time, end_string)
    return Response(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))