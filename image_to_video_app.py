import streamlit as st
import cv2
import os
import tempfile
from natsort import natsorted

st.title("🧠 Frame-to-Video Generator Bot")

# Upload image files
uploaded_files = st.file_uploader("Upload image frames (in order)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

fps = st.slider("Select Frame Rate (FPS)", 1, 60, 24)

if uploaded_files:
    if st.button("🎬 Generate Video"):
        with st.spinner("Processing video..."):

            # Create temp directory to store files
            with tempfile.TemporaryDirectory() as temp_dir:
                filepaths = []
                
                for uploaded_file in uploaded_files:
                    filepath = os.path.join(temp_dir, uploaded_file.name)
                    with open(filepath, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    filepaths.append(filepath)

                # Sort naturally: frame1.png, frame2.png, etc.
                filepaths = natsorted(filepaths)

                # Read first image for resolution
                first_img = cv2.imread(filepaths[0])
                height, width, _ = first_img.shape

                video_path = os.path.join(temp_dir, "output.mp4")
                out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

                for path in filepaths:
                    img = cv2.imread(path)
                    if img.shape[:2] != (height, width):
                        img = cv2.resize(img, (width, height))
                    out.write(img)

                out.release()

                # Let user download video
                with open(video_path, "rb") as f:
                    st.success("✅ Video generated!")
                    st.download_button(label="⬇️ Download Video", data=f, file_name="generated_video.mp4", mime="video/mp4")
