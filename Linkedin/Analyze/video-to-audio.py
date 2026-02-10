import subprocess
import os

ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

input_dir = r"D:\Tata Motors Internship\Source-Code\Media-Downloader\Linkedin\linkedin_downloads\videos"
output_dir = os.path.join(BASE_DIR, "audio")

os.makedirs(output_dir, exist_ok=True)

if not os.path.exists(input_dir):
    raise FileNotFoundError(f"'videos' folder not found at: {input_dir}")

for file in os.listdir(input_dir):
    if file.lower().endswith((".mp4", ".mkv", ".avi", ".mov")):
        input_video = os.path.join(input_dir, file)

        base_name = os.path.splitext(file)[0]
        output_audio = os.path.join(output_dir, base_name + ".mp3")

        subprocess.run([
            ffmpeg_path,
            "-y",
            "-i", input_video,
            "-vn",
            output_audio
        ], check=True)

        print("Saved audio:", output_audio)
