from RedDownloader import RedDownloader
url = "https://www.reddit.com/r/bollynewsandgossips/comments/1qohtgc/rahul_vaidya_urges_people_to_not_buy_tata_nexon/"

title = RedDownloader.GetPostTitle(url).Get()
print(title)

def get_title(url):
    title = RedDownloader.GetPostTitle(url).Get()
    print(url)
    return title
