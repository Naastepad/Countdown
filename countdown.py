from flask import Flask, Response
from PIL import Image, ImageDraw, ImageFont
import datetime
import io

app = Flask(__name__)

# Doel datum/tijd instellen (pas dit aan naar je countdown-doel)
TARGET_DATETIME = datetime.datetime(2025, 3, 1, 12, 0, 0)  # 1 maart 2025 om 12:00

def generate_countdown_image():
    now = datetime.datetime.utcnow()
    remaining_time = TARGET_DATETIME - now
    
    # Bereken dagen, uren, minuten en seconden
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Maak een afbeelding (400x100 pixels)
    img = Image.new('RGB', (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Gebruik een standaard lettertype (pas dit aan naar een TTF-bestand op je server)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    # Tekst met countdown toevoegen
    countdown_text = f"{days}d {hours}h {minutes}m {seconds}s"
    text_width, text_height = draw.textsize(countdown_text, font=font)
    draw.text(((400 - text_width) // 2, (100 - text_height) // 2), countdown_text, fill=(0, 0, 0), font=font)

    # Bewaar de afbeelding in een buffer
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

@app.route('/countdown.png')
def countdown():
    img_io = generate_countdown_image()
    return Response(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
