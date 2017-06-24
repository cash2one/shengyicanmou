import datetime

# from MySQLdb import *                                              
from peewee import *

from settings import MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWD

mysql_db = MySQLDatabase(MYSQL_DBNAME, user=MYSQL_USER, passwd=MYSQL_PASSWD)

def convert_to_date():
    return datetime.date.today().strftime('%Y-%m-%d')

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


class ListItem(BaseModel):
    item_title = CharField(unique=True)
    item_id = CharField()

class ListItemTrend(BaseModel):
    '''
    商品趋势 数据
    '''
    list_item = ForeignKeyField(ListItem, related_name='list_item')
    pay_item_qtylist = CharField()
    pay_ord_cntlist = CharField()
    pay_byr_rate_index_list = CharField()
    update_date = CharField(default=convert_to_date)

    # class Meta:
    #     indexes = (
    #         # Specify a unique multi-column index on 'item_title', 'update_date'.
    #         (('item_title', 'update_date'), True),
    #     )
