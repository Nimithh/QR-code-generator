import streamlit as st
from PIL import Image
import io
from qr_builder import build_qr

st.set_page_config(page_title="QR Code Generator", page_icon="🔳", layout="centered")

st.title("🔳 QR Code Generator")
st.markdown("Generate a QR code from any text or URL — optionally with a logo.")

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────

data = st.text_area("Text or URL", placeholder="https://example.com", height=100)

col1, col2 = st.columns(2)
with col1:
    qr_color = st.color_picker("QR Color", "#000000")
with col2:
    bg_color = st.color_picker("Background Color", "#ffffff")

quality = st.radio(
    "Scan Quality",
    ["Low", "Medium", "High", "Max"],
    index=3,
    horizontal=True,
)
quality_map = {"Low": "L", "Medium": "M", "High": "Q", "Max": "H"}

logo_file = st.file_uploader("Embed Logo (optional)", type=["png", "jpg", "jpeg", "bmp", "ico"])

st.divider()

# ── Generate ──────────────────────────────────────────────────────────────────

if st.button("Generate QR", type="primary", use_container_width=True):
    if not data.strip():
        st.warning("Please enter some text or a URL.")
    else:
        with st.spinner("Generating..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                tmp_path = "/tmp/logo_upload.png"
                logo_img.save(tmp_path)
                logo_path = tmp_path

            img = build_qr(data.strip(), qr_color, bg_color,
                           quality_map[quality], logo_path)
            img_rgb = img.convert("RGB")

        st.success("QR code generated!")
        st.image(img_rgb, caption="Your QR Code", use_container_width=False, width=300)

        buf = io.BytesIO()
        img_rgb.save(buf, format="PNG")
        st.download_button(
            label="⬇ Download PNG",
            data=buf.getvalue(),
            file_name="qrcode.png",
            mime="image/png",
            use_container_width=True,
        )
