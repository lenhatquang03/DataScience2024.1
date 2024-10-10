import scrapy
from scrapy.http import Response
from typing import Any
from ..items import CafelandItem

# MAXIMUM NUMBER OF SCRAPED PAGES FOR EACH PROPERTY TYPE IS AS FOLLOW: 384 (DONE), 384 (DONE), 239, 384 (DONE), 0 (NO RESULTS)

class RealEstateSpider(scrapy.Spider):
    name = "RealEstate"
    BASE_URL = "https://nhadat.cafeland.vn/nha-dat-ban/"
    PROPERTY_TYPES = ["nha rieng", "nha pho du an", "biet thu", "can ho chung cu", "can ho mini dich vu"]

    def __init__(self, city: str, property_type: str, page_limit: int, **kwargs: Any):
        super().__init__(**kwargs)
        self.pages_crawled = 0
        self.items_scraped = 0
        self.city = city
        self.property_type = property_type
        self.page_limit = page_limit
        self.start_urls =  RealEstateSpider.create_startURL(self.city, self.property_type)

    @staticmethod
    def create_startURL(city: str, property_type: str) -> list:
        """ Return the URL(s) holding all information of different real estate in a city. """
        if bool(city) and bool(property_type):
            relative_link = "ban {} tai {}/page-1/".format(property_type, city).replace(" ", "-")
            absolute_link = RealEstateSpider.BASE_URL + relative_link
            return [absolute_link]

        elif bool(city) and  not bool(property_type):
            relative_links = ["ban {} tai {}/page-1/".format(house_type, city).replace(" ", "-")
                              for house_type in RealEstateSpider.PROPERTY_TYPES]
            absolute_links = [(RealEstateSpider.BASE_URL + link) for link in relative_links]
            return absolute_links

        elif not bool(city) and bool(property_type):
            relative_link = "ban {}/page-1/".format(property_type).replace(" ", "-")
            absolute_link = [RealEstateSpider.BASE_URL + relative_link]
            return absolute_link

        else:
            return [RealEstateSpider.BASE_URL + "page-1/"]

    def parse(self, response: Response) -> Any:
        """ Traverse through every webpages and follow all property links. """
        # Following all properties' links
        page_links = response.css(".realTitle::attr(href)").extract()
        for link in page_links:
            yield scrapy.Request(link, callback = self.parse_property)


        # Update page's number and traverse to the next page.
        page_num = response.url.split("page-")[1][:-1] # Since the page number can have more than 1 digit.
        print("WE ARE AT PAGE: ", page_num)
        curr_page_number = int(page_num) if page_num.isdigit() else 1
        next_page_number = curr_page_number + 1
        next_page = response.url.replace(f"page-{curr_page_number}", f"page-{next_page_number}")

        if next_page_number <= int(self.page_limit):
            yield response.follow(next_page, callback = self.parse)

    def parse_property(self, response: Response) -> CafelandItem:
        """ Scraping chosen information of a particular property. """
        items = CafelandItem()
        items["title"] = response.css(".head-title::text").extract()
        items["address"] = response.css(".infor div+ div::text").extract()
        items["post_update"] = response.css(".col-right i::text").extract()
        items["price"] = response.css(".col-item:nth-child(1) .infor-data").css("::text").extract()
        items["area"] = response.css(".col-item+ .col-item .infor-data").css("::text").extract()
        items["description"] = response.css(".reals-description .content").css("::text").extract()
        items["property_type"] = response.css(".opt-mattien .value-item").css("::text").extract()
        items["direction"] = response.css(".opt-huongnha .value-item").css("::text").extract()
        items["floors"] = response.css(".opt-sotang .value-item").css("::text").extract()
        items["bathrooms"] = response.css(".opt-sotoilet .value-item").css("::text").extract()
        items["entrance"] = response.css(".opt-duong .value-item").css("::text").extract()
        items["livingrooms"] = response.css(".opt-bancong .value-item").css("::text").extract()
        items["bedrooms"] = response.css(".opt-sopngu .value-item").css("::text").extract()
        items["law_doc"] = response.css(".opt-phaply .value-item").css("::text").extract()
        items["location"] = response.css(".reals-map .content").css("::attr(src)").extract()
        yield items