# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 10:23:17 2020
"""

from selenium import webdriver
import time
from lxml import etree
import re
import csv
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# 登录微博
def get_login(browser, url, account, password):
    '''
    Parameters
    ----------
    url : 首页链接
    account : 账户（手机号）
    password : 密码
    '''
    browser.maximize_window()
    browser.get(url)
    time.sleep(1)
    input_count = browser.find_element_by_xpath('//*[@id="loginname"]')
    input_count.clear()# 清空搜索框
    input_count.send_keys(account)# 输入账号
    input_password = browser.find_element_by_xpath('//*[@type="password"]')
    input_password.clear()
    input_password.send_keys(password)# 输入密码
    
def get_title_urls(browser, page_url):
    '''
    Parameters
    ----------
    page_url : 每一页的链接
    Returns
    -------
    title_urls : 返回每一页所有微博（20条）的链接
    '''
    browser.get(page_url)
    time.sleep(5)
    html = etree.HTML(browser.page_source)  # 解析页面
    title_urls = html.xpath('//*[@id="pl_service_showcomplaint"]/table/tbody/tr/td[2]/div/a/@href')
    return title_urls
    
# 判断页面元素是否存在，这里是为了判断是否有"原文"字段
def element_judge(browser, xpath_path):
    try:
        element = browser.find_element_by_xpath(xpath_path)
    except:
        return False  # 发生异常，说明页面中未找到该元素，返回False
    else:
        return True   # 没有发生异常，表示在页面中找到了该元素，返回True
    
# 获取具体的微博内容
def title_content(page, browser, title_urls):
    '''
    Parameters
    ----------
    page : 当前爬取的页码
    title_urls : 当前页码内所有微博（20条）的链接
    Yields
    ------
    pre_results : 每条微博的详细信息
    '''
    n = len(title_urls)
    for order in range(0, n):
        title_url = 'https://service.account.weibo.com' + title_urls[order] 
        browser.get(title_url)
        time.sleep(2)
        html = etree.HTML(browser.page_source)
        # 判断原文是否已经删除
        text = element_judge(browser, '//*[@id="pl_service_common"]/div[4]/div[2]/div/div/div/div/p/a')
        # 获取具体微博信息
        if text:
            # 标题
            title = html.xpath('//*[@id="pl_service_common"]/div[1]/div[2]/h2/text()')
            # 举报人
            user_0 = html.xpath('//*[@id="pl_service_common"]/div[2]/div[1]/div/div[2]/div/p[1]/a[1]/text()')
            # 被举报人
            user_1 = html.xpath('//*[@id="pl_service_common"]/div[2]/div[2]/div/div[2]/p[1]/a[1]/text()')
            # 受理编号
            app_num = html.xpath('//*[@id="pl_content_backCount"]/div[1]/span[1]/text()')
            # 访问次数
            counter = html.xpath('//*[@id="pl_content_backCount"]/div[2]/span/text()')
            # 举报人数
            persons = html.xpath('//*[@id="pl_service_common"]/div[2]/div[1]/div/div[1]/span[2]/text()')
            # 发布日期
            datetime = html.xpath('//*[@id="pl_service_common"]/div[4]/div[2]/div/div/div/div/p/text()')
            # 举报人信用度
            jb_credict = html.xpath('//*[@id="pl_service_common"]/div[2]/div[1]/div/div[2]/div/p[1]/a[2]/img/@title')
            if len(jb_credict) == 0:
                jb_credict = html.xpath('//*[@id="pl_service_common"]/div[2]/div[1]/div/div[2]/div/p[1]/a[3]/img/@title')
            # 被举报人信用度
            bjb_credict = html.xpath('//*[@id="pl_service_common"]/div[2]/div[2]/div/div[2]/p[1]/a[3]/img/@title')
            if len(bjb_credict) == 0:
                bjb_credict = html.xpath('//*[@id="pl_service_common"]/div[2]/div[2]/div/div[2]/p[1]/a[2]/img/@title')
            # 点击原文
            browser.find_element_by_xpath('//*[@id="pl_service_common"]/div[4]/div[2]/div/div/div/div/p/a').click()
            windows = browser.current_window_handle #定位当前页面句柄
            all_handles = browser.window_handles   #获取全部页面句柄
            for handle in all_handles:          #遍历全部页面句柄
                if handle != windows:          #判断条件
                    browser.switch_to.window(handle)   #切换到新页面
            time.sleep(1)
            original_html = etree.HTML(browser.page_source)
            # 微博原文
            original_content = original_html.xpath('//div[@node-type="feed_list_content"]/text()')
            original_text = ''.join(original_content).replace('\u200b', '').replace(' ', '').replace('\xa0', '').replace('\n', '').replace('[', '').replace(']', '')
            # 点赞数
            good = original_html.xpath('//*[@class="WB_feed_handle"]/div/ul/li[4]/a/span/span/span/em[2]/text()')
            if len(good) == 0 or good[0] == '赞':
                good = [0]
            # 留言数
            message = original_html.xpath('//*[@class="WB_feed_handle"]/div/ul/li[3]/a/span/span/span/em[2]/text()')
            if len(message) == 0 or message[0] == '评论':
                message = [0]
            # 转发数
            share = original_html.xpath('//*[@class="WB_feed_handle"]/div/ul/li[2]/a/span/span/span/em[2]/text()')
            if len(share) == 0 or share[0] == '转发':
                share = [0]
            key = str(page) + '页-' + str(order+1) + '条'
            pre_results = [key
                           , title[0]
                           , user_0[0]
                           , user_1[0]
                           , app_num[0]
                           , re.search(r"\d+", counter[0]).group()
                           , re.search(r"\d+", persons[0]).group()
                           , re.search(r"\d\d\d\d-\d\d-\d\d", datetime[0]).group()
                           , jb_credict[0].replace('信用等级：','')
                           , bjb_credict[0].replace('信用等级：','')
                           , original_text
                           , good[0]
                           , message[0]
                           , share[0]]
    
            yield pre_results
            browser.close()
            browser.switch_to.window(all_handles[0])

# 主函数    
def main():
    
    with open('weibo.csv', 'a', encoding='gb18030', newline='') as f:
        writer = csv.writer(f)
        
        # 输入账号密码
        account = 'phone'
        password = 'password'
        
        home_url = 'https://service.account.weibo.com/'
        browser = webdriver.Chrome()
        try:
            wait = WebDriverWait(browser, 30) #显示等待30秒
            while True:
                get_login(browser, home_url, account, password)
                # 30秒内登录成功，开始爬取
                if wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR
                                                                , '.nav_title'), '举报处理大厅')):#(定位器，目标文本))
                    break
            # 设置爬取页码
            for page in range(200, 300):
                page_url = 'https://service.account.weibo.com/index?type=5&status=0&page={}'.format(page)
                title_urls = get_title_urls(browser, page_url)
                # 写入到csv文件
                for item in title_content(page, browser, title_urls):
                    writer.writerow(item)
                    print(item[0],'\033[42;1m Done!\033[0m')
        # 保证浏览器的最终关闭
        finally:
            browser.close()
            browser.quit()
    print('爬取完成！')
        
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
