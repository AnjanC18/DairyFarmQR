import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from flask import current_app

def generate_animal_qr(tag_number, animal_info=None):
    """
    Generates a QR code image for the given animal tag number.
    Saves to the static/qr_codes folder.
    Returns the filename (e.g. 'DF-101.png').
    """
    qr_folder = current_app.config.get('QR_FOLDER')
    os.makedirs(qr_folder, exist_ok=True)
    
    filename = f"{tag_number.replace('/', '_').replace(' ', '_')}.png"
    filepath = os.path.join(qr_folder, filename)

    # QR payload can be tag_number or full structured JSON
    payload = tag_number

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e3a8a", back_color="white").convert('RGB')

    # Add tag banner at the bottom of the image for visual clarity
    width, height = img.size
    banner_height = 40
    new_img = Image.new('RGB', (width, height + banner_height), color='#1e3a8a')
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    text = f"TAG: {tag_number}"
    
    # Try to calculate text position
    try:
        # Default font
        font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (width - text_w) / 2
        text_y = height + (banner_height - text_h) / 2
        draw.text((text_x, text_y), text, fill="white", font=font)
    except Exception:
        draw.text((width / 4, height + 10), text, fill="white")

    new_img.save(filepath, format='PNG')
    return filename
