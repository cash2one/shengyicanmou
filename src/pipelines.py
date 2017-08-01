# coding:utf-8

import datetime
import logging
import logging.config

from models import  ListItemTrend, IndustryCategory,\
        IndustryThirdCategory, Industrys,\
        ListItem, mysql_db
from settings import LOGGING
from  utils import get_30_date_before_today, get_lastday

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('mydata')

def before_request_handler():
    # if not IndustryFirstCategory.table_exists():
    #     IndustryFirstCategory.create_table()
    if not IndustryCategory.table_exists():
        IndustryCategory.create_table()
    if not IndustryThirdCategory.table_exists():
        IndustryThirdCategory.create_table()
    if not Industrys.table_exists():
        Industrys.create_table()
    if not ListItem.table_exists():
        ListItem.create_table()
    if not ListItemTrend.table_exists():
        ListItemTrend.create_table()

class SycmData(object):

    def __init__(self):
        before_request_handler()

    # def save_industry_category(self):
    #     '''
    #     https://sycm.taobao.com/mq/industry/product/rank.htm
    #     在页面数据没有发生变化之前，该表数据固定不变
    #     '''
    #     categorys = [
    #         {'cate_id': '122966004', 'cate_name': '处方药'},
    #         {'cate_id': '50023717', 'cate_name': 'OCT药品/医疗器械/计生用品'},
    #     ]
    #     with mysql_db.atomic():
    #         IndustryFirstCategory.insert_many(categorys).execute()

    def save_category(self, item_list):
        # if not IndustryFirstCategory.select().count():
        #     self.save_industry_category()
        for item in item_list:
            second_cate_id = item['second_cate_id']
            second_cate_name = item['second_cate_name']
            third_cate_id = item['third_cate_id']
            third_cate_name = item['third_cate_name']
            cate_id = item['cate_id']

            if cate_id == 50023717: cate_name = 'OCT药品/医疗器械/计生用品'
            elif cate_id == 122966004: cate_name = '处方药'
            else: cate_name = None
            logger.debug('\033[96m 保存产品分析一、二级目录数据: cate_name:{0}, \
                        second_cate_name:{1} \033[0m'.format(cate_name, second_cate_name))
            #import pdb
            #pdb.set_trace()
            try:
                if second_cate_name:
                    #此时该目录是三级目录
                    second_category, created = IndustryCategory.get_or_create(
                        second_cate_id = second_cate_id,
                        cate_id = cate_id,
                        defaults = {
                            'second_cate_name': second_cate_name,
                            'cate_name': cate_name,
                        })
                    if not created:
                        second_category.second_cate_name = second_cate_name
                        second_category.cate_name = cate_name
                        second_category.save()
                else:
                    #此时该目录是二级目录
                    second_category = IndustryCategory.get_or_create(
                        second_cate_id = second_cate_id,
                        cate_id = cate_id,
                        defaults = {
                            'second_cate_name': second_cate_name,
                            'cate_name': cate_name,
                        })

                third_category, third_created = IndustryThirdCategory.get_or_create(
                    third_cate_id = third_cate_id,
                    defaults ={
                        'second_category': second_category,
                        'third_cate_name': third_cate_name
                    })
                if not third_created:
                    if isinstance(second_category, tuple):
                        second_category = second_category[0]
                    third_category.second_category = second_category
                    third_category.third_cate_name = third_cate_name
                    third_category.save()
            except Exception as e:
                logger.error('\033[92m {} \033[0m'.format(e))

    def save_industrys(self, item_list):
        for item in item_list:
            third_cate_id = item['cate_id']
            model_id = item['model_id']
            model_name = item['model_name']
            trade_index = item['trade_index']
            pay_item_qty = item['pay_item_qty']
            brand_id = item['brand_id']
            brand_name = item['brand_name']
            rank_id = item['rank_id']
            update_time = datetime.date.today() - datetime.timedelta(1)
            logger.debug('\033[96m 保存产品分析的详情: 产品名:{0} \033[0m'.format(model_name))
            try:
                third_category = IndustryThirdCategory.get(third_cate_id=third_cate_id)
                industry, created = Industrys.get_or_create(
                        model_id = model_id,
                        update_time = update_time,
                        brand_id = brand_id,
                        defaults = {
                            'third_category':third_category,
                            'model_name': model_name,
                            'trade_index': trade_index,
                            'pay_item_qty': pay_item_qty,
                            'brand_name': brand_name,
                            'rank_id': rank_id,
                            },
                        )
                if not created:
                        industry.third_category = third_category
                        industry.model_name = model_name
                        industry.trade_index = trade_index
                        industry.pay_item_qty = pay_item_qty
                        industry.brand_id = brand_id
                        industry.brand_name = brand_name
                        industry.rank_id = rank_id
                        industry.save()
            except Exception as e:
                logger.error('\033[92m {} \033[0m'.format(e))

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
                            logger.debug('\033[96m 保存商品趋势信息: date:{0}, 所有终端-支付子订单数:{1} , 所有终端-支付转化率指数：{2} ,所有终端-支付件数:{3}\033[0m'
                                        .format(data_mapping_date,
                                            pay_item_qty, pay_ord_cnt,
                                            pay_byr_rate_index))
                            list_item_trend, created = ListItemTrend.get_or_create(
                                    list_item = list_item,
                                    data_mapping_date = data_mapping_date,
                                    defaults = {
                                        'pay_item_qty': pay_item_qty if  pay_item_qty else 0,
                                        'pay_ord_cnt': pay_ord_cnt if pay_ord_cnt else 0,
                                        'pay_byr_rate_index': pay_byr_rate_index if pay_byr_rate_index else 0,
                                        }
                                    )
                            if not created:
                                list_item_trend.pay_item_qty =  pay_item_qty
                                list_item_trend.pay_ord_cnt = pay_ord_cnt
                                list_item_trend.pay_byr_rate_index = pay_byr_rate_index
                                list_item_trend.save()
                except Exception as e:
                    logger.error('\033[92m {} \033[0m'.format(e))





