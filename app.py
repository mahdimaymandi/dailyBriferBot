from mastodon import Mastodon

#   Set up Mastodon
mastodon = Mastodon(
    access_token = 'test',
    api_base_url = 'https://mstdn.social/'
)

# mastodon.status_post("hello world!")