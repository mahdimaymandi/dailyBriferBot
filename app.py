import json
from mastodon import Mastodon
import feedparser
from cuttpy import Cuttpy
import config
import ssl
from pathlib import Path
from datetime import date
from datetime import datetime

entriesPath = Path(__file__).parent / "./entries.json"

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

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
    elif (source == "CNBC"):
        newsFeed = feedparser.parse("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114")
        sourceTitle = "CNBC"
    
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
        self.shortURL = None

    def shortenURL(self):
        try:
            shortener = Cuttpy(config.cuttly_token)
            response = shortener.shorten(self.link)
            self.shortURL = response.shortened_url
        except:
            print("Couldn't Shorten URL")
    
    def postOnBot(self):
        if (not self.isEntryUnique()):
            return False

        self.shortenURL()
        if (self.shortURL != None):
            self.recordEntry()
            message = self.title + " \nSource: " + self.source + "\nLink: " + self.shortURL
            mastodon.status_post(message)

        return True

    def isEntryUnique(self):
        f = open(entriesPath)
        data = json.loads(f.read())
        for record in data:
            if (record['title'] == self.title or record['summary'] == self.summary or record['link'] == self.link):
                return False
        return True
    
    def recordEntry(self):
        f = open(entriesPath)
        data = json.loads(f.read())
        currentTimestamp = datetime.now().timestamp()
        data.append({"title": self.title, "summary": self.summary, "link": self.link, "published": self.published, "timestamp": currentTimestamp})
        with open(entriesPath, "w") as outfile:
            json.dump(data, outfile)

def cleanEntries():
    f = open(entriesPath)
    data = json.loads(f.read())

    currentTimestamp = datetime.now().timestamp()
    oneWeekPriorTimestamp = currentTimestamp - (7 * 24 * 60 * 60) # 7 Days - 24 Hours - 60 Minutes - 60 Seconds

    # oneWeekPriorDate = datetime.fromtimestamp(oneWeekPriorTimestamp)

    # daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # weekday = daysOfWeek[oneWeekPriorDate.weekday()]

    # formattedDate = weekday + ", " + oneWeekPriorDate.strftime("%d %B %Y")

    i = 0
    while (i < len(data)):
        try:
            if (data[i]["timestamp"] <= oneWeekPriorTimestamp):
                del data[i]
        except:
            print("Record Does Not Have Timestamp")
        i += 1

    with open(entriesPath, "w") as outfile:
        json.dump(data, outfile)

postArticles("NYT")
postArticles("WSJ")
postArticles("CNBC")
cleanEntries()