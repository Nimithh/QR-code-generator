import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import base64
from qr_builder import build_qr

st.set_page_config(page_title="QR Code Generator", page_icon="🔳", layout="centered")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 680px; }
    #MainMenu, footer { visibility: hidden; }

    .step-label {
        font-size: 1rem; font-weight: 700; margin: 1.4rem 0 0.5rem;
        display: flex; align-items: center; gap: 10px;
    }
    .step {
        background: #4a90d9; color: white; border-radius: 50%;
        width: 26px; height: 26px; display: inline-flex;
        align-items: center; justify-content: center;
        font-size: 13px; font-weight: 800; flex-shrink: 0;
    }
    .tip {
        background: #1a1a2e; border-left: 3px solid #4a90d9;
        border-radius: 0 8px 8px 0; padding: 0.6rem 1rem;
        font-size: 0.85rem; color: #aaa; margin-top: 0.6rem;
    }
    .qr-result {
        background: white; border-radius: 20px;
        padding: 24px; text-align: center; margin: 1rem 0;
    }
    .qr-hint {
        text-align: center; color: #888; font-size: 0.82rem; margin-top: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem">
    <h1 style="font-size:2.2rem; font-weight:800; margin:0">🔳 QR Code Generator</h1>
    <p style="color:#888; margin-top:0.4rem">Turn any link or text into a scannable QR code in seconds</p>
</div>
<hr style="border:none; border-top:1px solid #2a2a2a; margin:1rem 0">
""", unsafe_allow_html=True)

# ── Step 1 ────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label"><span class="step">1</span> Enter your text or URL</div>', unsafe_allow_html=True)
data = st.text_area("", placeholder="e.g. https://google.com  or  Hello World!", height=110, label_visibility="collapsed")

# ── Step 2 ────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label"><span class="step">2</span> Customize <span style="color:#666; font-weight:400; font-size:0.85rem">(optional)</span></div>', unsafe_allow_html=True)

with st.expander("🎨  Open customization options"):
    col1, col2 = st.columns(2)
    with col1:
        qr_color = st.color_picker("QR Color", "#000000")
    with col2:
        bg_color = st.color_picker("Background Color", "#ffffff")

    logo_file = st.file_uploader("Add a logo in the center of the QR", type=["png", "jpg", "jpeg", "bmp", "ico"])
    st.markdown('<div class="tip">💡 When adding a logo, keep Scan Quality on <b>Max</b> so the QR still scans correctly.</div>', unsafe_allow_html=True)
    quality = st.radio("Scan Quality", ["Low", "Medium", "High", "Max"], index=3, horizontal=True)

# ── Step 3 ────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label"><span class="step">3</span> Generate your QR code</div>', unsafe_allow_html=True)

if st.button("⚡ Generate QR Code", type="primary", use_container_width=True):
    if not data.strip():
        st.warning("⚠️ Please enter some text or a URL first.")
    else:
        with st.spinner("Generating..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                tmp_path = "/tmp/logo_upload.png"
                logo_img.save(tmp_path)
                logo_path = tmp_path

            img = build_qr(
                data.strip(),
                qr_color if "qr_color" in dir() else "#000000",
                bg_color if "bg_color" in dir() else "#ffffff",
                {"Low": "L", "Medium": "M", "High": "Q", "Max": "H"}.get(quality if "quality" in dir() else "Max", "H"),
                logo_path,
            )
            img_rgb = img.convert("RGB")

        buf = io.BytesIO()
        img_rgb.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        img_data_url = f"data:image/png;base64,{b64}"

        st.success("✅ Done! Your QR code is ready.")

        # Show QR as clickable full-size image (easy to screenshot / long press on phone)
        components.html(f"""
        <div style="background:white; border-radius:20px; padding:24px; text-align:center;">
            <img src="{img_data_url}" style="width:260px; height:260px; border-radius:12px;" id="qrimg"/>
            <p style="color:#888; font-size:13px; margin:12px 0 0;">
                📱 <b>On phone:</b> long-press the image → Save / Copy<br>
                🖥️ <b>On desktop:</b> right-click the image → Copy / Save
            </p>
        </div>
        """, height=340)

        st.download_button(
            "⬇ Download QR as PNG",
            data=buf.getvalue(),
            file_name="qrcode.png",
            mime="image/png",
            use_container_width=True,
        )
