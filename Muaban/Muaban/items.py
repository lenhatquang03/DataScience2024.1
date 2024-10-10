# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class MuabanItem(scrapy.Item):
    title = scrapy.Field()
    address = scrapy.Field()
    price = scrapy.Field()
    briefing = scrapy.Field()
    property_type = scrapy.Field()
    area = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    floors = scrapy.Field()
    direction = scrapy.Field()
    balcony_direction = scrapy.Field()
    law_doc = scrapy.Field()
