import os
import yt_dlp

@staticmethod
def download_video(url):
    print("Downloading LinkedIn video...")

    # 🔹 Get current script directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 🔹 Save in ./downloads folder (same directory as script)
    download_dir = os.path.join(base_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True)

    output_template = os.path.join(download_dir, '%(title)s.%(ext)s')

    try:
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': output_template,
            'quiet': True,
            'progress_hooks': [
                lambda d: print(f"Status: {d['status']}")
            ]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = os.listdir(download_dir)
        if not files:
            raise Exception("No file downloaded")

        # 🔹 Return full path of latest downloaded file
        files.sort(key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
        return os.path.join(download_dir, files[-1])

    except Exception as e:
        print(f"Error downloading video: {e}")
        raise ValueError(f"Failed to download LinkedIn video: {str(e)}")


download_video(
    "https://www.linkedin.com/posts/lalit-rawool_react-flask-websocket-activity-7393593863132733440-ymAS?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD2UYW8BhX4mDClkWKCesNiei52xwnwOlz8"
)
