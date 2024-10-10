import scrapy
from typing import Any

from scrapy.http import Response

from ..items import MuabanItem

class HouseSpider(scrapy.Spider):
    name = "House"
    start_urls = [
        "https://muaban.net/bat-dong-san/ban-nha?page=1"
    ]

    # COMMENT WHEN CLEANING THE DATA: The property price is the first one (if there are many)

    BASE_URL = "https://muaban.net/"
    # def __init__(self, house_type, **kwargs: Any):
    #     super().__init__(**kwargs)
    #     if house_type == "town":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-nha-mat-tien?page=1"]
    #     elif house_type == "alley":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-nha-hem-ngo?page=1"]
    #     elif house_type == "villa":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-biet-thu-villa-penthouse?page=1"]

    def parse(self, response: Response):
        property_links = response.css(".title::attr(href)").extract()
        for link in property_links:
            yield scrapy.Request(HouseSpider.BASE_URL + link, callback = self.parse_property)

        curr_page = response.url.split("=")[-1]
        curr_page_number = int(curr_page) if curr_page.isdigit() else 1
        next_page_number = curr_page_number + 1
        next_page = response.url.replace(f"page={curr_page_number}", f"page={next_page_number}")
        if next_page_number <= 100:
            yield response.follow(next_page, callback=self.parse)

    def parse_property(self, response: Response):
        items = MuabanItem()
        items['title'] = response.css("h1::text").extract()
        items['address'] = response.css(".address::text").extract()
        items['price'] = response.css(".price::text").extract()
        items['briefing'] = response.css(".gdAVnx::text").extract()
        items['property_type'] = response.css(".iHMsCj .label+ span").css("::text").extract()
        items['area'] = response.css(".bMsWUQ .label+ span").css("::text").extract()
        items['bedrooms'] = response.css(".iqdYme .label+ span").css("::text").extract()
        items['bathrooms'] = response.css(".fJTowC .label+ span").css("::text").extract()
        items['floors'] = response.css(".bgrmZM .label+ span").css("::text").extract()
        items['direction'] = response.css(".iCmNyo .label+ span").css("::text").extract()
        items['balcony_direction'] = response.css(".fxooPS .label+ span").css("::text").extract()
        items['law_doc'] = response.css(".cizefY .label+ span").css("::text").extract()
        yield items


