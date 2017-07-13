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

# class IndustryFirstCategory(BaseModel):
#     '''
#     存储一级目录
#     '''
#     cate_id = CharField(verbose_name='一级产品类型ID', unique=True)
#     cate_name = CharField(verbose_name='一级产品类型')
 
#     class Meta:
#         db_table = 'industry_first_category'

class IndustryCategory(BaseModel):
    '''
    存储一、二级目录
    '''
    second_cate_id = IntegerField(verbose_name='二级产品类型ID')
    second_cate_name = CharField(verbose_name='二级产品类型', null=True)
    cate_id = IntegerField(verbose_name='一级产品类型ID')
    cate_name = CharField(verbose_name='一级产品类型')
    update_time = CharField(default=datetime.date.today)

    class Meta:
        db_table = 'industry_category'
        indexes = (
             (('cate_id', 'second_cate_id'), True),
             )

class IndustryThirdCategory(BaseModel):
    '''
    存储三级目录
    '''
    second_category = ForeignKeyField(IndustryCategory, related_name='second_category')
    third_cate_id = CharField(verbose_name='三级产品类型ID', unique=True)
    third_cate_name = CharField(verbose_name='三级产品类型')
    update_time = CharField(default=datetime.date.today)

    class Meta:
        db_table = 'industry_third_category'
        # indexes = (
        #      (('second_category', 'third_cate_id'), True),
        #      )

class Industrys(BaseModel):
    '''
    存储三级或二级目录下的商品详细信息
    '''
    third_category = ForeignKeyField(IndustryThirdCategory, related_name='third_category')
    model_id = IntegerField(verbose_name='产品ID')
    model_name = CharField(verbose_name='产品名')
    trade_index = CharField(verbose_name='交易指数')
    pay_item_qty = CharField(verbose_name='支付件数')
    brand_id = CharField(verbose_name='品牌ID')
    brand_name = CharField(verbose_name='品牌名')
    rank_id = CharField(verbose_name='特定产品类型下的排名')
    update_time = CharField(default=datetime.date.today)

    class Meta:
        db_table = 'industrys'
        indexes = (
             (('model_id', 'brand_id', 'update_time'), True),
             )

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

