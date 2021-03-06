# This is a sample Python script.

import logging
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import time
import urllib.request
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup
from pythonping import ping

path_file_log = "e:\\flibusta\\Update.log"  # Файл лога
path_to_lib = r'e:\flibusta\_LIB.RUS.EC\librusec'
path_to_file_temp = r'e:\temp\proxy.txt'

logging.basicConfig(filename=path_file_log, format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

pr_ping = {}


def test_proxy(proxy):
    # print(proxy)
    p = ping(proxy.split(':')[0]).rtt_avg_ms
    return (proxy, p)


class Free_Proxys(object):
    def __init__(self):
        self.pr_ping = {}
        self.proxy_list = []
        self.get_proxy_list()
        print('Proxy count {}'.format(len(self.proxy_list)))
        # self.run_test()

    def get_proxy_list(self):
        urllib.request.urlretrieve('http://spys.me/proxy.txt', r'e:\temp\proxy.txt')
        with open(path_to_file_temp, 'r') as f:
            lines = [line.strip() for line in f]
        self.proxy_list = [line.split() for line in lines[9:-2] if not 'RU' in line]
        self.proxy_list = [ip for proxy in self.proxy_list[:] for ip in proxy if ':' in ip]
        self.pr_ping = {proxy: 0 for proxy in self.proxy_list}

    def run_test(self, process_count=30):
        with Pool(processes=process_count) as pool:
            self.pr_ping = dict(list(pool.map(test_proxy, self.pr_ping.copy())))
        self.pr_ping = dict(sorted(self.pr_ping.items(), key=lambda pr: pr[1]))



class Flibusta_Day_Update(object):
    def __init__(self, path_to_lib, proxylist):
        self.path_to_lib = path_to_lib

        # self.filelist = [os.path.join(r, fn) for r, d, f in os.walk(path_to_lib) for fn in f[:] if '.zip' in fn]

        self.filelist = [fn for r, d, f in os.walk(path_to_lib) for fn in f[:] if '.zip' in fn]
        self.proxylist = proxylist
        self.clear_not_working_proxy(crit_time=600)  # proxy with ping time > 600 - deleted
        print('Proxy count < 600 ms {}'.format(len(self.proxylist)))
        self.ulr_to_flibusta = 'http://flibusta.is/daily/'
        self.page = ''
        self.current_proxy = ''
        if not self.find_working_proxy():
            print('error. Not load page!')
        else:
            self.clear_not_working_proxy()  # proxy not working - deleted
            print('Count proxy passed {}'.format(len(self.proxylist)))
            self.update_day_files()

    def get_page(self, proxy_test):
        proxy = proxy_test
        # print(proxy)
        try:
            r = requests.get(self.ulr_to_flibusta, proxies={'http': 'http://' + proxy})
            self.page = r.content
            if r.status_code != 200:
                print('error open ulr', r.status_code)
                return False
            else:
                self.current_proxy = proxy
                return True
        except:
            return False

    def clear_not_working_proxy(self, crit_time=9000):  # del proxy from proxylist{} not doing
        self.proxylist = {key: time for (key, time) in self.proxylist.items() if time < crit_time}

    def find_working_proxy(self):
        for proxy in self.proxylist.copy():
            # print(proxy, end=' > ')
            if self.get_page(proxy):
                # print('Pass')
                logging.info('proxy {}'.format(self.current_proxy))
                return True
            else:
                self.proxylist.pop(proxy)
                # self.proxylist[proxy] = 9999
                # print('Error')
        return False

    def update_day_files(self):
        soup = BeautifulSoup(self.page, "html.parser")
        day_file_list = [f['href'] for f in soup.select('a') if 'fb2' in f['href']]
        update = False
        for fn in day_file_list:
            print(fn, end=' > ')
            if not fn in self.filelist:
                if self.retrieve_file(fn):
                    logging.info('Download {} proxy {}'.format(fn, self.current_proxy))
                    update = True
                    print('Download')
                else:
                    logging.info('Not working proxy')
                    return
            else:
                print('Exist')
        if update:
            print('Update - Done')
            logging.info('Update - Done')
        else:
            print('Update nothing')
            logging.info('Update nothing')

    def retrieve_file(self, fn):
        while self.get_day_file(fn):
            if len(self.proxylist) == 1:
                return False
            del self.proxylist[self.current_proxy]
            self.current_proxy = list(self.proxylist.keys())[0]
            print('change proxy to {}'.format(self.current_proxy), end=' > ')
        return True

    def get_day_file(self, fn):
        try:
            print('retrieve file', end=' > ')
            proxy = urllib.request.ProxyHandler({'http': self.current_proxy})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
            tmp = urllib.request.urlretrieve(self.ulr_to_flibusta + fn, self.path_to_lib + '\\' + fn)
            return False
        except Exception as e:
            return True


def main():
    logging.info(' ====Start====')

    # получем и тестирует прокси
    proxy = Free_Proxys()
    proxy.run_test(process_count=25)

    # Обновление
    Flibusta_Day_Update(path_to_lib, proxy.pr_ping)

    logging.info(' ====Stop====')


def test_time():
    # получем и тестирует прокси

    proxy = Free_Proxys()
    for i in range(5, 50, 5):
        e = time.clock()
        proxy.run_test(process_count=i)
        print(i, time.clock() - e)


# 5 196.06496209699998
# 10 109.95311797199997
# 15 79.437627824
# 20 60.26124019299999
#                           !25 47.58588980500002! Оптимально
# 30 44.90855763400003
# 35 37.11979738100001
# 40 36.013118125000005
# 45 35.94224253300001


if __name__ == '__main__':
    main()
# test_time()
