import redis
from . import setting
from random import choice
from .error import PoolEmptyError
import re

MAX_SCORE = setting.MAX_SCORE
MIN_SCORE = setting.MIN_SCORE
INITIAL_SCORE = setting.INITIAL_SCORE
REDIS_HOST = setting.REDIS_HOST
REDIS_PORT  = setting.REDIS_PORT
REDIS_PASSWORD = setting.REDIS_PASSWORD
REDIS_KEY = setting.REDIS_KEY

class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        Initialization
        :param host: Redis host address
        :param port: Redis port
        :Param password: Redis password
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
    
    def add(self, proxy, score=INITIAL_SCORE):
        """
        Adding proxy
        :param proxy: proxy
        :param score: proxy score
        :return: adding result
        """
        if not re.match(r'\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('Wrong proxy format - ', proxy, ' is ignored')
            return

        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, score, proxy)
    
    def random(self):
        """
        Randomly select valiable proxy. Firstly, try to select the proxy with highest score, if it is not existed, then select according to sorted result, else catch error.
        :return: random proxy
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError

    def decrease(self, proxy):
        """
        Decrease score by 1, if score is lower than MIN_SCORE, then delete
        : param proxy: proxy
        : return: modified score
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('Proxy ', proxy, ' current score: ', score, ' -1')
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            print('Proxy ', proxy, ' current score: ', score, ' Removed')
            return self.db.zrem(REDIS_KEY, proxy)
    
    def exists(self, proxy):
        """
        Check if a proxy exisits
        :param proxy: proxy
        :return True/False
        """
        return not self.db.zscore(REDIS_KEY, proxy) == None

    def max(self, proxy):
        """
        Set the proxy score to MAX_SCORE
        :param proxy: proxy
        :return: result
        """
        print('Proxy ', proxy, 'is available, score is ', MAX_SCORE)
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def count(self):
        """
        Count the proxies in database
        : return: number of proxies
        """
        return self.db.zcard(REDIS_KEY)
    
    def all(self):
        """
        Get all proxies
        : return: list of all proxies
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.db.zrevrange(REDIS_KEY, start, stop - 1)


if __name__ == '__main__':
    conn = RedisClient()
    result = conn.batch(1, 10)
    print(result)