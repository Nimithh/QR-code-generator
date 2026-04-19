import qrcode
from PIL import Image

EC_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}

def build_qr(data, qr_color, bg_color, error_correction, logo_path=None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=EC_MAP[error_correction],
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGBA")

    if logo_path:
        img = _embed_logo(img, logo_path)

    return img

def _embed_logo(qr_img, logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    qr_w, qr_h = qr_img.size
    logo_size = qr_w // 4
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
    pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)
    qr_img.paste(logo, pos, logo)
    return qr_img
