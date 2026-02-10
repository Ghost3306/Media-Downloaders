import instaloader

L = instaloader.Instaloader(
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern=""
)

# Login recommended (optional but improves success)
# L.login("username", "password")

shortcode = "DT0oRaDDbpn"  # from your URL
post = instaloader.Post.from_shortcode(L.context, shortcode)

L.download_post(post, target="downloads")
