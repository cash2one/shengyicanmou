# coding:utf-8

import random
import datetime

from fake_useragent import UserAgent

# from settings import REFERER_LIST

def get_user_agent():
    ua = UserAgent()
    return ua.random

# def get_referer():
#     return random.choice(REFERER_LIST)


def get_30_date_before_today():
    '''
    注意日期应该从小到大写入list
    '''
    today = datetime.date.today()
    date_list= []
    #for i in range(1, 31):
    start = 30
    while start > 0:
        day = datetime.timedelta(days=start)
        date_list.append(today-day )
        start -= 1
    return date_list
        
