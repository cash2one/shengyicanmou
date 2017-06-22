# coding:utf-8

import os
import logging
import logging.config
import time
import pprint
import json

import requests
from selenium import webdriver

from settings import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('myspider')

class Sycm(object):
    def __init__(self,  username, passwd):
        self.username = username
        self.passwd = passwd
        self.session = requests.Session()
        self._login(username, passwd)
        try:
            self._get_cookies()
        except IOError as e:
            logger.debug(e)
        if self._check_login():            
            logger.debug('from cache...cookies...')
            logger.debug(self.session.cookies)    
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
            executable_path="E:/Program Files (x86)/chromedriver"
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

     def _get_cookies(self):
        """从文本中获得cookies
        """
        with open("login_cookies.json") as f:
            cookies = json.load(f)
            self.session.cookies.update(cookies)

    def _update_login_cookies(self):
        pass

    def crawl_data(self):
        pass


if __name__ == '__main__':
    username = '健客大药房旗舰店:运营04'
    passwd = 'cfyyy_04'
    sycm = Sycm(username, passwd)

