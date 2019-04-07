# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 新房
class NewHouseItem(scrapy.Item):
    # 省份
    province = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 小区名字
    name = scrapy.Field()
    # 价格
    price = scrapy.Field()
    # 居室  列表
    rooms = scrapy.Field()
    # 面积
    area = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 行政区
    district = scrapy.Field()
    # 是否在售
    sale = scrapy.Field()
    # 房天下详情页面url
    origin_url = scrapy.Field()


# 二手房
class ESFItem(scrapy.Item):
    # 省份
    province = scrapy.Field()
    # 城市
    city = scrapy.Field()
    # 二手房名称
    name = scrapy.Field()
    # 总价
    total_price = scrapy.Field()
    # 单价
    price = scrapy.Field()
    # 厅室
    rooms = scrapy.Field()
    # 面积
    area = scrapy.Field()
    # 楼层
    floor = scrapy.Field()
    # 朝向
    toward = scrapy.Field()
    # 建造年限
    build = scrapy.Field()
    # 小区
    plot = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 交通
    traffic = scrapy.Field()
    # 详情链接
    origin_url = scrapy.Field()
