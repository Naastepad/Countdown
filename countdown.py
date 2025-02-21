import os
from flask import Flask, Response
from PIL import Image, ImageDraw, ImageFont
import datetime
import io

app = Flask(__name__)

# Gebruik de poort die Render toewijst, of standaard 10000
PORT = int(os.environ.get("PORT", 10000))

@app.route('/')
def home():
    return "Countdown Service is running! Try accessing /countdown.png"

@app.route('/countdown.png')
def countdown():
    img_io = generate_countdown_image()
    return Response(img_io, mimetype='image/png')

def generate_countdown_image():
    now = datetime.datetime.utcnow()
    target_datetime = datetime.datetime(2025, 3, 1, 12, 0, 0)
    remaining_time = target_datetime - now
    
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    img = Image.new('RGB', (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), f"{days}d {hours}h {minutes}m {seconds}s", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    draw.text(((400 - text_width) // 2, (100 - text_height) // 2), f"{days}d {hours}h {minutes}m {seconds}s", fill=(0, 0, 0), font=font)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
