# coding:utf-8

import os
import logging
import logging.config
import time
import pprint
import json
import re

from lxml import etree
import requests
from selenium import webdriver

from settings import LOGGING, HEADERS
from pipelines import Sycm

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('myspider')

class Sycm(object):

    def __init__(self,  username, passwd):
        self.data_url = 'https://sycm.taobao.com/mq/industry/product/detail.htm?spm=a21ag.7782686.0.0.c8PRca#/?brandId=3228590&cateId=50023717&dateRange=2017-06-21%7C2017-06-21&dateType=recent1&device=0&modelId=277847275&seller=-1&spuId=277847275'
        self.username = username
        self.passwd = passwd
        self.db = Sycm()
        self.session = requests.Session()
        # self._login(username, passwd)

        self._get_login_cookies()
        if self._check_login():            
            logger.debug('from cache...cookies...,login success')
            # self.crawl_industry_data()
            self.crawl_list_item_trend()
        else:
            # 防止cookie过期失效
            self.session.cookies.clear()
            self._login(username, passwd)
            self.crawl_list_item_trend()

    def _login(self, username, passwd):
        # url = 'https://sycm.taobao.com'
        login_url = 'https://login.taobao.com/member/login.jhtml?from=sycm&full_redirect=true&style=minisimple&minititle=&minipara=0,0,0&sub=true&redirect_url=http://sycm.taobao.com/'
        # driver = webdriver.Chrome(
        #     executable_path="E:/Program Files (x86)/chromedriver"
        #     # executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver"
        #     )
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
        
        cookies = driver.get_cookies()
        login_cookies = {item["name"] : item["value"] for item in cookies}
        self._save_login_cookies(login_cookies)
        logger.debug("login success")

        # 点击市场
        self.crawl_industry_data(driver=driver)
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
    
    def analysis_industry_html(self, page_source):
        html = etree.HTML(page_source)
        #获取表格数据 
        table = html.xpath('//div[@class="list-table-container"]/table')[0]
        # # 表头: 排名 产品名称 交易指数 支付件数 操作
        # threads = table.xpath('./thead/tr/th')
        # # thread_length = len(thread)
        # th_text = []
        # for th in threads:
        #     th_text.append(th.xpath('./div/span/text()')[0])
        # logger.debug(th_text)
        # 表体
        tbodys = table.xpath('./tbody/tr')
        # tbody_length = len(tbody)
        td_text = []
        for tr in tbodys:
            
            # tds = tr.xpath('./td')
            # td_length = len(tds)
            # 排名
            ranking = tr.xpath('./td[1]/text()')[0]
            # 产品名称 
            product = ''.join(tr.xpath('./td[2]/a/span/text()'))
            # 交易指数 
            sale_index = tr.xpath('./td[3]/text()')[0]
            # 支付件数 
            sales = tr.xpath('./td[4]/text()')[0]
            # 操作
            operation = ''.join(tr.xpath('./td[5]/div/a/text()'))
            logger.debug('排名：{}，产品名称：{}， 交易指数：{}， 支付件数：{}， 操作：{}'
                        .format(ranking, product, sale_index, sales, operation))
            product_info = {
                'rangking':ranking,
                'product': product,
                'sale_index': sale_index,
                'sales': sales,
                'operation':  operation
            }
            td_text.append(product_info)
        self.db.save_industry_product(td_text)
        

    def get_industry_total_pages(self, driver):
        per_100_first_url = 'https://sycm.taobao.com/mq/industry/product/rank.htm?spm=a21ag.7782695.LeftMenu.d320.mfz2ZP&page=1&pageSize=50#/?cateId=50023717&dateRange=2017-06-22%7C2017-06-22&dateType=recent1&device=0&orderBy=tradeIndex&orderType=desc&page=1&pageSize=100&seller=-1'
        driver.get(per_100_first_url)
        time.sleep(5)

        page_source = driver.page_source.encode('utf-8')
        html = etree.HTML(page_source)
        #获取总页数
        total_page = html.xpath('//span[@class="ui-pagination-total"]/text()')
        total_page = int(total_page[1])
        logger.debug('产品分析页数据总页数:{}'.format(total_page))
        return total_page

    def crawl_industry_data(self, driver=None):
        '''
        抓取 市场->产品分析 表格数据
        '''
        product_url = 'https://sycm.taobao.com/mq/industry/product/rank.htm'
        if driver:
            driver.get(product_url)
        else:
            # driver = webdriver.Chrome(
            #     executable_path="E:/Program Files (x86)/chromedriver"
            #     # executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver"
            # )
            driver = webdriver.PhantomJS()
            driver.maximize_window()
            driver.get(product_url)
            driver.add_cookie(self._get_login_cookies())    # 增加保存到本地的cookies，实现带cookies登录
            
        time.sleep(10)
        # import pdb
        # pdb.set_trace()
        total_page = self.get_industry_total_pages(driver) + 1
        for page in range(1, total_page):
            per_100_url = 'https://sycm.taobao.com/mq/industry/product/rank.htm?spm=a21ag.7782695.LeftMenu.d320.mfz2ZP&page=1&pageSize=50#/?cateId=50023717&dateRange=2017-06-22%7C2017-06-22&dateType=recent1&device=0&orderBy=tradeIndex&orderType=desc&page={}&pageSize=100&seller=-1'\
                        .format(page)
            driver.get(per_100_url)
            page_source = driver.page_source.encode('utf-8')
            logger.debug('开始获取第{}页数据'.format(page)+'-'*20)
            self.analysis_industry_html(page_source)
          
    def get_list_item_total_page(self):
        list_items_url = 'https://sycm.taobao.com/mq/rank/listItems.json?cateId=50023717&categoryId=50023717&dateRange=2017-06-22%7C2017-06-22&dateRangePre=2017-06-22|2017-06-22&dateType=recent1&dateTypePre=recent1&device=0&devicePre=0&itemDetailType=1&keyword=&orderDirection=desc&orderField=payOrdCnt&page=1&pageSize=100&rankTabIndex=0&rankType=1&seller=-1&token=aa970f317&view=rank&_=1498206609142'
        res = self.session.get(url=list_items_url, headers=HEADERS, verify=False)
        list_items = json.loads(res.text)
        total_items_count = list_items['content']['data']['recordCount']
        total_page = int(total_items_count/100)
        return total_page

    def crawl_list_item_trend(self):
        '''
        抓取 市场->市场店铺榜->查看详情->商品趋势 数据
            所有终端-支付子订单数  "payOrdCntList"
            所有终端-支付转化率指数  "payByrRateIndexList"
            所有终端-支付件数  "payItemQtyList"
        '''
        # import pdb
        # pdb.set_trace()
        # 获得 商品信息(itemTitle)、商品id(itemId)
        total_page = self.get_list_item_total_page()+1
        for page in range(1, total_page):
            logger.debug('开始获取第{}页数据'.format(page)+'-'*20)
            list_items_url = 'https://sycm.taobao.com/mq/rank/listItems.json?cateId=50023717&categoryId=50023717&dateRange=2017-06-22%7C2017-06-22&dateRangePre=2017-06-22|2017-06-22&dateType=recent1&dateTypePre=recent1&device=0&devicePre=0&itemDetailType=1&keyword=&orderDirection=desc&orderField=payOrdCnt&page={page}&pageSize=100&rankTabIndex=0&rankType=1&seller=-1&token=aa970f317&view=rank&_=1498206609142'\
                            .format(page=page)
            res = self.session.get(url=list_items_url, headers=HEADERS, verify=False)
            list_items = json.loads(res.text)
            total_items_count = list_items['content']['data']['recordCount']
            total_items_data = list_items['content']['data']['data']
            for item in total_items_data:
                #item keys: ['payByrRateIndex', 'mallItem', 'itemUrl', 'itemPicUrl', 'sameGoodUrl', 'itemPrice', 'payOrdCnt', 'itemId', 'shopUrl', 'pvIndex', 'shopName', 'tradeIndexCrc', 'searchIndex', 'orderNum', 'itemTitle']
                item_title = item['itemTitle']
                item_id = item['itemId']
                # 构造 商品趋势的折线图 的URL
                item_tred_url = 'https://sycm.taobao.com/mq/rank/listItemTrend.json?cateId=50023717&categoryId=50023717&dateRange=2017-06-22%7C2017-06-22&dateRangePre=2017-06-22|2017-06-22&dateType=recent1&dateTypePre=recent1&device=0&devicePre=0&indexes=payOrdCnt,payByrRateIndex,payItemQty&itemDetailType=1&itemId={item_id}&latitude=undefined&rankTabIndex=0&rankType=1&seller=-1&token=aa970f317&view=detail'\
                                .format(item_id=item_id)
                tred_res = self.session.get(url=item_tred_url, headers=HEADERS, verify=False)
                tred_items = json.loads(tred_res.text)
                pay_item_qtylist = tred_items['content']['data']['payItemQtyList']
                pay_ord_cntlist = tred_items['content']['data']['payOrdCntList']
                pay_byr_rate_index_list = tred_items['content']['data']['payByrRateIndexList']
                logger.debug('产品：{}, 所有终端-支付子订单数:{}, 所有终端-支付转化率指数:{}, 所有终端-支付件数:{}'
                            .format(item_title, pay_ord_cntlist, pay_byr_rate_index_list, pay_item_qtylist))
           

if __name__ == '__main__':
    username = '健客大药房旗舰店:运营04'
    passwd = 'cfyyy_04'
    sycm = Sycm(username, passwd)

