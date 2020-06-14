# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 16:13:33 2019
@author: D-pc
"""

import requests
import re
import os
import json
import time

# 获取网页
def get_page(url):
    headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.'
            '36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
            }
    response = requests.get(url, headers=headers, timeout=(5, 10))
    if response.status_code == 200:
        return response.content
    else:
        return None

# 解析网页，获取详细信息
def parse_page(page_html):
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.'
                         '*?data-src="(.*?)".*?name.*?<a'
                         '.*?>(.*?)</a>.*?class="star".*?>(.*?)</p>'
                         '.*?releasetime.*?>(.*?)</p>.*?score.*?<i.*?>(.*?)</i>'
                         '.*?fraction.*?>(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, page_html)
#    print(items)
    for item in items:
        yield{
                '排名-index':item[0],
                '封面-image':item[1],
                '标题-title':item[2],
                '演员-actor':item[3],
                '时间-time':item[4],
                '评分-score':item[5]+item[6]}

# 保存信息到txt，以及封面
def save_file(path, content):
    path_txt = os.path.join(path, 'MaoYan.txt')
    path_image = os.path.join(path, 'Image')
    with open(path_txt, 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False)+'\n')
    if not os.path.exists(path_image):# 创建保存封面的文件夹
        os.mkdir(path_image)
    os.chdir(path_image)# 切换到封面文件夹路径
    with open(content['排名-index']+'-'+content['标题-title']+'.jpg', 'wb') as f:
        f.write(get_page(content['封面-image']))
    
# 主函数
def main():
    path = os.getcwd()# 获取当前py文件的路径
    for page_index in range(20):
        os.chdir(path)
        offset = 'offset='+str(page_index * 10)
        url = 'https://maoyan.com/board/4?'+offset
        html = get_page(url).decode('utf-8')
        print('开始解析网页:第{}页'.format(page_index+1))
        for item in parse_page(html.replace('\n', '').replace(' ', '')):
            save_file(path, item)
            os.chdir(path)
        time.sleep(1)
        
if __name__ == '__main__':
    main()
    print('Done')
        
        
        
        
        
        
        
        
