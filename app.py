import json
from mastodon import Mastodon
import feedparser
from cuttpy import Cuttpy
import config

mastodon = Mastodon(
    access_token = config.bot_token,
    api_base_url = 'https://mstdn.social/'
)

def postArticles(source):
    newsFeed = None
    sourceTitle = None
    if (source == "NYT"):
        newsFeed = feedparser.parse("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml")
        sourceTitle = "New York Times"
    elif (source == "WSJ"):
        newsFeed = feedparser.parse("https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml")
        sourceTitle = "Wall Street Journal"
    
    i = 0
    while (i < config.total_posts_per_source):
        entry = Entry(newsFeed.entries[i]["title"], newsFeed.entries[i]["summary"], newsFeed.entries[i]["link"], newsFeed.entries[i]["published"], sourceTitle)
        entry.postOnBot()
        i += 1

class Entry:
    def __init__(self, title, summary, link, published, source):
        self.title = title
        self.summary = summary
        self.link = link
        self.published = published
        self.source = source

    def shortenURL(self):
        shortener = Cuttpy(config.cuttly_token)
        response = shortener.shorten(self.link)
        self.shortURL = response.shortened_url
    
    def postOnBot(self):
        if (not self.isEntryUnique()):
            return False

        self.recordEntry()
        self.shortenURL()

        message = self.title + " \nSource: " + self.source + "\nLink: " + self.shortURL
        mastodon.status_post(message)

        return True

    def isEntryUnique(self):
        f = open("entries.json")
        data = json.loads(f.read())
        for record in data:
            if ((record['title'] == self.title or record['summary'] == self.summary or record['link'] == self.link) and record['published'] == self.published):
                return False
        return True
    
    def recordEntry(self):
        f = open("entries.json")
        data = json.loads(f.read())
        data.append({"title": self.title, "summary": self.summary, "link": self.link, "published": self.published})
        with open("entries.json", "w") as outfile:
            json.dump(data, outfile)

postArticles("NYT")
postArticles("WSJ")