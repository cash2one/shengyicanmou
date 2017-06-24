import datetime

# from MySQLdb import *                                              
from peewee import *

from settings import MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWD

mysql_db = MySQLDatabase(MYSQL_DBNAME, user=MYSQL_USER, passwd=MYSQL_PASSWD)

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
    update_date = CharField(default=datetime.date.today)

    class Meta:
        db_table = 'industry_product'


class ListItem(BaseModel):
    shop_name = CharField()
    item_title = CharField()
    item_id = CharField()
    item_price = CharField()
    item_url = CharField()

    class Meta:
        db_table = 'list_item'
         indexes = (
             # Specify a unique multi-column index on 'item_title', 'item_id'.
             (('item_title', 'item_id'), True),


class ListItemTrend(BaseModel):
    '''
    商品趋势 数据
    '''
    list_item = ForeignKeyField(ListItem, related_name='list_item')
    pay_item_qtylist = CharField()
    pay_ord_cntlist = CharField()
    pay_byr_rate_index_list = CharField()
    update_date = CharField(default=datetime.date.today)

    class Meta:
        db_table = 'list_item_trend'
