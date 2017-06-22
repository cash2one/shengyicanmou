# coding:utf-8

import os
import logging
import logging.config
import time
import pprint
import json
import re

import requests
from selenium import webdriver

from settings import LOGGING, HEADERS

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('myspider')

class Sycm(object):
    def __init__(self,  username, passwd):
        self.data_url = 'https://sycm.taobao.com/mq/industry/product/detail.htm?spm=a21ag.7782686.0.0.c8PRca#/?brandId=3228590&cateId=50023717&dateRange=2017-06-21%7C2017-06-21&dateType=recent1&device=0&modelId=277847275&seller=-1&spuId=277847275'
        self.username = username
        self.passwd = passwd
        self.session = requests.Session()
        # self._login(username, passwd)

        self._get_login_cookies()
        if self._check_login():            
            logger.debug('from cache...cookies...,login success')
            self.crawl_data()
        else:
            # 防止cookie过期失效
            self.session.cookies.clear()
            self._login(username, password)
            self.crawl_data()


    def _login(self, username, passwd):
        # url = 'https://sycm.taobao.com'
        login_url = 'https://login.taobao.com/member/login.jhtml?from=sycm&full_redirect=true&style=minisimple&minititle=&minipara=0,0,0&sub=true&redirect_url=http://sycm.taobao.com/'
        driver = webdriver.Chrome(
            # executable_path="E:/Program Files (x86)/chromedriver"
            executable_path="C:/Program Files (x86)/Google/Chrome/Application/chromedriver"
            )
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

    def _check_login(self):
        """验证是否登陆成功
        Returns:
            Boolean: 是否登陆成功
        """
        res = self.session.get(self.data_url, headers=HEADERS, verify=False)
        # import pdb
        # pdb.set_trace()
        text = res.text
        login_key = re.findall(r'title="登出"', text)
        if login_key:
            return True
        else:
            return False

    def crawl_data(self):
        pass


if __name__ == '__main__':
    username = '健客大药房旗舰店:运营04'
    passwd = 'cfyyy_04'
    sycm = Sycm(username, passwd)

