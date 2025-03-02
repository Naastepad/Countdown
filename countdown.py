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

def parse_end_time(end_string):
    """ Converteert een datum-string naar een UNIX-timestamp """
    try:
        end_string = unquote(end_string).replace("+", " ")
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
    except ValueError:
        return None

def generate_countdown_image(remaining_time, event_name):
    """ Genereert een countdown afbeelding met Cairo zonder emoji's """
    # Bereken tijdwaarden
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # Initialiseer Cairo surface
    width, height = 600, 200
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    ctx = cairo.Context(surface)

    # Teken blauwe achtergrond
    ctx.set_source_rgb(0, 0.34, 0.71)  # RGB: (0, 87, 183)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()

    # Stel standaard font in
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    
    # Definieer labels en waarden zonder emoji's
    labels = ["DAGEN", "UREN", "MINUTEN", "SECONDEN"]
    values = [f"{days:02d}", f"{hours:02d}", f"{minutes:02d}", f"{seconds:02d}"]

    # Teken labels (kleiner lettertype)
    ctx.set_source_rgb(1, 1, 1)  # Wit
    ctx.set_font_size(18)
    for i, label in enumerate(labels):
        x_pos = 40 + i * 140
        ctx.move_to(x_pos, 40)
        ctx.show_text(label)

    # Teken waarden (groter lettertype)
    ctx.set_font_size(36)
    for i, value in enumerate(values):
        x_pos = 40 + i * 140
        ctx.move_to(x_pos, 100)
        ctx.show_text(value)

    # Teken evenement naam en datum in twee regels
    ctx.set_font_size(14)
    ctx.move_to(50, 170)
    ctx.show_text(f"Aanmelden voor {event_name}")
    
    ctx.move_to(50, 190)  # Meer naar boven geplaatst
    ctx.show_text(f"is mogelijk tot {datetime.datetime.fromtimestamp(end_time).strftime('%d-%m-%Y %H:%M')}")

    # Genereer PNG output
    surface.flush()
    img_io = io.BytesIO()
    surface.write_to_png(img_io)
    img_io.seek(0)

    return img_io

@app.route('/countdown.png')
def countdown_png():
    """ API endpoint om een countdown afbeelding te genereren """
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    event_name = request.args.get('doel', "een evenement")
    global end_time
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_time - now)

    img_io = generate_countdown_image(remaining_time, event_name)
    return Response(img_io, mimetype='image/png')

# GIF generatie endpoint
@app.route('/countdown.gif')
def countdown_gif():
    """ API endpoint om een countdown GIF te genereren """
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    event_name = request.args.get('doel', "een evenement")
    global end_time
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    frames = []
    for i in range(30):  # 30 frames
        now = int(time.time()) + i
        remaining_time = max(0, end_time - now)
        img_io = generate_countdown_image(remaining_time, event_name)
        frames.append(imageio.imread(img_io))

    # Genereer GIF
    gif_io = io.BytesIO()
    imageio.mimsave(gif_io, frames, format="GIF", duration=1000, loop=0)  # Verlaging snelheid naar 1000ms
    gif_io.seek(0)

    return Response(gif_io, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
