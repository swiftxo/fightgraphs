# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UfcstatsScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class UfcStatsFighterItem(scrapy.Item):
    hash = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    nickname = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    reach = scrapy.Field()
    stance = scrapy.Field()
    wins = scrapy.Field()
    losses = scrapy.Field()
    draws = scrapy.Field()
    champ = scrapy.Field()
    fighter_link = scrapy.Field()
    fights = scrapy.Field()