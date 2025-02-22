import os
import datetime
import time
import io
import imageio
import flask
import cairo
import gi
from flask import Flask, Response, request
from urllib.parse import unquote

# Initialiseer Pango
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo

app = Flask(__name__)

def create_pango_layout(ctx, text, font_size, is_bold=False):
    """Helper functie voor het maken van een Pango layout"""
    layout = PangoCairo.create_layout(ctx)
    font_desc = Pango.FontDescription(f"Sans {'Bold' if is_bold else 'Normal'} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text, -1)
    return layout

def generate_countdown_image(remaining_time):
    """Genereert een countdown afbeelding met Cairo en Pango voor emoji-ondersteuning"""
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
    ctx.set_source_rgb(0, 0.34, 0.71)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()

    # Stel tekstkleur in op wit
    ctx.set_source_rgb(1, 1, 1)

    # Labels en waarden met emoji's
    labels = [
        ("🌙 DAGEN", 40),
        ("⭐ UREN", 180),
        ("✨ MINUTEN", 320),
        ("☀️ SECONDEN", 460)
    ]
    values = [
        (f"{days:03d} 🪨", 40),
        (f"{hours:02d} ∴", 180),
        (f"{minutes:02d} ◻️", 320),
        (f"{seconds:02d}", 460)
    ]

    # Teken labels met Pango
    for text, x_pos in labels:
        ctx.save()
        ctx.translate(x_pos, 40)
        layout = create_pango_layout(ctx, text, 18, True)
        PangoCairo.show_layout(ctx, layout)
        ctx.restore()

    # Teken waarden met Pango
    for text, x_pos in values:
        ctx.save()
        ctx.translate(x_pos, 100)
        layout = create_pango_layout(ctx, text, 36, True)
        PangoCairo.show_layout(ctx, layout)
        ctx.restore()

    # Teken onderste tekst
    ctx.save()
    ctx.translate(50, 180)
    layout = create_pango_layout(ctx, "Aanmelden voor de O∴ L∴ is mogelijk tot", 14)
    PangoCairo.show_layout(ctx, layout)
    ctx.restore()

    # Teken timestamp
    ctx.save()
    ctx.translate(320, 180)
    layout = create_pango_layout(
        ctx,
        datetime.datetime.fromtimestamp(end_time).strftime("%d-%m-%Y %H:%M:%S"),
        14
    )
    PangoCairo.show_layout(ctx, layout)
    ctx.restore()

    # Genereer PNG output
    surface.flush()
    img_io = io.BytesIO()
    surface.write_to_png(img_io)
    img_io.seek(0)

    return img_io

@app.route('/countdown.png')
def countdown_png():
    """API endpoint om een countdown afbeelding te genereren"""
    end_string = request.args.get('end', "2025-01-01 00:00:00")
    global end_time
    end_time = parse_end_time(end_string)

    if end_time is None:
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS", 400

    now = int(time.time())
    remaining_time = max(0, end_time - now)

    img_io = generate_countdown_image(remaining_time)
    return Response(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))