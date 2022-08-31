from .db import RedisClient
from .crawler import Crawler
from . import setting
import sys

POOL_UPPER_THRESHOLD = setting.POOL_UPPER_THRESHOLD

class Getter():
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """
        Check if it reaches to pool limit
        """
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print('Getting proxies...')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                sys.stdout.flush()
                for proxy in proxies:
                    self.redis.add(proxy)
