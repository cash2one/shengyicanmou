# coding:utf-8

from models import IndustryProduct, ListItemTrend, \
        ListItem

def before_request_handler():
    if not IndustryProduct.table_exists():
        IndustryProduct.create_table()
    if not ListItem.table_exists():
        ListItem.create_table()
    if not ListItemTrend.table_exists():
        ListItemTrend.create_table()

class Sycm(object):

    def __init__(self):
        before_request_handler()

    def save_industry_product(self, items):
        if not isinstance(items, list):
            return
        else:
            for item in items:
                ranking = item['ranking']
                product = item['product']
                sale_index = item['sale_index']
                sales = item['sales']
                operation = item['operation']
                logger.debug('\033[92m product:{0}, sales:{1} \033[0m'
                    .format(product.encode('utf-8'), sales.encode('utf-8')))
                try:
                    industry_product, created = IndustryProduct.get_or_create(
                        product=product,
                        defaults = {
                            'sale_index': sale_index,
                            'ranking': ranking,
                            'sales': sales,
                            'operation': operation
                            },
                        )
                    if not created:
                        industry_product.sale_index = sale_index
                        industry_product.ranking = ranking
                        industry_product.sales = sales
                        industry_product.operation = operation
                        #import pdb
                        #pdb.set_trace()
                        industry_product.save()
                except Exception as e:
                    logger.error(e)
        return item
