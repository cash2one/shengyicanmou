from models import IndustryProduct, ListItemTrend

def before_request_handler():
    if not IndustryProduct.table_exists():
        IndustryProduct.create_table()
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
                        ranking=ranking,
                        product=product,
                        sale_index=sale_index,

                        defaults = {
                            'city_country_url':city_country_url,
                            },
                        )
                    if not created:
                        city_country.city_country_url = city_country_url
                        #import pdb
                        #pdb.set_trace()
                        industry_product.save()
                except Exception as e:
                    logger.error(e)
       return item
