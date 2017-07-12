# -*- coding:utf-8 -*-

import datetime
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import logging
import logging.config

from settings import LOGGING, HEADERS

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('myspider')


sender='515550681@qq.com'    # 发件人邮箱账号
passwd = 'lwbsjijnxqnycagb'              # 发件人邮箱密码(当时申请smtp给的口令)
receiver='liling@jianke.com'      # 收件人邮箱账号，我这边发送给自己

def send_email(receiver, content):
    try:
        msg=MIMEText(content,'plain','utf-8')
        msg['From']=formataddr(["liling",sender])  #括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To']=formataddr(["liling",receiver])              #括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject']="中标数据网数据爬取记录"                #邮件的主题，也可以说是标题

        server=smtplib.SMTP_SSL("smtp.qq.com", 465)  #发件人邮箱中的SMTP服务器，端口是465
        server.login(sender, passwd)  #括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(sender,[receiver,],msg.as_string())  #括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()# 关闭连接
        logger.debug("\033[96m {}. 邮件发送成功 \033[0m"
                .format(datetime.datetime.today().strftime('%Y-%m-%d %H:%m')))
    except Exception as e:
        logger.error("\033[92m {}. 邮件发送失败:{} \033[0m"
                .format(datetime.datetime.today().strftime('%Y-%m-%d %H:%m'), e))

if __name__ == '__main__':
    send_email(receiver, 'ceshi')
