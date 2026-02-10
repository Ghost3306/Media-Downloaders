
from reddit_downloader import Reddit
URLs = [
    "https://www.reddit.com/r/BuyItForLife/comments/1q0zlxe/buy_it_for_life_cars/",
    "https://www.reddit.com/r/coolguides/comments/1iahpgp/a_cool_guide_to_used_cars_to_avoid/",
    "https://www.reddit.com/r/Mcat/comments/1dp9g52/cars_is_easy_actually/",
    "https://www.reddit.com/r/CarsIndia/comments/19f3ye6/tata_cars_dont_have_resale_value/",
    "https://www.reddit.com/r/CarsIndia/comments/1qq8shb/stumbled_upon_this_video_and_now_im_rethinking_my/",
    "https://www.reddit.com/r/youtubeindia/comments/1qbqere/cars_youtube_at_its_best_tata_punch_facelift/"
]


for url in URLs:
    Reddit.download_by_url(url)

print("all downloaded")