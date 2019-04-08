# -*- coding: utf-8 -*-
import scrapy
import re
from fang.items import NewHouseItem, ESFItem


class FtxSpider(scrapy.Spider):
    name = 'ftx'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        # 提取全国所有城市得url
        trs = response.xpath('//div[@class="outCont"]/table/tr')
        # 省份
        province = None
        # 遍历大陆城市
        for tr in trs[:-2]:
            # 查找所有没有class属性的标签
            tds = tr.xpath('.//td[not(@class)]')
            # 省份
            province_text = tds[0].xpath('.//text()').get()
            # 使用正则将省份中的空白字符替换为空
            province_text = re.sub(r'\s', '', province_text)
            # 如果省份不为空，则将省份保存下来
            if province_text:
                province = province_text
            # 城市信息a标签
            city_links = tds[1].xpath('.//a')
            for city_link in city_links:
                city = city_link.xpath('.//text()').get()
                # 城市链接
                city_url = city_link.xpath('.//@href').get()
                newhouse_url = None
                esf_url = None
                if '北京' in city:
                    newhouse_url = 'https://newhouse.fang.com/house/s/'
                    esf_url = 'https://esf.fang.com/'
                else:
                    # 构建新房链接
                    newhouse_url = city_url.split('.')[0] + '.newhouse.fang.com/house/s/'
                    # 构建二手房链接
                    esf_url = city_url.split('.')[0] + '.esf.fang.com'
                # 新房调度请求
                yield scrapy.Request(url=newhouse_url, callback=self.parser_newhouse, meta={'info': (province, city)})
                # 二手房调度请求
                yield scrapy.Request(url=esf_url, callback=self.parser_esf, meta={'info': (province, city, esf_url)})

    # 城市新房数据
    def parser_newhouse(self, response):
        # 获取省份城市信息
        province, city = response.meta.get('info')
        lis = response.xpath('//div[@class="nhouse_list"]/div/ul/li[not(@class)]')
        for li in lis:
            try:
                # 小区名称
                name = li.xpath('.//div[@class="nlcd_name"]/a/text()').get().strip()
                # 价格
                price = ''.join(li.xpath('.//div[@class="nhouse_price"]//text()').getall())
                # 去掉价格中的杂质字符
                price = re.sub(r'\s', '', price)
                # 居室
                rooms = ''.join(li.xpath('.//div[@class="house_type clearfix"]/a/text()').getall())
                # 面积
                area = ''.join(li.xpath('.//div[@class="house_type clearfix"]/text()').getall())
                # 去除面积中的杂质字符
                area = re.sub(r'[\s/－]', '', area)
                # 地址
                address = li.xpath('.//div[@class="address"]/a/@title').get()
                # 行政区， 包含地址
                district_text = ''.join(li.xpath('.//div[@class="address"]/a//text()').getall())
                # 使用正则提取出行政区
                district = re.search(r'\[(.*)\].*', district_text).group(1)
                # 是否在售
                sale = li.xpath('.//span[@class="inSale" or @class="forSale"]/text()').get()
                # 详情页面url
                origin_url = li.xpath('.//div[@class="nlcd_name"]/a/@href').get()

                item = NewHouseItem(province=province, city=city, name=name, price=price, rooms=rooms, area=area,
                                    address=address, district=district, sale=sale, origin_url=origin_url)
                yield item

            except Exception as e:
                print(e)

        # 获取下一页链接
        next_url = response.xpath('//a[@class="next"]/@href')
        # 请求下一页
        yield scrapy.Request(url=response.urljoin(next_url), callback=self.parser_newhouse,
                             meta={'info': (province, city)})

    # 城市二手房数据
    def parser_esf(self, response):
        # 获取省份城市信息
        province, city, esf_url = response.meta.get('info')
        # 格式化数据
        item = ESFItem(province=province, city=city)
        # 每一页所有二手房信息
        dls = response.xpath('//div[@class="shop_list shop_list_4"]/dl[@dataflag]')
        for dl in dls:
            try:
                # 二手房标题名
                item['name'] = dl.xpath('.//h4[@class="clearfix"]/a/@title').get()
                # 总价
                item['total_price'] = dl.xpath('.//dd[@class="price_right"]/span/b/text()').get()
                # 单价
                item['price'] = dl.xpath('.//dd[@class="price_right"]/span[not(@class)]/text()').get()
                # tel_shop
                tel_shop_list = dl.xpath('.//p[@class="tel_shop"]/text()').getall()
                # 将住房详情信息中的空白字符去掉
                tel_shop_list = list(map(lambda x: re.sub(r'\s', '', x), tel_shop_list))
                for info in tel_shop_list:
                    if '厅' in info:
                        item['rooms'] = info  # 厅室
                    elif '㎡' in info:
                        item['area'] = info  # 面积
                    elif '层' in info:
                        item['floor'] = info  # 楼层
                    elif '向' in info:
                        item['toward'] = info  # 朝向
                    elif '建' in info:
                        item['build'] = info  # 建成年限
                # 小区
                item['plot'] = dl.xpath('.//p[@class="add_shop"]/a/@title').get()
                # 地址
                item['address'] = dl.xpath('.//p[@class="add_shop"]/span/text()').get()
                # 交通
                item['traffic'] = dl.xpath('.//span[@class="bg_none icon_dt"]/text()').get()
                # 二手房详情url
                item['origin_url'] = esf_url + dl.xpath('.//h4[@class="clearfix"]/a/@href').get()

                yield item

            except Exception as e:
                print(e)

        # 下一页链接
        next_url = response.xpath('//div[@class="page_al"]/p[a="下一页"]/a/@href').get()
        # 将下一页请求交给引擎
        yield scrapy.Request(url=response.urljoin(next_url), callback=self.parser_esf,
                             meta={'info': (province, city, esf_url)})
