import datetime

# from MySQLdb import *                                              
from peewee import *

from settings import MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWD
from utils import get_yesterday

mysql_db = MySQLDatabase(MYSQL_DBNAME, host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWD)

class BaseModel(Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = mysql_db


class IndustryProduct(BaseModel):
    '''
    产品分析 数据
    '''
    ranking = CharField()
    product = CharField()
    sale_index = CharField()
    sales = CharField()
    operation = CharField()
    sycm_product_url = CharField()
    update_date = CharField(default=get_yesterday)

    class Meta:
        db_table = 'industry_product'


class ListItem(BaseModel):
    '''
    商品店铺表
    '''
    shop_name = CharField()
    item_category = CharField()
    item_category_id = CharField()
    item_title = CharField()
    item_id = CharField()
    item_price = CharField()
    item_url = CharField()

    class Meta:
        db_table = 'product_shop'
        indexes = (
             # Specify a unique multi-column index on 'item_title', 'item_id'.
             (('shop_name', 'item_title', 'item_id'), True),
             )


class ListItemTrend(BaseModel):
    '''
    商品趋势 数据
    '''
    list_item = ForeignKeyField(ListItem, related_name='list_item')
    pay_item_qty = CharField()
    pay_ord_cnt = CharField()
    pay_byr_rate_index = CharField()
    data_mapping_date = CharField()

    class Meta:
        db_table = 'product_trend'
        indexes = (
             # Specify a unique multi-column index on 'item_title', 'item_id'.
             (('data_mapping_date', 'list_item'), True),
             )

