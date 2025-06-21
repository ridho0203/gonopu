import streamlit as st
import cv2
import os
import tempfile
from natsort import natsorted
from moviepy.editor import VideoFileClip, AudioFileClip
from PIL import Image
import numpy as np

st.set_page_config(page_title="Smart Video Bot", layout="centered")
st.title("🎬 Frame-to-Video Generator 2.0")

# Upload image files
uploaded_files = st.file_uploader("📂 Upload image frames (in order)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Upload optional background music
audio_file = st.file_uploader("🎵 Optional: Upload background music (.mp3)", type=["mp3"])

fps = st.slider("🎚 Set Frame Rate (FPS)", 1, 60, 24)
text_overlay = st.text_input("📝 Add text overlay on video (leave blank for none)", "")

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

            raw_video_path = os.path.join(temp_dir, "raw_video.mp4")
            final_video_path = os.path.join(temp_dir, "final_video.mp4")

            out = cv2.VideoWriter(raw_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

            for path in image_paths:
                img = cv2.imread(path)
                if img.shape[:2] != (height, width):
                    img = cv2.resize(img, (width, height))

                if text_overlay:
                    cv2.putText(img, text_overlay, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                out.write(img)
            out.release()

            # Optional: add audio
            if audio_file:
                audio_path = os.path.join(temp_dir, "audio.mp3")
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())

                video = VideoFileClip(raw_video_path)
                audio = AudioFileClip(audio_path).subclip(0, video.duration)
                final = video.set_audio(audio)
                final.write_videofile(final_video_path, codec="libx264", audio_codec="aac")
                video_file_to_show = final_video_path
            else:
                video_file_to_show = raw_video_path

            st.success("✅ Video ready!")
            st.video(video_file_to_show)

            with open(video_file_to_show, "rb") as f:
                st.download_button("⬇️ Download Final Video", data=f, file_name="final_video.mp4", mime="video/mp4")
