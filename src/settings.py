import os
import random

from utils import get_user_agent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MYSQL_HOST = '172.17.240.6'
MYSQL_DBNAME = 'shengyicanmou'
MYSQL_USER = 'root'
MYSQL_PASSWD = '2016abc'

REFERER_LIST = [
    'https://www.google.com/',
    'https://www.baidu.com/',
]

HEADERS = {
            "User-Agent": get_user_agent(),
            "Referer" : random.choice(REFERER_LIST),
            "Accept-encoding": "gzip",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch, br",
            "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            }

PROXY_SITES = []



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(pathname)s:%(lineno)d][%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'}
    },
    #过滤器，表明一个日志信息是否要被过滤掉而不记录
    'filters': {                                         
    },
    #处理器
    'handlers': {
        'spider': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + '/log/spider.log',
            'maxBytes': 1024*1024*5,
            # 'backupCount': 5,
            'formatter':'standard',
        },
        'spider_error': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + '/log/spider_error.log',
            'maxBytes':1024*1024*5,
            # 'backupCount': 5,
            'formatter':'standard',
            },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'ocr': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename':BASE_DIR + '/log/data.log',
            'maxBytes': 1024*1024*5,
            # 'backupCount': 5,
            'formatter':'standard',
            },
        'ocr_error': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + '/log/data_error.log',
            'maxBytes':1024*1024*5,
            # 'backupCount': 5,
            'formatter':'standard',
            },
    },
    # 记录器
    'loggers': {
        'mydata': {
            'handlers': ['console', 'ocr', 'ocr_error'],
            'level': 'DEBUG',  #级别最低
            'propagate': True
        },
        'myspider': {
            'handlers': ['console', 'spider', 'spider_error'],
            'level': 'DEBUG',
            'propagate': True
        },
    }

}

import logging
import logging.config

logging.config.dictConfig(LOGGING)
dblogger = logging.getLogger('mydata')
logger = logging.getLogger('myspider')
