# import subprocess


# URLS = [
#     "https://youtu.be/rkW_0_ZDDw0",
#     "https://youtu.be/TmXL3Ejl9II",
#     "https://youtu.be/OK8Vu12zN8A",
#     "https://youtu.be/MVeeRCRw5kM",
   
# ]
# #url = "https://youtu.be/dR9B_gPxjkk?si=Tr5bCiUP1I9YBPIl"
# subprocess.run([
#     "gradlew.bat",
#     "run",
#     f"--args={url}"
# ], shell=True)



import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

URLS = [
    "https://youtu.be/-YlmnPh-6rE?si=w4OXmFMmm5z8Wt3N",
    "https://youtu.be/GX9x62kFsVU?si=P65PJsGIUJL0dXkA",
    "https://youtu.be/lBvbNxiVmZA?si=W_LKB92iK2LQFMSW",
    "https://youtu.be/6d5SS0gS5bU?si=XtJ45ZN35YyZBUu-",
]

MAX_WORKERS = 3


def run_download(url):
    return subprocess.run(
        [
            "gradlew.bat",
            "run",
            f"--args={url}"
        ],
        shell=True
    )


def main():
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(run_download, url) for url in URLS]

        for future in as_completed(futures):
            result = future.result()
            if result.returncode != 0:
                print("Download failed")


if __name__ == "__main__":
    main()
