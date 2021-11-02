from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import io
import textwrap
import random
import os
import pathlib

app = Flask(__name__)

here = os.path.abspath(os.path.dirname(__file__))
font_path = os.path.join(here, "../fonts/FreeMono.ttf")
image_path = os.path.join(here, "../images/")
images = [
    os.path.join(image_path, i)
    for i in os.listdir(image_path)
    if pathlib.Path(i).suffix in [".jpg", ".jpeg", ".png"]
]

IMAGE_SIZE = 800
font = ImageFont.truetype(font_path, 35)
author_font = ImageFont.truetype(font_path, 30)
credit_font = ImageFont.truetype(font_path, 25)


@app.route("/quote/", methods=["POST"])
def quote():
    data = request.get_json()

    with Image.open(random.choice(images)).convert("RGBA") as base:
        if not data.get("quote"):
            return "No quote supplied", 400

        if base.size[0] > base.size[1]:
            base = base.crop((0, 0, base.size[1] / base.size[0] * base.size[0], base.size[1]))
        elif base.size[1] > base.size[0]:
            base = base.crop((0, 0, base.size[0] / base.size[1] * base.size[1], base.size[1]))

        base = base.resize((IMAGE_SIZE, IMAGE_SIZE))

        border_color = data.get("border_color") or "#e6e600"

        enhancer = ImageEnhance.Brightness(base)
        base = enhancer.enhance(0.2)
        base = ImageOps.expand(base, border=4, fill=border_color)

        draw = ImageDraw.Draw(base)
        lines = textwrap.wrap(f'"{data.get("quote")}"', width=30)

        y_position = (500 - len(lines) * 45) / 2

        for line in lines:
            width = font.getsize(line)[0]
            draw.text(
                ((IMAGE_SIZE - width) / 2, y_position),
                line,
                font=font,
                fill=(255, 255, 255, 128),
            )
            y_position += 45

        author = data.get("author") or "No Author"
        credits = data.get("credits")

        draw.text(
            ((IMAGE_SIZE - author_font.getsize(author)[0]) / 2, y_position + 60),
            author,
            font=author_font,
            fill=(255, 255, 255, 128),
        )
        if credits:
            draw.text(
                ((IMAGE_SIZE - credit_font.getsize(credits)[0]) / 2, IMAGE_SIZE - 90),
                credits,
                font=credit_font,
                fill=(255, 255, 255, 128),
            )

        fp = io.BytesIO()
        base.save(fp, "png")
        fp.seek(0)

        return send_file(fp, mimetype="image/png")
