# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 18:49:04 2019
@author: D-pc
"""
import requests
from urllib.parse import urlencode
import time
import os
from hashlib import md5
from multiprocessing.pool import Pool

def get_page(offset):
    headers = {
        'Host': 'www.toutiao.com',
        'Referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
        'cookie':('tt_webid=6741671832443717128; WEATHER_CITY=%E5%8C%97%E4%BA%AC; t'
                  't_webid=6741671832443717128; csrftoken=1018b5b3a9e73813c87e1a573a'
                  'c5a75d; __tasessionId=9ir94h1n11569683600848; s_v_web_id=b92036325'
                  'b7cbf7c94be40ea131a3bbb'),
        'user-agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.3'
                       '6 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'),
        'x-requested-with': 'XMLHttpRequest'
        }
    params = {'aid' : '24',
              'app_name' : 'web_search',
              'offset' : offset,
              'format' : 'json',
              'keyword' : '街拍',
              'autoload' : 'true',
              'count' : '20',
              'en_qc' : '1',
              'cur_tab' : '1',
              'from' : 'search_tab',
              'pd' : 'synthesis',
              'timestamp':'{}'.format(int(time.time()))
              }
    base_url = 'https://www.toutiao.com/api/search/content/?'
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(e.args)
        return None

def get_image(json):
    if json.get('data'):
        for item in json.get('data'):
            title = item.get('title')
            images = item.get('image_list')
            if images:# 去除空集
                for image in images:
                    yield {
                            'image':image.get('url'),
                            'title':title
                            }

def save_image(item):
    os.chdir('C:\code\spyder\爬虫\TouTiao_pictures')
    folder = item['title'].replace('|','').replace(':','').replace('?','').replace('*','').replace('<','').replace('>','')
    if not os.path.exists(folder):
        os.mkdir(folder)
    try:
        response = requests.get(item['image'])
        if response.status_code == 200:
            file = '{0}\{1}.{2}'.format(folder, md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file):
                with open(file, 'wb') as f:
                    f.write(response.content)
            else:
                return ('Already Download', file)
    except requests.ConnectionError:
        print('Failed to save image')
        
def main(offset):
    json = get_page(offset)
    for item in get_image(json):
        save_image(item)
    return 'Page {} Save Successful'.format(offset/20)
        

if __name__ == '__main__':
    print('Program Start')
#    offset = 10
#    main(offset)
    GROUP_START = 1
    GROUP_END = 5
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END+1)])
    results = pool.map(main, groups)
    for result in results:
        print(result)
    pool.close()
    pool.join()
    print('Program End')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        