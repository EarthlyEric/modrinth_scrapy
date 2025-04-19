# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ModsMetadataItem(scrapy.Item):
    icon_url = scrapy.Field()
    name = scrapy.Field()
    mod_url = scrapy.Field()
    author = scrapy.Field()
    author_url = scrapy.Field()
    description = scrapy.Field()
    categories = scrapy.Field()
    environment = scrapy.Field()
    loaders = scrapy.Field()
    downloads = scrapy.Field()
    followers = scrapy.Field()
    