#!/usr/bin/env python
#coding:utf-8


from bs4 import BeautifulSoup
from selenium import webdriver
import sys
import requests
import multiprocessing
from terminaltables import DoubleTable

__author__ = 'songjim'

'''
获取电影的磁力链接
资源网站：
    飘花
    1、http://www.piaohua.com/
    电影天堂
    2、http://www.dytt8.net/index2.htm
    LOL电影天堂
    3、http://www.loldytt.com/
    最后就偷懒完成了LOL电影天堂的
'''


def detail_search(target_list=[]):
    if len(target_list) == 0:
        return []
    target_return = []
    for target in target_list:
        res = requests.get(target['url'])
        bs = BeautifulSoup(res.content, 'html.parser')
        t_dom = bs.find('ul', class_='downurl')
        sec_return = []
        for tt in t_dom.find_all('a'):
            sec_return.append({'BT_url': tt.get('href'), 'BT_title': tt.get_text()})
        target_return.append({'title': target['content'], 'data': sec_return})
    return target_return

if __name__ == '__main__':
    driver = webdriver.PhantomJS()
    driver.get('http://www.loldytt.com')
    movie_name = sys.argv[1].decode('utf8')
    driver.find_element_by_name("keyword").clear()
    driver.find_element_by_name("keyword").send_keys(movie_name)
    driver.find_element_by_class_name("submit").click()
    tab_list = driver.window_handles
    driver.switch_to.window(tab_list[1])
    html = BeautifulSoup(driver.page_source, 'html.parser')
    html_dom = html.find('div', class_='solb')
    detail_list = []
    for item in html_dom.find_all('ol'):
        detail_list.append({'url': item.a.get('href'), 'content': item.a.get_text()})
    driver.quit()
    if len(detail_list) == 0:
        sys.exit('😁😁😂😂没有查到相关电影😁😁😂😂')
    #开始详情查询
    cpus = multiprocessing.cpu_count()
    target_idx = len(detail_list)/cpus
    pool = multiprocessing.Pool()
    proc_list = 0
    results = []
    for i in xrange(0, cpus):
        if i == (cpus-1):
            result = pool.apply_async(detail_search, args=(detail_list[proc_list:],))
        else:
            result = pool.apply_async(detail_search, args=(detail_list[proc_list: proc_list + target_idx],))
        proc_list += target_idx
        results.append(result)
    pool.close()
    pool.join()
    out_list = []
    for result in results:
        out_list += result.get()

    for ii in out_list:
        table_d = [['title', 'url']]
        for iii in ii['data']:
            table_d.append([iii['BT_title'], iii['BT_url']])
        table = DoubleTable(table_d)
        table.title = ii['title']
        print table.table

