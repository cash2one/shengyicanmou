# coding:utf-8

'''
该脚本只针对 生意参谋-》市场-》产品分析(所有商品作三级目录分类，全部爬取)
date: 2017-7-14
'''

import os
import time
import urllib
import json
import re

from lxml import etree
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from settings import logger, HEADERS
from pipelines import SycmData
from utils import get_lastday
from models import IndustryCategory, IndustryThirdCategory

class Sycm(object):

    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.db = SycmData()
        self.session = requests.Session()
        self._get_login_cookies()
        if self._check_login():
            logger.debug('from cache...cookies...,login success')
            #self.crawl_industry_category()
            self.crawl_industry_info()
        else:
            # 防止cookie过期失效
            self.session.cookies.clear()
            self._login()
            #self.crawl_industry_category()
            self.crawl_industry_info()

    def _login(self, callback=False):
        # url = 'https://sycm.taobao.com'
        login_url = 'https://login.taobao.com/member/login.jhtml?from=sycm&full_redirect=true&style=minisimple&minititle=&minipara=0,0,0&sub=true&redirect_url=http://sycm.taobao.com/'
        #driver = webdriver.Chrome(
        #    executable_path="E:/Program Files (x86)/chromedriver"
        #    # executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver"
        #    )
        driver = webdriver.PhantomJS()
        driver.maximize_window()
        driver.get(login_url)
        logger.debug("start login")
        username_field  = driver.find_element_by_id("TPL_username_1")
        username_field.send_keys(self.username)
        passwd_field = driver.find_element_by_id("TPL_password_1")
        passwd_field.send_keys(self.passwd)
        login_button = driver.find_element_by_id("J_SubmitStatic")
        login_button.click()
        time.sleep(20)

        # 如果该主机是第一次登录生意参谋，会要求进行短信验证，此时界面会触发其短信验证的弹窗：
        if re.findall(r'安全验证', driver.page_source):
            ## 这里需要解决短信验证的问题！！！
            logger.debug('*'*20 + '\033[92m 需进行短信验证,请注意，如果长时间不验证，\
                会跳转到本次请求已超时的页面,此时再验证会一直停留在该界面 \033[0m')
        elif re.findall(r'滑块验证码', driver.page_source):
            ## 这里需要解决滑块验证的问题！！！
            logger.debug('*'*20 + '\033[92m 需进行滑块验证 \033[0m')

        if self._check_login():
            logger.debug("login success")
        cookies = driver.get_cookies()
        login_cookies = {item["name"] : item["value"] for item in cookies}
        self._save_login_cookies(login_cookies)
        if callback:
            self.crawl_industry_category()
        return driver

    def _save_login_cookies(self, login_cookies):
        if not isinstance(login_cookies, dict):
            logger.debug('The cookies must be dict type')
            return
        with open("login_cookies.json", "w") as f:
            json.dump(login_cookies, f)
        self.session.cookies.update(login_cookies)

    def _get_login_cookies(self):
        """从文本中获得cookies
        """
        with open("login_cookies.json") as f:
            cookies = json.load(f)
            self.session.cookies.update(cookies)
        return cookies

    def _check_login(self):
        """验证是否登陆成功
        Returns:
            Boolean: 是否登陆成功
        """
        data_url = 'https://sycm.taobao.com/mq/industry/product/detail.htm?spm=a21ag.7782686.0.0.c8PRca#/?brandId=3228590&cateId=50023717&dateRange=2017-06-21%7C2017-06-21&dateType=recent1&device=0&modelId=277847275&seller=-1&spuId=277847275'
        res = self.session.get(data_url, headers=HEADERS, verify=False)
        text = res.text
        login_key = re.findall(r'title="登出"', text)
        if login_key:
            return True
        else:
            return False

    def crawl_industry_category(self):
        '''
        抓取 市场->产品分析 表格数据
        获取产品名：cate_name 和 产品ID：cate_id
        '''
        category_url = 'https://sycm.taobao.com/mq/common/category.json?edition=2&statDate={yesterday}'.format(yesterday=get_lastday())
        res = self.session.get(category_url, headers=HEADERS, verify=False)
        page_source = res.content
        try:
            #import pdb
            #pdb.set_trace()
            info = json.loads(page_source)
        except Exception as e:
            info = json.loads(page_source.decode('utf-8'))
            if info.get('code') == 5810: self._login(callback=True)
        data = info['content']['data']  # len(data)=290
        item_list = []
        for item in data:
            if item[1]:  #排除写入一级目录
                if item[1] == item[-1]:
                    # 此时该目录是二级目录
                    second_cate_id = item[0]
                    second_cate_name = item[2]
                    cate_id = item[-1]
                    third_cate_id = second_cate_id
                    third_cate_name = '无三级目录'
                else:
                    #此时该目录是三级目录
                    second_cate_id = item[1]
                    second_cate_name = None
                    third_cate_id = item[0]
                    third_cate_name = item[2]
                    cate_id = item[-1]
                item_list.append({
                    'second_cate_id': second_cate_id,
                    'second_cate_name': second_cate_name,
                    'third_cate_id': third_cate_id,
                    'third_cate_name': third_cate_name,
                    'cate_id': cate_id,
                })
                logger.debug('\033[95m 三级目录总:{}量 \033[0m'.format(len(item_list)))
        self.db.save_category(item_list)

    def crawl_industry_info(self, driver=None):
        '''
        获取二级（没有三级目录时）或三级目录下的商品详情
        '''
        #获取没有三级目录的二级目录的cate_id
        # second_categorys = IndustryCategory.raw('select cate_id from industry_category where count_third >0')
        # second_cate_ids = IndustryCategory.select(IndustryCategory.cate_id).where(IndustryCategory.count_third >0)
        cate_id_list = IndustryThirdCategory.select(IndustryThirdCategory.third_cate_id)
        length = cate_id_list.count()
        try:
            for num in range(length):
                item_list = []
                cate_id = cate_id_list[num].third_cate_id
                url = 'https://sycm.taobao.com/mq/industry/product/product_rank/getRankList.json?cateId={cate_id}&dateRange={lastday}%7C{yesterday}&dateType=recent7&device=0&seller=-1'\
                    .format(cate_id=cate_id, lastday=get_lastday(day=7), yesterday=get_lastday())
                res = self.session.get(url, headers=HEADERS, verify=False)
                res = json.loads(res.text)
                if res.get('rgv587_flag0') == 'sm':
                    import pdb
                    pdb.set_trace()
                    logger.debug('\033[92m 需进行图片验证 !!\033[0m')
                    verify_url=res['url']+'&style=mini'
                    verify_res = self.session.get(verify_url, headers=HEADERS, verify=False)
                    html = etree.HTML(verify_res.text)
                    text = html.xpath('//script')[4].text
                    text = text.replace('\n', '').replace('\t','').replace('  ','').replace(' ','')
                    query_string = re.findall(r'data:{(.*)},', text)[0].replace("'", '')
                    #driver = self._login()
                    query_params = {}
                    for key in query_string.split(','):
                        query_params[key.split(':')[0]] = key.split(':')[1]
                    #此时有三个参数要重写：smReturn, ua, code
                    query_params['smReturn'] = url
                    #尝试任意给定 code (图片验证码中的任意一个)
                    query_params['code'] = 'nffa'
                    query_params['ua'] = ''
                    query_url = 'https://sec.taobao.com/query.htm?' + urllib.parse.urlencode(query_params)
                    self.session.get(query_url, headers=HEADERS, verify=False)
                    return

                try:
                    items = res['content']['data']
                except Exception as e:
                    logger.error('\033[92m {}报错:{}\033[0m'.format(url, e))
                    continue
                for data in items:
                    model_id = data['modelId']
                    model_name = data['modelName']
                    trade_index = data['tradeIndex']
                    pay_item_qty = data['payItemQty']
                    brand_id = data['brandId']
                    brand_name = data['brandName']
                    rank_id = data['rankId']
                    item_list.append({
                        'cate_id': cate_id,
                        'model_id': model_id,
                        'model_name': model_name,
                        'trade_index': trade_index,
                        'pay_item_qty': pay_item_qty,
                        'brand_id': brand_id,
                        'brand_name': brand_name,
                        'rank_id': rank_id,
                    })
                logger.debug('\033[95m URL:{}, 数据总量:{} \033[0m'
                        .format(url, len(item_list)))
                self.db.save_industrys(item_list)
        except Exception as e:
            logger.error('\033[92m {} \033[0m'.format(e))


if __name__ == '__main__':
    username = '健客大药房旗舰店:运营04'
    passwd = 'cfyyy_04'
    sycm = Sycm(username, passwd)

