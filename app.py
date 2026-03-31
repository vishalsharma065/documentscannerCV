import streamlit as st
import cv2
import numpy as np
from PIL import Image
from scanner import scan_document, preprocess, find_document_contour, perspective_transform, enhance_image
from ocr_reader import extract_text
import tempfile, os

st.set_page_config(page_title="Document Scanner", layout="wide")
st.title("📄 Document Scanner")
st.caption("Upload a photo of a document to scan and extract text.")

uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded:
    # Save to a temp file (OpenCV needs a path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    image = cv2.imread(tmp_path)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Original")
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_column_width=True)

    enhanced, warped = scan_document(tmp_path)

    with col2:
        st.subheader("Scanned (B&W)")
        st.image(enhanced, use_column_width=True)

    with col3:
        st.subheader("Color crop")
        if warped is not None:
            st.image(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB), use_column_width=True)
        else:
            st.info("No document edges detected.")

    st.subheader("📝 Extracted Text (OCR)")
    with st.spinner("Running OCR..."):
        text = extract_text(enhanced)

    if text:
        st.text_area("Result", text, height=200)
        st.download_button("💾 Download text", text, file_name="scanned_text.txt")
    else:
        st.warning("No text found. Try a clearer image.")

    os.unlink(tmp_path)