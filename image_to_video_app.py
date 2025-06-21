import streamlit as st
import cv2
import os
import tempfile
from natsort import natsorted
from PIL import Image
import numpy as np

st.set_page_config(page_title="Smart Video Bot", layout="centered")
st.title("🎬 Frame-to-Video Generator")

# Upload image files
uploaded_files = st.file_uploader("📂 Upload image frames (in order)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

fps = st.slider("🎚 Set Frame Rate (FPS)", 1, 60, 24)
text_overlay = st.text_input("📝 Add text overlay on video (optional)", "")

if uploaded_files and st.button("🎬 Generate Video"):
    with st.spinner("Processing your video..."):

        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []

            # Save uploaded images to temp dir
            for uploaded_file in uploaded_files:
                filepath = os.path.join(temp_dir, uploaded_file.name)
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                image_paths.append(filepath)

            image_paths = natsorted(image_paths)

            first_img = cv2.imread(image_paths[0])
            height, width, _ = first_img.shape

            video_path = os.path.join(temp_dir, "final_video.mp4")
            out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

            for path in image_paths:
                img = cv2.imread(path)
                if img.shape[:2] != (height, width):
                    img = cv2.resize(img, (width, height))
                if text_overlay:
                    cv2.putText(img, text_overlay, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                out.write(img)

            out.release()

            st.success("✅ Video generated!")
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button("⬇️ Download Video", data=f, file_name="final_video.mp4", mime="video/mp4")
