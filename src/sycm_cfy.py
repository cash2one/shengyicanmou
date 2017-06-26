# coding:utf-8

'''
该脚本只针对 生意参谋-》市场-》商品店铺榜-》处方药
date: 2017-6-26
'''

import os
import time
import datetime
import pprint
import json
import re
import logging
import logging.config

from lxml import etree
import requests
from selenium import webdriver

from settings import LOGGING, HEADERS
from pipelines import SycmData
from utils import get_yesterday

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('myspider')

class Sycm(object):

    def __init__(self,  username, passwd):
        self.data_url = 'https://sycm.taobao.com/mq/industry/product/detail.htm'
        self.username = username
        self.passwd = passwd
        self.failed_count = 0
        self.db = SycmData()
        self.session = requests.Session()

        self._get_login_cookies()
        if self._check_login():            
            logger.debug('from cache...cookies...,login success')
            self.crawl_list_item_trend()
        else:
            # 防止cookie过期失效
            self.session.cookies.clear()
            self._login(username, passwd)
            self.crawl_list_item_trend()

    def _login(self, username, passwd):
        # url = 'https://sycm.taobao.com'
        login_url = 'https://login.taobao.com/member/login.jhtml?from=sycm&full_redirect=true&style=minisimple&minititle=&minipara=0,0,0&sub=true&redirect_url=http://sycm.taobao.com/'
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
        #import pdb
        #pdb.set_trace()

        # 如果该主机是第一次登录生意参谋，会要求进行短信验证，此时界面会触发其短信验证的弹窗：
        if re.findall(r'安全验证', driver.page_source):
            ## 这里需要解决短信验证的问题！！！
            logger.debug('*'*20 + '\033[92m 需进行短信验证,请注意，如果长时间不验证，会跳转到本次请求已超时的页面,此时再验证会一直停留在该界面 \033[0m')
        elif re.findall(r'滑块验证码', driver.page_source):
            ## 这里需要解决滑块验证的问题！！！
            logger.debug('*'*20 + '\033[92m 需进行滑块验证 \033[0m')
        
        if self._check_login():
            logger.debug("login success")
        cookies = driver.get_cookies()
        login_cookies = {item["name"] : item["value"] for item in cookies}
        self._save_login_cookies(login_cookies)

        return login_cookies
        
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
        res = self.session.get(self.data_url, headers=HEADERS, verify=False)
        text = res.text
        login_key = re.findall(r'title="登出"', text)
        if login_key:
            return True
        else:
            return False
          
    def get_list_item_total_page(self):
        list_items_url = 'https://sycm.taobao.com/mq/rank/listItems.json?cateId=122966004&categoryId=122966004&dateRange={yesterday}%7C{yesterday}&dateRangePre={yesterday}|{yesterday}&dateType=recent1&dateTypePre=recent1&device=0&devicePre=0&itemDetailType=1&keyword=&orderDirection=desc&orderField=payOrdCnt&page=1&pageSize=100&rankTabIndex=0&rankType=1&seller=-1&token=aa970f317&view=rank&_=1498206609142'\
                .format(yesterday=get_yesterday())
        res = self.session.get(url=list_items_url, headers=HEADERS, verify=False)
        list_items = json.loads(res.text)
        total_items_count = list_items['content']['data']['recordCount']
        total_page = int(total_items_count/100)
        return total_page

    def crawl_list_item_trend(self):
        '''
        抓取 市场->市场店铺榜->查看详情->商品趋势->处方药 数据
            处方药的cateId: 122966004
            所有终端-支付子订单数  "payOrdCntList"
            所有终端-支付转化率指数  "payByrRateIndexList"
            所有终端-支付件数  "payItemQtyList"
        '''
        total_page = self.get_list_item_total_page()
        item_list = []
        for page in range(1, total_page+1):
            logger.debug('共{}页，开始获取第{}页数据'.format(total_page, page)+'-'*20)
            list_items_url = 'https://sycm.taobao.com/mq/rank/listItems.json?cateId=122966004&categoryId=122966004&dateRange={yesterday}%7C{yesterday}&dateRangePre={yesterday}|{yesterday}&dateType=recent1&dateTypePre=recent1&device=0&devicePre=0&itemDetailType=1&keyword=&orderDirection=desc&orderField=payOrdCnt&page={page}&pageSize=100&rankTabIndex=0&rankType=1&seller=-1&token=aa970f317&view=rank&_=1498206609142'\
                            .format(yesterday=get_yesterday(), page=page)
            res = self.session.get(url=list_items_url, headers=HEADERS, verify=False)
            list_items = json.loads(res.text)
            if list_items['content']['message'] == "操作成功":
                logger.debug('\033[94m 获取商品店铺排行榜表格数据成功 \033[0m')
                total_items_count = list_items['content']['data']['recordCount']
                total_items_data = list_items['content']['data']['data']
                # 商品分类
                item_category = u'处方药'
                # 商品分类id
                item_category_id = '122966004'
                try:
                    for item in total_items_data:
                        #item keys: ['payByrRateIndex', 'mallItem', 'itemUrl', 'itemPicUrl', 'sameGoodUrl', 'itemPrice', 'payOrdCnt', 'itemId', 'shopUrl', 'pvIndex', 'shopName', 'tradeIndexCrc', 'searchIndex', 'orderNum', 'itemTitle']
                        # 店名
                        shop_name = item['shopName']
                        # 产品名
                        item_title = item['itemTitle']
                        # 产品id
                        item_id = item['itemId']
                        # 产品价格
                        item_price = item['itemPrice']
                        # 产品url
                        item_url = 'https:' + item['itemUrl'] 

                        # 构造 商品趋势的折线图 的URL
                        item_trend_url = 'https://sycm.taobao.com/mq/rank/listItemTrend.json?cateId=122966004&categoryId=122966004&dateRange={yesterday}%7C{yesterday}&dateRangePre={yesterday}|{yesterday}&dateType=recent1&dateTypePre=recent1&device=0&devicePre=0&indexes=payOrdCnt,payByrRateIndex,payItemQty&itemDetailType=1&itemId={item_id}&latitude=undefined&rankTabIndex=0&rankType=1&seller=-1&token=aa970f317&view=detail'\
                                        .format(yesterday=get_yesterday(), item_id=item_id)
                        trend_res = self.session.get(url=item_trend_url, headers=HEADERS, verify=False)
                        trend_items = json.loads(trend_res.text)
                        if trend_items['content']['message'] == "操作成功":
                            logger.debug('\033[94m 获取商品趋势数据成功 \033[0m')
                            pay_item_qtylist = trend_items['content']['data']['payItemQtyList']
                            pay_ord_cntlist = trend_items['content']['data']['payOrdCntList']
                            pay_byr_rate_index_list = trend_items['content']['data']['payByrRateIndexList']
                            logger.debug('产品：{}, 所有终端-支付子订单数:{}, 所有终端-支付转化率指数:{}, 所有终端-支付件数:{}'
                                        .format(item_title, pay_ord_cntlist, pay_byr_rate_index_list, pay_item_qtylist))
                            item_info = {
                                    'shop_name': shop_name,
                                    'item_category': item_category,
                                    'item_category_id': item_category_id,
                                    'item_title': item_title,
                                    'item_id': item_id,
                                    'item_price': item_price,
                                    'item_url': item_url,
                                    'pay_item_qtylist': pay_item_qtylist,
                                    'pay_ord_cntlist': pay_ord_cntlist,
                                    'pay_byr_rate_index_list': pay_byr_rate_index_list,
                                    }
                            item_list.append(item_info)
                        else:
                            logger.debug('\033[94m 获取商品趋势数据失败{} \033[0m'.format(trend_items['content']['message']))
                    self.db.save_list_item_trend(item_list)
                except Exception as e:
                    logger.error('\033[94m :爬取第{page}页时报错: \033[0m'.format(page=page))
                    logger.error(e)
            else:
                ### 这里可做发送邮件通知
                logger.error('\033[94m :爬取第{page}页数据失败 \033[0m'.format(page=page))


if __name__ == '__main__':
    username = '健客大药房旗舰店:运营04'
    passwd = 'cfyyy_04'
    sycm = Sycm(username, passwd)

