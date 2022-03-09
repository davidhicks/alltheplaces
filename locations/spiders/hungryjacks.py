# -*- coding: utf-8 -*-
import re

import scrapy
import json

from locations.items import GeojsonPointItem

class HungryJacksSpider(scrapy.Spider):
    #download_delay = 0.3
    name = "hungry_jacks"
    item_attributes = {'brand': "Hungry Jacks"}
    allowed_domains = ["hungryjacks.com.au"]
    start_urls = ([
        'https://www.hungryjacks.com.au/api/storelist',
    ])

    def parse(self, response):
        data = json.loads(json.dumps(response.json()))
        for i in data:
            properties = {
                'ref': i['store_id'],
                'name': i['name'],
                'addr_full': i['location']['address'],
                'city': i['location']['suburb'],
                'state': i['location']['state'],
                'postcode': i['location']['postcode'],
                'country': "AU",
                'phone': i['location']['phone'],
                'lat': i['location']['lat'],
                'lon': i['location']['long'],
            }
            yield GeojsonPointItem(**properties)
