def parse_rss_feed(url):
    import feedparser

    # Parse the RSS feed
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary,
        }
        articles.append(article)

    return articles

def fetch_and_parse_rss(url):
    import requests

    response = requests.get(url)
    if response.status_code == 200:
        return parse_rss_feed(url)
    else:
        raise Exception(f"Failed to fetch RSS feed: {response.status_code}")