# This is a sample Python script.

import logging
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import urllib.request
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup
from pythonping import ping

path_file_log = "e:\\flibusta\\Update.log"  # Файл лога
path_to_lib = r'e:\flibusta\_LIB.RUS.EC\librusec'

logging.basicConfig(filename=path_file_log, format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

pr_ping = {}


def test_proxy(proxy):
    print(proxy)
    p = ping(proxy.split(':')[0]).rtt_avg_ms
    return (proxy, p)


class Free_Proxys(object):
    def __init__(self):
        self.pr_ping = {}
        self.proxy_list = []
        self.get_proxy_list()
        print(len(self.proxy_list))
        # self.run_test()

    def get_proxy_list(self):
        urllib.request.urlretrieve('http://spys.me/proxy.txt', r'e:\temp\proxy.txt')
        with open(r'e:\temp\proxy.txt', 'r') as f:
            lines = [line.strip() for line in f]
        self.proxy_list = [line.split() for line in lines[9:-2] if not 'RU' in line]
        self.proxy_list = [ip for proxy in self.proxy_list for ip in proxy if ':' in ip]
        self.pr_ping = {proxy: 0 for proxy in self.proxy_list}

    def run_test(self):
        with Pool(processes=30) as pool:
            self.pr_ping = dict(list(pool.map(test_proxy, self.pr_ping.copy())))
        self.pr_ping = sorted(self.pr_ping.items(), key=lambda pr: pr[1])


class Flibusta_Day_Update(object):
    def __init__(self, path_to_lib, proxylist):
        self.path_to_lib = path_to_lib

        # self.filelist = [os.path.join(r, fn) for r, d, f in os.walk(path_to_lib) for fn in f[:] if '.zip' in fn]

        self.filelist = [fn for r, d, f in os.walk(path_to_lib) for fn in f[:] if '.zip' in fn]
        self.proxylist = proxylist
        self.ulr_to_flibusta = 'http://flibusta.is/daily/'
        self.page = ''
        self.current_proxy = ''
        if not self.test_get_page():
            print('error. Not load page!')
        else:
            self.update_day_files()

    def get_page(self, proxy_test):
        proxy, time = proxy_test
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

    def test_get_page(self):
        for proxy in self.proxylist:
            print(proxy, end=' > ')
            if self.get_page(proxy):
                print('Pass')
                logging.info('proxy {}'.format(self.current_proxy))
                return True
            else:
                print('Error')
        return False

    def update_day_files(self):
        soup = BeautifulSoup(self.page, "html.parser")
        day_file_list = [f['href'] for f in soup.select('a') if 'fb2' in f['href']]
        update = False
        for fn in day_file_list:
            print(fn, end=' > ')
            if not fn in self.filelist:
                self.get_day_file(fn)
                logging.info('Download {} proxy {}'.format(fn, self.current_proxy))
                update = True
                print('Download')
            else:
                print('Exist')
        if update:
            print('Update - Done')
            logging.info('Update - Done')
        else:
            print('Update nothing')
            logging.info('Update nothing')

    def get_day_file(self, fn):
        proxy = urllib.request.ProxyHandler({'http': self.current_proxy})
        opener = urllib.request.build_opener(proxy)
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(self.ulr_to_flibusta + fn, self.path_to_lib + '\\' + fn)


def main():
    logging.info(' ====Start====')

    # получем и тестирует прокси
    proxy = Free_Proxys()
    proxy.run_test()

    # Обновление
    FDU = Flibusta_Day_Update(path_to_lib, proxy.pr_ping)

    logging.info(' ====Stop====')


if __name__ == '__main__':
    main()
