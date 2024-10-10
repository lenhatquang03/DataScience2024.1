# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CafelandItem(scrapy.Item):
    title = scrapy.Field()
    address = scrapy.Field()
    post_update = scrapy.Field()
    price = scrapy.Field()
    area = scrapy.Field()
    description = scrapy.Field()
    property_type = scrapy.Field()
    direction = scrapy.Field()
    floors = scrapy.Field()
    bathrooms = scrapy.Field()
    entrance = scrapy.Field()
    livingrooms = scrapy.Field()
    bedrooms = scrapy.Field()
    law_doc = scrapy.Field()
    location = scrapy.Field()