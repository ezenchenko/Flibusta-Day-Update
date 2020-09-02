# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import urllib.request
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup
from pythonping import ping

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
                update = True
                print('Download')
            else:
                print('Exist')
        if update:
            print('Update - Done')
        else:
            print('Update nothing')

    def get_day_file(self, fn):
        # print('download file {}'.format(fn), end=' ')
        # create the object, assign it to a variable
        proxy = urllib.request.ProxyHandler({'http': self.current_proxy})
        # construct a new opener using your proxy settings
        opener = urllib.request.build_opener(proxy)
        # install the openen on the module-level
        urllib.request.install_opener(opener)
        # make a request
        urllib.request.urlretrieve(self.ulr_to_flibusta + fn, self.path_to_lib + '\\' + fn)
        # print('Done.')


def main():
    proxy = Free_Proxys()
    proxy.run_test()
    # print(proxy.pr_ping)
    # pr = [('51.68.71.95:3128', 65.08),
    #      ('205.185.127.8:8080', 182.41), ('181.129.198.196:999', 185.24), ('202.148.20.4:8080', 195.98),
    #      ('61.8.78.130:8080', 197.47), ('101.255.103.201:53281', 206.15), ('103.209.230.129:8080', 240.68),
    #      ('103.143.84.72:8080', 245.2), ('203.176.129.69:8080', 247.24), ('170.79.95.204:8080', 272.81),
    #      ('177.43.217.74:8080', 281.59), ('36.73.72.47:8080', 314.46), ('181.209.82.154:23500', 326.15),
    #      ('114.5.97.138:8080', 686.55), ('131.161.254.150:3128', 705.78), ('209.190.32.28:3128', 1105.64),
    #      ('200.60.79.11:53281', 2000.0), ('52.251.47.125:3128', 2000.0)]
    FDU = Flibusta_Day_Update(r'e:\flibusta\_LIB.RUS.EC\librusec', proxy.pr_ping)


if __name__ == '__main__':
    main()
