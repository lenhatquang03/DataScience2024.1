import scrapy
from scrapy.http import Response
from ..items import MuabanItem

class ApartmentSpider(scrapy.Spider):
    name = "Apartment"
    BASE_URL = "https://muaban.net/"
    start_urls = [
        "https://muaban.net/bat-dong-san/ban-can-ho?page=1"
    ]

    # COMMENT WHEN CLEANING THE DATA: The property price is the first one (if there are many)

    # def __init__(self, apartment_type, **kwargs):
    #     super().__init__(**kwargs)
    #     if apartment_type == "condominium":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-can-ho-chung-cu?page=1"]
    #     elif apartment_type == "penthouse":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-can-ho-penthouse?page=1"]
    #     elif apartment_type == "service":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-can-ho-dich-vu?page=1"]
    #     elif apartment_type == "public housing":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-can-ho-tap-the-cu-xa?page=1"]
    #     elif apartment_type == "officetel":
    #         self.start_urls = ["https://muaban.net/bat-dong-san/ban-officetel?page=1"]

    def parse(self, response: Response):
        apartment_links = response.css(".title::attr(href)").extract()
        for link in apartment_links:
            yield scrapy.Request(ApartmentSpider.BASE_URL + link, self.parse_detail)

        curr_page = response.url.split("=")[-1]
        curr_page_num = int(curr_page) if curr_page.isdigit() else 1
        next_page_num = curr_page_num + 1
        next_page = response.url.replace(f"page={curr_page_num}", f"page={next_page_num}")

        if next_page_num <= 100:
            yield response.follow(next_page, self.parse)

    def parse_detail(self, response:Response):
        items = MuabanItem()
        items['title'] = response.css("h1::text").extract()
        items['address'] = response.css(".address::text").extract()
        items['price'] = response.css(".price::text").extract()
        items['briefing'] = response.css(".gdAVnx::text").extract()
        items['area'] = response.css(".kjJdBk .label+ span").css("::text").extract() #Different
        items['property_type'] = response.css(".iHMsCj .label+ span").css("::text").extract()
        items['bedrooms'] = response.css(".iqdYme .label+ span").css("::text").extract()
        items['bathrooms'] = response.css(".fJTowC .label+ span").css("::text").extract()
        items['floors'] = response.css(".hDXzwZ .label+ span").css("::text").extract() #Different
        items['direction'] = response.css(".iCmNyo .label+ span").css("::text").extract()
        items['balcony_direction'] = response.css(".fxooPS .label+ span").css("::text").extract()
        items['law_doc'] = response.css(".cizefY .label+ span").css("::text").extract()
        yield items