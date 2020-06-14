# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 23:33:02 2019
@author: D-pc
"""

from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient as mg
import time

base_url = 'https://m.weibo.cn/api/container/getIndex?'
headers = {
        'Host': 'm.weibo.cn',
        'Referer': 'https://m.weibo.cn/u/2830678474',
        'user-agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.3'
                       '6 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'),
        'x-requested-with': 'XMLHttpRequest'
        }

def get_page(page):
    params = {
            'type': 'uid',
            'value': '2830678474',
            'containerid': '1076032830678474',
            'page': page
            }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers, timeout=(5,5))
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)

def parse_page(json):
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            weibo = {}
            weibo['id'] = item.get('id')
            weibo['text'] = pq(item.get('text')).text()
            weibo['attitudes'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reposts'] = item.get('reposts_count')
            yield weibo #类似return，不过在返回weibo后函数停止，下次调用时从上次停止的地方继续执行，直到结束

def main():
    client = mg()
    db = client['weibo']
    collection = db['weibo']
    page, n, k = 1, 0, 0
    while 348-n>0:
        time.sleep(1)
        json = get_page(page)
        results = parse_page(json)
        page += 1
        for i, result in enumerate(results):
            n += 1; k += 1 #n为每一页的微博序数；k为总的微博序数
            if collection.insert(result):
                print('The#{i}of page{page} / ${k}of348 Save to Mongo'.format(i=i, page=page, k=k))
            
if __name__ == '__main__':
    main()


























