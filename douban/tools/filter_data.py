# -*- coding: utf-8 -*-
# !/usr/bin/python

import json
import urllib
import shutil
import os

import requests

dir_path = 'meta_data'

refer_url = 'https://movie.douban.com/subject/'
uodoo_url = 'http://bq-spider.peco.uodoo.com/r/radar/;0,,?r2='
uodoo_save_path = '&save=img/buz/1004'


def read_from_json(file_name):
    with open(file_name) as data_file:
        data = json.load(data_file)
        return data


def filter_item(item):
    try:
        if item['vTitle'].contains(u'战狼'):
            return True
        return False
    except Exception as e:
        print 'filter fail [' + item['vTitle'] + '] msg:' + str(e)
        return False


if __name__ == "__main__":
    data = read_from_json("./meta_data/search_all_uodoo_flush.json")
    new_data = []
    print len(data)
    for item in data:
        if filter_item(item):
            new_data.push(item)

    with open('./meta_data/search_all_uodoo_flush_filter.json', 'w') as outfile:
        json.dump(data, outfile)


