from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from locations.hours import DAYS_NL, OpeningHours
from locations.items import Feature


class SpecsaversNLSpider(CrawlSpider):
    name = "specsavers_nl"
    item_attributes = {"brand": "Specsavers", "brand_wikidata": "Q2000610"}
    start_urls = ["https://www.specsavers.nl/winkelzoeker/winkeloverzicht"]
    rules = [
        Rule(
            LinkExtractor(
                allow=r"^https:\/\/www\.specsavers\.nl\/winkelzoeker\/(?!winkeloverzicht)((?!<\/)(.(?!-hoorzorg))+)$"
            ),
            callback="parse_store",
        )
    ]

    def parse_store(self, response):
        properties = {
            "ref": response.xpath('//div[contains(@class, "js-yext-info")]/@data-yext-url').get().split("?", 1)[0],
            "name": response.xpath('//h1[contains(@class, "store-header--title")]/text()').get().strip(),
            "lat": response.xpath("//div/@data-store-geo-loc-lat").get().strip(),
            "lon": response.xpath("//div/@data-store-geo-loc-lng").get().strip(),
            "addr_full": " ".join(
                (" ".join(response.xpath('//div[contains(@class, "store")]/p[1]/span/text()').getall())).split()
            ),
            "postcode": response.xpath('//div[contains(@class, "store")]/p[1]/span[@itemprop="postalCode"]/text()')
            .get()
            .strip(),
            "city": response.xpath('//div[contains(@class, "store")]/p[1]/span[@itemprop="addressRegion"]/text()')
            .get()
            .strip(),
            "phone": response.xpath('//span[contains(@class, "contact--store-telephone--text")]/text()').get().strip(),
            "website": response.url,
        }

        properties["opening_hours"] = OpeningHours()
        hours_raw = (
            (" ".join(response.xpath('//tr[@itemprop="openingHours"]/@content').getall()))
            .replace("Gesloten", "0:00 - 0:00")
            .replace(" - ", " ")
            .split()
        )
        hours_raw = [hours_raw[n : n + 3] for n in range(0, len(hours_raw), 3)]
        for day in hours_raw:
            if day[1] == "0:00" and day[2] == "0:00":
                continue
            properties["opening_hours"].add_range(DAYS_NL[day[0]], day[1].upper(), day[2].upper())

        yield Feature(**properties)
