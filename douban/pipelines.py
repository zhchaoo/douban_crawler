# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2

from django.core.serializers import json
from scrapy.exporters import CsvItemExporter

from douban.items import DoubanItem


class MetaPostPipeline(object):
    def process_item(self, item, spider):
        payload = dict(item)

        try:
            post_url = spider.settings.get('POST_URL')
            req = urllib2.Request(post_url)
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, json.dumps(payload))
            spider.log(response.read() + ' title:' + item['title'] + ' payload:' + str(payload))
        except Exception as e:
            spider.log('Post exp:' + e.message + ' title:' + item['title'] + ' url:' + item['url'])

        return item


class MultiCSVItemPipeline(object):
    SaveTypes = ['meta']

    @staticmethod
    def item_type(item):
        if isinstance(item, DoubanItem):
            return 'meta'
        else:
            return 'unknown'

    def open_spider(self, spider):
        spider_name = spider.name
        self.out_files = dict([(name, open(spider_name + '_' + name + '.csv', 'w+b')) for name in self.SaveTypes])
        self.exporters = dict([(name, CsvItemExporter(self.out_files[name])) for name in self.SaveTypes])
        [e.start_exporting() for e in self.exporters.values()]

    def close_spider(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.out_files.values()]

    def process_item(self, item, spider):
        what = MultiCSVItemPipeline.item_type(item)
        if what in set(self.SaveTypes):
            self.exporters[what].export_item(item)

        return item
