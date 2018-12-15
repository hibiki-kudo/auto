from datetime import datetime

from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering


@generate_ordering('timestamp', 'icon', 'id', 'text', "media", 'user', 'replies', 'retweets', 'likes')
class Tweet:
    def __init__(self, user, icon, fullname, id, media, url, timestamp, text, replies, retweets, likes, html):
        self.user = user.strip('\@')
        self.fullname = fullname
        self.icon = icon
        self.id = id
        self.url = url
        self.timestamp = timestamp
        self.text = text
        self.media = media
        self.replies = replies
        self.retweets = retweets
        self.likes = likes
        self.html = html

    @classmethod
    def from_soup(cls, tweet):
        return cls(
            user=tweet.find('span', 'username').text or "",
            fullname=tweet.find('strong', 'fullname').text or "",
            id=tweet['data-item-id'] or "",
            icon=tweet.find("img")["src"] or "",
            url=tweet.find('div', 'tweet')['data-permalink-path'] or "",
            timestamp=datetime.utcfromtimestamp(
                int(tweet.find('span', '_timestamp')['data-time'])),
            text=tweet.find('p', 'tweet-text').text or "",
            media=[media["src"] for media in
                   tweet.find_all("img", attrs={"data-aria-label-part": "", "class": ""})] or [],
            replies=int(tweet.find(
                'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'),
            retweets=int(tweet.find(
                'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'),
            likes=int(tweet.find(
                'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'),
            html=str(tweet.find('p', 'tweet-text')) or "",
        )

    @classmethod
    def from_html(cls, html):
        soup = BeautifulSoup(html, "lxml")
        tweets = soup.find_all('li', 'js-stream-item')
        if tweets:
            for tweet in tweets:
                try:
                    yield cls.from_soup(tweet)
                except AttributeError:
                    pass  # Incomplete info? Discard!
                except TypeError:
                    pass  # Incomplete info? Discard!
