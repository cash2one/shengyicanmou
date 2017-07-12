# !/usr/bin/python
# coding:utf-8

import MySQLdb
import pandas as pd
from datetime import date, datetime


from settings import MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWD

class SycmXlsx(object):

    # 初始化
    def __init__(self):

        # 数据库链接
        self.conn_6 = MySQLdb.connect(
            host = MYSQL_HOST,
            user = MYSQL_USER,
            passwd = MYSQL_PASSWD,
            db = MYSQL_DBNAME,
            port = 3306,
            charset="utf8"
        )

    def get_file(self):

        # 从数据库获取数据
        sql = " select t2.id, t1.shop_name, t1.item_category, t1.item_title, t1.item_id, \
                t1.item_price, t1.item_url,  t2.pay_item_qty, t2.pay_ord_cnt, \
                t2.pay_byr_rate_index, t2.data_mapping_date from product_shop t1 \
                inner join product_trend t2 on t1.id=t2.list_item_id; \
              "
        df = pd.read_sql(sql, self.conn_6)

        # 删除 id 列
        # df = df.drop('id', axis = 1)
        # 计算价格排名
        #df['price_rank'] = df.groupby("jk_id")['price'].rank(method = 'dense', ascending = False)
        # 标识 最高价
        #idx =  df.groupby(['jk_id'])['price'].transform(max) == df['price']
        #df.loc[idx, '价格标识'] = '最高价'
        # 标识 最低价
        #idx =  df.groupby(['jk_id'])['price'].transform(min) == df['price']
        #df.loc[idx, '价格标识'] = '最低价'
        # 表示 中间价
        #idx = df['价格标识'].isnull()
        #df.loc[idx, '价格标识'] = '中间价'

        # 修改中文名
        df = df.rename(columns = {
            'id' : 'ID',
            'shop_name' : '店铺名',
            'item_category' : '商品分类',
            'item_title' : '商品',
            'item_id' : '商品ID',
            'item_price' : '商品价格',
            'item_url' : '商品链接',
            'pay_item_qty' : '所有终端-支付件数',
            'pay_ord_cnt' : '所有终端-支付子订单数',
            'pay_byr_rate_index' : '所有终端-支付转化率指数',
            'data_mapping_date' : '日期',
        })
        # 保存 excel 文件
        date = datetime.today().strftime('%Y-%m-%d')
        filename = u"/home/liling/share/{date}商品趋势（处方药）.xlsx".format(date=date)
        df = df.drop('ID', axis = 1)
        df.to_excel(filename, u'结果')


if __name__ == '__main__':
    main = SycmXlsx()
    main.get_file()
