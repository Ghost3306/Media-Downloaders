from RedDownloader import RedDownloader
url = "https://www.reddit.com/r/bollynewsandgossips/comments/1qohtgc/rahul_vaidya_urges_people_to_not_buy_tata_nexon/"

try:
    RedDownloader.Download(url,output="MyFiles",quality=1080)
except Exception as e:
    print(e)
