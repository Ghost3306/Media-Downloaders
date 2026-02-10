import subprocess
from innertube import InnerTube

def download_video(url):
    try:
        # Try InnerTube first
        client = InnerTube("WEB")
        vid = url.split("v=")[-1]
        data = client.player(vid)

        formats = data["streamingData"].get("formats", [])
        mp4s = [f for f in formats if "url" in f]

        if mp4s:
            print("[OK] Direct MP4 found (rare)")
            return

        raise RuntimeError("Ciphered only")

    except Exception:
        print("Failed")
        

download_video("https://youtu.be/N7EKS2aW_oc?si=UTe--vXOQSGIxXaR")
