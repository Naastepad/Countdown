import os
import datetime
import time
import io
import imageio
from flask import Flask, Response, request
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import unquote

app = Flask(__name__)

# Maçonnieke Unicode-symbolen
SYMBOLS = {
    "dag": "\U0001faa8",  # 🪨
    "uur": "\u2234",      # ∴
    "minuut": "\u25fb",   # ◻️
    "seconde": "\u2600\ufe0f"  # ☀️
}

LABELS = ["🌙 DAGEN", "⭐️ UREN", "✨ MINUTEN", "☀️ SECONDEN"]

# Pad naar het NotoColorEmoji lettertype
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoColorEmoji.ttf')

def load_font(size=24):
    """Laad het NotoColorEmoji-lettertype."""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except IOError:
        print("Het NotoColorEmoji-lettertype kon niet worden geladen.")
        return ImageFont.load_default()

def parse_end_time(end_string):
    """Converteer een datum-string naar een UNIX-timestamp en verwerk URL-encoding."""
    try:
        end_string = unquote(end_string).replace("+", " ")  # Verwerk spaties
        dt = datetime.datetime.strptime(end_string, "%Y-%m-%d %H:%M:%S")
        return dt  # Retourneer datetime-object
    except ValueError:
        return None  # Ongeldige invoer

def generate_countdown_image(remaining_time, end_time):
    """Genereer een countdown-afbeelding met maçonnieke elementen en correcte symbolen."""
    days = remaining_time // 86400
    hours = (remaining_time % 86400) // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60

    width, height = 800, 250
    img = Image.new('RGB', (width, height), color=(0, 87, 183))  # Blauw
    draw = ImageDraw.Draw(img)

    # Lettertypen laden
    font_large = load_font(70)
    font_small = load_font(28)

    # Bepaal de juiste iconen per status
    label_status = ["🌙", "⭐️", "✨", "☀️"]
    if days == 0:
        label_status[0] = "⚠️"
    if days == 0 and hours == 0:
        label_status[1] = "⌛️"
    if days == 0 and hours == 0 and minutes == 0:
        label_status[2] = "⌛️"
    if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
        label_status = ["🔒", "⌛️", "⌛️", "⌛️"]

    # Labels bovenaan
    for i, label in enumerate(LABELS):
        x_pos = i * (width // 4) + 40
        draw.text((x_pos, 20), f"{label_status[i]} {label}", font=font_small, fill=(255, 255, 255))

    # Countdown waarden met maçonnieke tekens
    values = [f"{days:02}", f"{hours:02}", f"{minutes:02}", f"{seconds:02}"]
    symbols = [SYMBOLS["dag"], SYMBOLS["uur"], SYMBOLS["minuut"], SYMBOLS["seconde"]]

    for i in range(4):
        x_pos = i * (width // 4) + 70
        draw.text((x_pos, 100), f"{values[i]} {symbols[i]}", font=font_large, fill=(255, 255, 255))

    # Instructie onderaan
    if remaining_time == 0:
        instruction = "⌛️ Tempus Fugit | aanmelden niet mogelijk"
    else:
        # Formatteer de eindtijd naar een leesbaar formaat
        end_time_str = end_time.strftime("%d-%m-%Y %H:%M:%S")
        instruction = f"Aanmelden voor de O∴ L∴ is mogelijk tot {end_time_str}"

    draw.text((width // 5, 200), instruction, font=font_small, fill=(255, 255, 255))

    return img

@app.route('/countdown.png')
def countdown_png():
    """API-endpoint om een countdown-afbeelding te genereren."""
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Ongeldig datumformaat. Gebruik JJJJ-MM-DD UU:MM:SS", 400

    now = datetime.datetime.now()
    remaining_time = max(0, int((end_time - now).total_seconds()))

    img = generate_countdown_image(remaining_time, end_time)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')

def generate_countdown_gif(end_time):
    """Genereer een GIF van 30 seconden met exact 1 seconde per frame en oneindige loop."""
    frames = []
    duration_per_frame = 1000  # 1 seconde per frame

    for i in range(30):  # 30 frames (30 seconden)
        remaining_time = max(0, int((end_time - datetime.datetime.now()).total_seconds()) - i)
        frame = generate_countdown_image(remaining_time, end_time)

        # Opslaan in geheugen
        img_io = io.BytesIO()
        frame.save(img_io, format="PNG")
        img_io.seek(0)

        frames.append(imageio.imread(img_io))

    # GIF genereren met 1 seconde per frame en oneindige loop
    gif_io = io.BytesIO()
    imageio.mimsave(gif_io, frames, format=" 
