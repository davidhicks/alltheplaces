# -*- coding: utf-8 -*-
import json
import re

import scrapy
from locations.items import GeojsonPointItem
from scrapy.selector import Selector


class FarmerBoys(scrapy.Spider):
    name = "farmerboys"
    item_attributes = {"brand": "Farmer Boys", "brand_wikidata": "Q5435711"}
    allowed_domains = ["farmerboys.com"]
    start_urls = ["https://www.farmerboys.com/locations/"]

    def parse(self, response):
        locations_js = response.xpath(
            '//script[contains(text(), "initMap")]/text()'
        ).extract_first()
        locations = re.findall("var\s+locations\s*=\s*(\[.*\]);", locations_js)[0]
        locations = json.loads(locations)
        for location in locations:
            properties = {
                "name": location["location_name"],
                "ref": location["location_url"],
                "street_address": location["address_1"],
                "city": location["city"],
                "postcode": location["postal_code"],
                "state": location["state"],
                "country": "US",
                "phone": location["phone"],
                "website": "https://www.farmerboys.com/locations/location-detail.php?loc="
                + location["location_url"].strip(),
                "image": "https://www.farmerboys.com/images/locations/"
                + location["location_pic"].strip()
                if location["location_pic"]
                else None,
                "lat": float(location["lat"]) if location["lat"] else None,
                "lon": float(location["lng"]) if location["lng"] else None,
                "opening_hours": " ".join(
                    Selector(text=location["location_hours"]).xpath("//text()").getall()
                ).replace("\r\n", ""),
            }
            yield GeojsonPointItem(**properties)