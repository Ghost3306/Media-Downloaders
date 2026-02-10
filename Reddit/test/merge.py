# import subprocess
# try:
#     result = subprocess.run([
#                 "ffmpeg",
#                 "-i", "Video.mp4",
#                 "-i", f"Audio.mp3",
#                 "-c:v", "copy",
#                 "-c:a", "copy",
#                 f"Final.mp4"
#             ],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
           
#             )
#     print(result.stderr)
# except Exception as e:
#     print(e)

from pathlib import Path
import os

pwd = str(Path.cwd().parent)
print(str(pwd)+"\Reddit")
# video_path = os.path.join(pwd, f"temp_{v_title}.mp4")
# audio_path = os.path.join(pwd, f"temp_{v_title}.mp3")

# if os.path.exists(video_path):
#     os.remove(video_path)

# if os.path.exists(audio_path):
#     os.remove(audio_path)

# print("Video downloaded successfully")