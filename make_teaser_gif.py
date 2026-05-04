#!/usr/bin/env python3
"""Generate a teaser GIF showcasing MMCORE capabilities."""
from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE, "assets", "teaser.gif")

CANVAS_W, CANVAS_H = 960, 540
BG_COLOR = (10, 10, 14)
ACCENT = (130, 90, 255)
TEXT_COLOR = (240, 240, 240)
SUBTLE_COLOR = (150, 150, 150)
LABEL_BG = (20, 20, 28)


def load_and_fit(path, target_w, target_h):
    img = Image.open(path).convert("RGBA")
    ratio = min(target_w / img.width, target_h / img.height)
    new_w, new_h = int(img.width * ratio), int(img.height * ratio)
    return img.resize((new_w, new_h), Image.LANCZOS)


def make_bg():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    # Subtle bottom gradient glow
    for y in range(CANVAS_H - 80, CANVAS_H):
        progress = (y - (CANVAS_H - 80)) / 80
        r = int(BG_COLOR[0] + (ACCENT[0] - BG_COLOR[0]) * progress * 0.08)
        g = int(BG_COLOR[1] + (ACCENT[1] - BG_COLOR[1]) * progress * 0.08)
        b = int(BG_COLOR[2] + (ACCENT[2] - BG_COLOR[2]) * progress * 0.15)
        draw.line([(0, y), (CANVAS_W, y)], fill=(r, g, b))
    return img


def get_font(size):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except:
        return ImageFont.load_default()


def add_label_bar(frame, category, description):
    draw = ImageDraw.Draw(frame)
    # Dark label bar at top
    draw.rectangle([(0, 0), (CANVAS_W, 70)], fill=LABEL_BG)
    # Accent line
    draw.rectangle([(0, 70), (CANVAS_W, 72)], fill=(*ACCENT, 80))

    cat_font = get_font(13)
    desc_font = get_font(19)
    draw.text((40, 16), category, fill=ACCENT, font=cat_font)
    draw.text((40, 38), description, fill=TEXT_COLOR, font=desc_font)


def create_title_frame():
    frame = make_bg()
    draw = ImageDraw.Draw(frame)

    title_font = get_font(64)
    sub_font = get_font(22)
    small_font = get_font(14)

    title = "MMCORE"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (CANVAS_W - tw) // 2
    draw.text((tx, 160), title, fill=TEXT_COLOR, font=title_font)

    sub = "Unified Multimodal Generation & Editing"
    bbox2 = draw.textbbox((0, 0), sub, font=sub_font)
    sw = bbox2[2] - bbox2[0]
    draw.text(((CANVAS_W - sw) // 2, 245), sub, fill=SUBTLE_COLOR, font=sub_font)

    # Accent bar
    bar_w = 120
    draw.rounded_rectangle(
        [(CANVAS_W // 2 - bar_w // 2, 295), (CANVAS_W // 2 + bar_w // 2, 299)],
        radius=2, fill=ACCENT
    )

    # Footer
    footer = "Text-to-Image  •  Image Editing  •  Multi-Reference Composition"
    bbox3 = draw.textbbox((0, 0), footer, font=small_font)
    fw = bbox3[2] - bbox3[0]
    draw.text(((CANVAS_W - fw) // 2, 340), footer, fill=(100, 100, 110), font=small_font)

    return frame


def create_t2i_frame(img_path, prompt_short):
    frame = make_bg()
    add_label_bar(frame, "TEXT → IMAGE", f'"{prompt_short}"')

    img = load_and_fit(img_path, CANVAS_W - 80, CANVAS_H - 120)
    x = (CANVAS_W - img.width) // 2
    y = 80 + (CANVAS_H - 100 - img.height) // 2
    frame.paste(img, (x, y), img)

    # Subtle border around image
    draw = ImageDraw.Draw(frame)
    draw.rectangle(
        [(x - 1, y - 1), (x + img.width, y + img.height)],
        outline=(40, 40, 50), width=1
    )
    return frame


def create_edit_frame(input_path, output_path, label):
    frame = make_bg()
    add_label_bar(frame, "IMAGE EDITING", label)

    content_top = 85
    content_h = CANVAS_H - content_top - 50
    pair_w = (CANVAS_W - 130) // 2

    inp = load_and_fit(input_path, pair_w, content_h)
    out = load_and_fit(output_path, pair_w, content_h)

    # Center both vertically
    y1 = content_top + (content_h - inp.height) // 2
    y2 = content_top + (content_h - out.height) // 2

    x1 = 40
    x2 = CANVAS_W - 40 - out.width

    frame.paste(inp, (x1, y1), inp)
    frame.paste(out, (x2, y2), out)

    draw = ImageDraw.Draw(frame)
    # Borders
    draw.rectangle([(x1 - 1, y1 - 1), (x1 + inp.width, y1 + inp.height)], outline=(40, 40, 50), width=1)
    draw.rectangle([(x2 - 1, y2 - 1), (x2 + out.width, y2 + out.height)], outline=(40, 40, 50), width=1)

    # Arrow in center
    arrow_font = get_font(32)
    mid_x = CANVAS_W // 2
    mid_y = content_top + content_h // 2
    draw.text((mid_x - 10, mid_y - 18), "→", fill=ACCENT, font=arrow_font)

    # Labels
    label_font = get_font(12)
    draw.text((x1, y1 + inp.height + 8), "INPUT", fill=SUBTLE_COLOR, font=label_font)
    draw.text((x2 + out.width - 52, y2 + out.height + 8), "OUTPUT", fill=SUBTLE_COLOR, font=label_font)

    return frame


# --- Build frames ---
frames = []

frames.append(create_title_frame())

t2i_samples = [
    ("hongkong_neon.jpeg", "Hong Kong neon night street"),
    ("enchanted_forest.jpeg", "Enchanted forest with moss and ferns"),
    ("wrathful_deity.jpeg", "Wrathful deity colossus in flames"),
    ("village_terraces.jpeg", "Chinese village with terraced fields"),
    ("whirlpool_vortex.jpeg", "Abyssal whirlpool vortex"),
    ("flower_bus.jpeg", "Flower-covered double-decker bus"),
]

for fname, prompt in t2i_samples:
    path = os.path.join(BASE, "assets", "t2i", fname)
    if os.path.exists(path):
        frames.append(create_t2i_frame(path, prompt))

edit_samples = [
    ("evening", "Transform to evening scene"),
    ("pyramids", "Change background to pyramids"),
    ("chinese_painting", "Style as Chinese painting"),
    ("shiba", "Transform dog breed"),
    ("swan", "Add swan to scene"),
    ("bronze", "Colorful bronze styling"),
]

for name, label in edit_samples:
    inp = os.path.join(BASE, "assets", "edit", f"{name}_input.jpeg")
    out = os.path.join(BASE, "assets", "edit", f"{name}_output.jpeg")
    if os.path.exists(inp) and os.path.exists(out):
        frames.append(create_edit_frame(inp, out, label))

frames.append(create_title_frame())

# Timing: title frames longer, content shorter for snappy feel
durations = [2200] + [1600] * (len(frames) - 2) + [2200]

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    optimize=True,
)

print(f"Created teaser GIF: {OUTPUT}")
print(f"  Frames: {len(frames)}")
print(f"  Size: {os.path.getsize(OUTPUT) / 1024 / 1024:.1f} MB")
