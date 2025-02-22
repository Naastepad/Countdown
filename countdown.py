import os

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/NotoColorEmoji.ttf")

if os.path.exists(FONT_PATH):
    print(f"✅ Emoji-lettertype gevonden: {FONT_PATH}")
else:
    print("❌ Emoji-lettertype NIET gevonden!")

import datetime
import time
import io
import cairo
from flask import Flask, Response, request
from urllib.parse import unquote

app = Flask(__name__)

# 🔹 Pad naar lettertype met emoji-ondersteuning
FONT_PATH = "fonts/NotoColorEmoji.ttf"

# 🔹 Canvas-grootte instellen
WIDTH, HEIGHT = 600, 200
BG_COLOR = (0, 0.34, 0.72)  # Blauw

# 🔹 Maçonnieke symbolen
EMOJIS = {
    "dagen": "🌙",
    "uren": "⭐️",
    "minuten": "✨",
    "seconden": "☀️",
    "sep1": "🪨",
    "sep2": "∴",
    "sep3": "◻️",
}

# 🔹 Functie om datumstring naar een UNIX timestamp te converteren
def parse_end_time(end_string):
    try:
        end_string = unquote(end_string).replace("+", " ")  
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
    except ValueError:
        return None  

# 🔹 Functie om countdown-afbeelding te genereren met Cairo
def generate_countdown_image(remaining_time):
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # Maak een nieuwe afbeelding
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Achtergrondkleur instellen
    ctx.set_source_rgb(*BG_COLOR)
    ctx.paint()

    # Laad het lettertype
    if os.path.exists(FONT_PATH):
        font_face = cairo.ToyFontFace(FONT_PATH, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    else:
        font_face = cairo.ToyFontFace("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    ctx.set_font_face(font_face)

    # 🔹 Labels boven de cijfers
    ctx.set_font_size(20)
    labels = [f"{EMOJIS['dagen']} DAGEN", f"{EMOJIS['uren']} UREN", f"{EMOJIS['minuten']} MINUTEN", f"{EMOJIS['seconden']} SECONDEN"]
    for i, label in enumerate(labels):
        x_pos = i * (WIDTH / 4) + 50
        ctx.move_to(x_pos, 30)
        ctx.set_source_rgb(1, 1, 1)  # Wit
        ctx.show_text(label)

    # 🔹 Countdown cijfers + scheidingstekens
    ctx.set_font_size(40)
    values = [
        f"{days:02} {EMOJIS['sep1']}", f"{hours:02} {EMOJIS['sep2']}", 
        f"{minutes:02} {EMOJIS['sep3']}", f"{seconds:02}"
    ]
    
    for i, value in enumerate(values):
        x_pos = i * (WIDTH / 4) + 50
        ctx.move_to(x_pos, 100)
        ctx.set_source_rgb(1, 1, 1)
        ctx.show_text(value)

    # 🔹 Instructie onderaan
    instruction_text = f"Aanmelden voor de O∴ L∴ is mogelijk tot {datetime.datetime.fromtimestamp(time.time() + remaining_time).strftime('%d-%m-%Y %H:%M:%S')}"
    ctx.set_font_size(14)
    ctx.move_to(WIDTH / 6, HEIGHT - 30)
    ctx.show_text(instruction_text)

    return surface

# 🔹 API endpoint voor PNG
@app.route('/countdown.png')
def countdown_png():
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_timestamp = parse_end_time(end_string)

    if end_timestamp is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_timestamp - now)

    surface = generate_countdown_image(remaining_time)
    
    img_io = io.BytesIO()
    surface.write_to_png(img_io)
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')

# 🔹 Functie voor GIF-generatie
def generate_countdown_gif(end_time):
    frames = []
    duration_per_frame = 1000  # 🔹 Precies 1 seconde per frame

    for i in range(30):
        remaining_time = max(0, end_time - int(time.time()) - i)
        surface = generate_countdown_image(remaining_time)

        img_io = io.BytesIO()
        surface.write_to_png(img_io)
        img_io.seek(0)
        frames.append(img_io.read())

    gif_io = io.BytesIO()
    from PIL import Image
    images = [Image.open(io.BytesIO(frame)) for frame in frames]
    images[0].save(gif_io, format="GIF", save_all=True, append_images=images[1:], duration=1000, loop=0)
    gif_io.seek(0)

    return gif_io

# 🔹 API endpoint voor GIF
@app.route('/countdown.gif')
def countdown_gif():
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_timestamp = parse_end_time(end_string)

    if end_timestamp is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    gif_io = generate_countdown_gif(end_timestamp)
    return Response(gif_io, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
