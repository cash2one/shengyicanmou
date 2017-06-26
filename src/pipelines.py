# coding:utf-8

import datetime
import logging
import logging.config

from models import IndustryProduct, ListItemTrend, \
        ListItem, mysql_db
from settings import LOGGING
from  utils import get_30_date_before_today, get_yesterday

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
                update_date = get_yesterday()
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

    def save_list_item_trend(self, items):
        if not isinstance(items, list):
            return
        else:
            for item in items:
                shop_name = item['shop_name']
                item_category = item['item_category']
                item_category_id = item['item_category_id']
                item_title = item['item_title']
                item_id = item['item_id']
                item_price = item['item_price']
                item_url = item['item_url']
                logger.debug('\033[92m 保存商品店铺信息: shop_name:{0}, item_title:{1} \033[0m'
                    .format(shop_name, item_title))
                # 这里还需要对这三组list数据做对应日期映射
                pay_item_qtylist = item['pay_item_qtylist']
                pay_ord_cntlist = item['pay_ord_cntlist']
                pay_byr_rate_index_list = item['pay_byr_rate_index_list']

                try:
                    list_item, created = ListItem.get_or_create(
                            item_title = item_title,
                            item_id = item_id,
                            shop_name = shop_name,
                            defaults = {
                                'item_category': item_category,
                                'item_category_id': item_category_id,
                                'item_price': item_price,
                                'item_url': item_url,
                                })
                    if not created:
                        list_item.item_price = item_price
                        list_item.item_url = item_url
                        list_item.item_category = item_category
                        list_item.item_category_id = item_category_id
                        list_item.save()

                    #import pdb
                    #pdb.set_trace()
                    #cursor = mysql_db.execute_sql('select count(*) from list_item_trend')
                    #res = cursor.fetchone()
                    ## 第一次将数据写入到ListItemTrend表时应该写入所有pay_*数据:
                    #if res[0] == 0:
                    if not len(pay_item_qtylist) \
                            == len(pay_ord_cntlist) \
                            == len(pay_byr_rate_index_list) == 30:
                        logger.warning('\033[94m please check the list data !!!\033[0m')
                    else:
                        date_list = get_30_date_before_today()
                        for num, old_date in enumerate(date_list):
                            data_mapping_date = old_date
                            pay_item_qty = pay_item_qtylist[num]
                            pay_ord_cnt = pay_ord_cntlist[num]
                            pay_byr_rate_index = pay_byr_rate_index_list[num]
                            logger.debug('\033[92m 保存商品趋势信息: date:{0}, 所有终端-支付子订单数:{1} , 所有终端-支付转化率指数：{2} ,所有终端-支付件数:{3}\033[0m'
                                        .format(data_mapping_date,
                                            pay_item_qty, pay_ord_cnt, 
                                            pay_byr_rate_index))
                            list_item_trend, created = ListItemTrend.get_or_create(
                                    list_item = list_item,
                                    data_mapping_date = data_mapping_date,
                                    defaults = {
                                        'pay_item_qty': pay_item_qty,
                                        'pay_ord_cnt': pay_ord_cnt,
                                        'pay_byr_rate_index': pay_byr_rate_index,
                                        }
                                    )
                            if not created:
                                list_item_trend.pay_item_qty =  pay_item_qty
                                list_item_trend.pay_ord_cnt = pay_ord_cnt
                                list_item_trend.pay_byr_rate_index = pay_byr_rate_index
                                list_item_trend.save()
                except Exception as e:
                    logger.error(e)

                



