import os
import datetime
import time
import io
import imageio
import flask
import cairo
from flask import Flask, Response, request
from urllib.parse import unquote

app = Flask(__name__)

# ✅ Pad naar emoji-font (moet kloppen met build.sh!)
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

def parse_end_time(end_string):
    """ Converteert een datum-string naar een UNIX-timestamp """
    try:
        end_string = unquote(end_string).replace("+", " ")  # Spaties vervangen
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())  # Zet om naar UNIX timestamp
    except ValueError:
        return None  # Ongeldige invoer

def generate_countdown_image(remaining_time):
    """ Genereert een countdown afbeelding met Cairo en emoji's """
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # ✅ Afmetingen van de afbeelding
    width, height = 600, 200
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    ctx = cairo.Context(surface)

    # ✅ Achtergrondkleur (blauw)
    ctx.set_source_rgb(0, 0.34, 0.71)  # RGB: (0, 87, 183)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()

    # ✅ Laad emoji-vriendelijk lettertype
    if os.path.exists(FONT_PATH):
        font = FONT_PATH
    else:
        font = "Sans"  # Valt terug op systeemfont als emoji-font ontbreekt

    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    # ✅ Countdown labels en emoji's
    labels = ["🌙 DAGEN", "⭐ UREN", "✨ MINUTEN", "☀️ SECONDEN"]
    values = [f"{days:02} 🪨", f"{hours:02} ∴", f"{minutes:02} ◻️", f"{seconds:02}"]

    # ✅ Teken labels bovenaan
    ctx.set_font_size(18)
    ctx.set_source_rgb(1, 1, 1)  # Wit
    for i, label in enumerate(labels):
        x_pos = 40 + i * 140
        ctx.move_to(x_pos, 40)
        ctx.show_text(label)

    # ✅ Teken countdown waarden
    ctx.set_font_size(36)
    for i, value in enumerate(values):
        x_pos = 40 + i * 140
        ctx.move_to(x_pos, 100)
        ctx.show_text(value)

    # ✅ Extra info onderaan
    ctx.set_font_size(14)
    ctx.move_to(50, 180)
    ctx.show_text("Aanmelden voor de O∴ L∴ is mogelijk tot")

    ctx.move_to(320, 180)
    ctx.show_text(datetime.datetime.fromtimestamp(end_time).strftime("%d-%m-%Y %H:%M:%S"))

    surface.flush()

    # ✅ Opslaan als PNG in geheugen
    img_io = io.BytesIO()
    surface.write_to_png(img_io)
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

def generate_countdown_gif(end_time):
    """ Genereert een countdown GIF met Cairo en emoji's """
    frames = []
    duration_per_frame = 1000  # ✅ 1 seconde per frame

    for i in range(30):  # 30 seconden aftellen
        remaining_time = max(0, end_time - int(time.time()) - i)  # ✅ Tel per seconde af
        img_io = generate_countdown_image(remaining_time)
        frames.append(imageio.imread(img_io))

    # ✅ GIF genereren met loop=0 (oneindige herhaling)
    gif_io = io.BytesIO()
    imageio.mimsave(gif_io, frames, format="GIF", duration=1, loop=0)
    gif_io.seek(0)

    return gif_io

@app.route('/countdown.gif')
def countdown_gif():
    """ API endpoint om een countdown GIF te genereren """

    end_string = request.args.get('end', "2025-01-01 00:00:00")
    global end_time
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    gif_io = generate_countdown_gif(end_time)
    return Response(gif_io, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
