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
    """ Genereert een countdown afbeelding met verbeterde breedte en layout """
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    # 🔹 Nieuwe breedte en hoogte
    width, height = 600, 200
    img = Image.new('RGB', (width, height), color=(0, 87, 183))  # Blauw
    draw = ImageDraw.Draw(img)

    # 🔹 Lettergrootte aanpassen
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_small = ImageFont.truetype("DejaVuSans-Bold.ttf", 12)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 🔹 Countdown waarden en labels
    values = [f"{days:02}", f"{hours:02}", f"{minutes:02}", f"{seconds:02}"]
    labels = ["Dagen", "Uren", "Minuten", "Seconden"]

    # 🔹 Posities voor blokken
    block_width = width // 4
    for i in range(4):
        x_pos = i * block_width + (block_width // 2) - 40  # Centraal uitlijnen

        # Teken de cijfers
        draw.text((x_pos, 50), values[i], font=font_large, fill=(255, 255, 255))  # Wit

        # Teken de labels
        draw.text((x_pos, 140), labels[i], font=font_small, fill=(255, 255, 255))  # Wit

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
    """ Genereert een GIF van 30 seconden met exact 1 seconde per frame """
    frames = []
    duration_per_frame = 1  # 🔹 Nu precies 1 seconde per frame

    for i in range(30):  # 30 frames (30 seconden)
        remaining_time = max(0, end_time - int(time.time()) - i)  # 🔹 Tel per seconde af
        frame = generate_countdown_image(remaining_time)

        # Opslaan in geheugen
        img_io = io.BytesIO()
        frame.save(img_io, format="PNG")
        img_io.seek(0)

        frames.append(imageio.imread(img_io))

    # 🔹 GIF genereren met 1 seconde per frame
    gif_io = io.BytesIO()
    imageio.mimsave(gif_io, frames, format="GIF", duration=1)  # 🔹 1 seconde per frame
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
