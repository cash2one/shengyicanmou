# coding:utf-8

import datetime
import logging
import logging.config

from models import IndustryProduct, ListItemTrend, \
        ListItem
from settings import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('mydata')

def before_request_handler():
    if not IndustryProduct.table_exists():
        IndustryProduct.create_table()
    if not ListItem.table_exists():
        ListItem.create_table()
    if not ListItemTrend.table_exists():
        ListItemTrend.create_table()

class SycmData(object):

    def __init__(self):
        before_request_handler()

    def save_industry_product(self, items):
        if not isinstance(items, list):
            return
        else:
            for item in items:
                ranking = item['ranking']
                product = item['product']
                sycm_product_url = item['sycm_product_url']
                sale_index = item['sale_index']
                sales = item['sales']
                operation = item['operation']
                update_date = datetime.date.today()
                logger.debug('\033[92m 保存产品分析的数据: product:{0}, ranking:{1} \033[0m'
                    .format(product, ranking))
                try:
                    industry_product, created = IndustryProduct.get_or_create(
                        product = product,
                        update_date = update_date,
                        sale_index = sale_index,
                        defaults = {
                            'ranking': ranking,
                            'sales': sales,
                            'operation': operation,
                            'sycm_product_url': sycm_product_url
                            },
                        )
                    if not created:
                        industry_product.ranking = ranking
                        industry_product.sales = sales
                        industry_product.operation = operation
                        industry_product.sycm_product_url = sycm_product_url
                        #import pdb
                        #pdb.set_trace()
                        industry_product.save()
                except Exception as e:
                    logger.error(e)
