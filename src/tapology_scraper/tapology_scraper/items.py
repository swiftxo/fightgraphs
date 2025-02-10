# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TapologyInitialFighterItem(scrapy.Item):
    hash = scrapy.Field()
    tapology_link = scrapy.Field()
    height = scrapy.Field()
    weightclass = scrapy.Field()
    record = scrapy.Field()
    nationality = scrapy.Field()



class TapologyPromotionItem(scrapy.Item):
    hash = scrapy.Field()
    promotion_name = scrapy.Field()
    promotion_link = scrapy.Field()
    headquarters = scrapy.Field()
    social_media_links = scrapy.Field()

class TapologyEventItem(scrapy.Item):
    hash = scrapy.Field()
    promotion_link = scrapy.Field()
    event_link = scrapy.Field()
    event_name = scrapy.Field()
    fights = scrapy.Field()
    fighters = scrapy.Field()
    event_date = scrapy.Field()
    event_location = scrapy.Field()
    event_details = scrapy.Field()
    
