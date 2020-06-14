# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 20:08:14 2019
@author: D-pc
"""

import requests
import re
import os
import json
import time
import csv
from pyquery import PyQuery as pq

# 获取网页
def get_page(url):
    headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.'
            '36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
            }
    response = requests.get(url, headers=headers, timeout=(5, 10))
    if response.status_code == 200:
        return response.text
    else:
        return None
    
def main():
    url = 'https://www.zhihu.com/explore'
    html = get_page(url)
    doc = pq(html)
    items = doc('.ExploreHomePage-specials .ExploreHomePage-specialCard').items()
    for item in items:
        title = item.find('.ExploreSpecialCard-title').text().replace('\n', '')
        count = item.find('.ExploreSpecialCard-count').text().replace('\n', '')
        content_list = item.find('.ExploreSpecialCard-contentList').text()
#        print(title, count, content_list, sep='\n')
        print('开始写入')
#        with open('explore.txt', 'w', encoding='utf-8') as f:
#            f.write('\n'.join([title, count, content_list]))
#            f.write('\n' + '='*80 + '\n')
        with open('data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([title, count, content_list])


if __name__ == '__main__':
    main()
    print('Done')
