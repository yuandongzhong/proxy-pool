import asyncio
import aiohttp
import time
import sys
from . import setting
from .db import RedisClient
try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError

VALID_STATUS_CODES = setting.VALID_STATUS_CODES
TEST_URL = setting.TEST_URL
BATCH_TEST_SIZE = setting.BATCH_TEST_SIZE


class Tester(object):
    def __init__(self):
        self.redis = RedisClient()
    
    async def test_single_proxy(self, proxy):
        """
        Test a single proxy
        :param proxy: a proxy
        :return: None
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('Testing ', proxy)
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('Proxy is working - ', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('Response error - ', proxy)
            except (ClientError, aiohttp.client_exceptions.ClientConnectorError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print('Proxy request failed - ', proxy)

    def run(self):
        """
        测试主函数
        :return:
        """
        print('测试器开始运行')
        try:
            count = self.redis.count()
            print('当前剩余', count, '个代理')
            for i in range(0, count, BATCH_TEST_SIZE):
                start = i
                stop = min(i + BATCH_TEST_SIZE, count)
                print('正在测试第', start + 1, '-', stop, '个代理')
                test_proxies = self.redis.batch(start, stop)
                loop = asyncio.get_event_loop()
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                sys.stdout.flush()
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)