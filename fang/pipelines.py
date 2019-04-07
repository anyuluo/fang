# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors
from fang.items import NewHouseItem, ESFItem


class FangPipeline(object):
    def process_item(self, item, spider):
        return item


class HousePipeline(object):
    def __init__(self):
        # 数据库链接参数
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'anyu',
            'db': 'fang',
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }
        # 创建一个数据库连接池
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        # sql
        self._sql_newhouse = None
        self._sql_esf = None

    def process_item(self, item, spider):
        # runInteraction 异步执行sql语句
        defer = self.dbpool.runInteraction(self.insert_item, item)
        defer.addErrback(self.handle_error, item, spider)

        # sql = '''
        #     insert into newhouse(id, province, city, name, price, rooms, area, address, district, sale, origin_url)
        #     values (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        # '''
        # self.cursor.execute(sql, (item['province'], item['city'], item['name'], item['price'], item['rooms'],
        #                           item['area'], item['address'], item['district'], item['sale'], item['origin_url']))
        # self.conn.commit()
        return item

    # 数据入库
    def insert_item(self, cursor, item):
        # 根据item的类型将数据放到数据库中
        if type(item) == NewHouseItem:
            cursor.execute(self.sql_newhouse,
                           (item['province'], item['city'], item['name'], item['price'], item['rooms'],
                            item['area'], item['address'], item['district'], item['sale'], item['origin_url']))
        elif type(item) == ESFItem:
            cursor.execute(self.sql_esf, (item['province'], item['city'], item['name'], item['total_price'],
                                          item['price'], item['rooms'], item['area'], item['floor'], item['toward'],
                                          item['build'], item['plot'], item['address'], item['traffic'],
                                          item['origin_url']))
        else:
            pass

    # 出错处理
    def handle_error(self, error, item, spider):
        print(error)

    @property
    def sql_newhouse(self):
        if not self._sql_newhouse:
            self._sql_newhouse = '''
                insert into newhouse(id, province, city, name, price, rooms, area, address, district, sale, origin_url)
                values (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            return self._sql_newhouse
        return self._sql_newhouse

    @property
    def sql_esf(self):
        if not self._sql_esf:
            self._sql_esf = '''
                insert into esf(id, province, city, name, total_price, price, rooms, area, floor, toward, build, plot, 
                address, traffic, origin_url)
                values (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            return self._sql_esf
        return self._sql_esf
