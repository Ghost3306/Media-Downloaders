from redvid import Downloader
reddit = Downloader(max_q=True)
reddit.url = "https://www.reddit.com/r/bollynewsandgossips/comments/1qohtgc/rahul_vaidya_urges_people_to_not_buy_tata_nexon/"
reddit.download()