from multiprocessing import Process
from .api import app
from .getter import Getter
from .tester import Tester
from . import setting
import time

TESTER_CYCLE = setting.TESTER_CYCLE
GETTER_CYCLE = setting.GETTER_CYCLE
TESTER_ENABLED = setting.TESTER_ENABLED
GETTER_ENABLED = setting.GETTER_ENABLED
API_ENABLED = setting.API_ENABLED
API_HOST = setting.API_HOST
API_PORT = setting.API_PORT

class Scheduler():
    def schedule_tester(self, cycle=TESTER_CYCLE):
        """
        定时测试代理
        """
        tester = Tester() 
        while True:
            print('Tester is running...')
            tester.run()
            time.sleep(cycle)
        
    def schedule_getter(self, cycle=GETTER_CYCLE):
        """
        定时获取代理
        """
        getter = Getter()
        while True:
            print('Start crawling proxies...')
            getter.run()
            time.sleep(cycle)

    def schedule_api(self):
        """
        Start API service
        """
        app.run(API_HOST, API_PORT)

    def run(self):
        print('Proxy pool starts running')
        
        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()
        
        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()
        
        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()