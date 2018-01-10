# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()
    dType = scrapy.Field()
    vTitle = scrapy.Field()
    vDirector = scrapy.Field()
    vStars = scrapy.Field()
    vType = scrapy.Field()
    vCountry = scrapy.Field()
    vLang = scrapy.Field()
    vInTheatersDate = scrapy.Field()
    vScore = scrapy.Field()
    vDesc = scrapy.Field()
    vCoverUrl = scrapy.Field()
    vDuration = scrapy.Field()
    vEpisodes = scrapy.Field()
    vWriter = scrapy.Field()
    vPlayScript = scrapy.Field()
    vAlias = scrapy.Field()
    vPageTitle = scrapy.Field()
    vPlayList = scrapy.Field()
    vPlayLinks = scrapy.Field()

