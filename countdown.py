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

# Algemene instellingen
WIDTH, HEIGHT = 600, 200
FONT_SIZE_LABEL = 18
FONT_SIZE_VALUE = 36
FONT_SIZE_FOOTER = 14
BG_COLOR = (0, 0.34, 0.71)  # Blauw
TEXT_COLOR = (1, 1, 1)  # Wit
GIF_DELAY = 1000  # Vertraging per frame in ms

def parse_end_time(end_string):
    """ Converteert een datum-string naar een UNIX-timestamp """
    try:
        end_string = unquote(end_string).replace("+", " ")
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
    except ValueError:
        return None

def generate_countdown_image(remaining_time, end_time):
    """ Genereert een countdown afbeelding met Cairo """
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Achtergrondkleur
    ctx.set_source_rgb(*BG_COLOR)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # Stel standaard font in
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    # Labels en waarden
    labels = ["DAGEN", "UREN", "MINUTEN", "SECONDEN"]
    values = [f"{days:02d}", f"{hours:02d}", f"{minutes:02d}", f"{seconds:02d}"]

    # Teken labels
    ctx.set_source_rgb(*TEXT_COLOR)
    ctx.set_font_size(FONT_SIZE_LABEL)
    for i, label in enumerate(labels):
        x_pos = 40 + i * 140
        ctx.move_to(x_pos, 40)
        ctx.show_text(label)

    # Teken waarden
    ctx.set_font_size(FONT_SIZE_VALUE)
    for i, value in enumerate(values):
        x_pos = 40 + i * 140
        ctx.move_to(x_pos, 100)
        ctx.show_text(value)

    # Teken korte tekst onderaan
    ctx.set_font_size(FONT_SIZE_FOOTER)
    ctx.move_to(50, 180)
    ctx.show_text("Aanmelden is mogelijk tot")

    # Controleer of end_time geldig is
    if end_time:
        ctx.move_to(320, 180)
        ctx.show_text(datetime.datetime.fromtimestamp(end_time).strftime("%d-%m-%Y %H:%M:%S"))

    # PNG-output genereren
    surface.flush()
    img_io = io.BytesIO()
    surface.write_to_png(img_io)
    img_io.seek(0)

    return img_io

@app.route('/countdown.png')
def countdown_png():
    """ API endpoint om een countdown afbeelding te genereren """
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_time - now)

    img_io = generate_countdown_image(remaining_time, end_time)
    return Response(img_io, mimetype='image/png')

@app.route('/countdown.gif')
def countdown_gif():
    """ API endpoint om een countdown GIF te genereren """
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    frames = []
    for i in range(30):  # 30 frames
        now = int(time.time()) + i
        remaining_time = max(0, end_time - now)
        img_io = generate_countdown_image(remaining_time, end_time)
        frames.append(imageio.imread(img_io))

    # Genereer GIF met **1000 ms per frame**
    gif_io = io.BytesIO()
    imageio.mimsave(gif_io, frames, format="GIF", duration=GIF_DELAY / 1000, loop=0)  # 1000ms per frame
    gif_io.seek(0)

    return Response(gif_io, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
