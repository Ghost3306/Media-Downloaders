
import subprocess

def download_with_streamlink(url, quality="best", output="output.mp4"):
    cmd = [
        "streamlink",
        url,
        quality,
        "-o", output
    ]

    subprocess.run(cmd, check=True)

# Example
# download_with_streamlink(
#     "https://youtu.be/YyepU5ztLf4?si=jfKwB5z7kp2z3Rmv",
#     quality="best",
#     output="video-streamlink.mp4"
# )



URLS = [
    "https://youtu.be/rkW_0_ZDDw0?si=wg9ksoVpqwzXbFAl",
    "https://youtu.be/TmXL3Ejl9II?si=ipxAAGTspZoHSDgy",
    "https://youtu.be/OK8Vu12zN8A?si=Q-KOyBzga77OG6Jd",
    "https://youtu.be/MVeeRCRw5kM?si=MSEIfsByAMewYiLE",
    "https://youtu.be/QMKPvfNB6l0?si=VgHM91sK1Mur8AUr",
    "https://youtu.be/IolHQoQso0c?si=fqx7-8tpzmELfqDe",
    "https://youtu.be/OMpVji16f2E?si=NpHiPQ-110V4V83J",
]

for url in URLS:
    download_with_streamlink(
    url,
    quality="best",
    output=f"{url}.mp4"
)