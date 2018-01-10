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


def flush_data(item):
    try:
        dictor = item['vDirector']
        starts = item['vStars']
        starts_list = map(lambda x: x.strip(), starts.split('/'))
        item['vDirector'] = dictor.split('/')[0].strip()
        item['vStars'] = '/'.join(starts_list)
        return item
    except Exception as e:
        print 'flush fail [' + item['vTitle'] + '] msg:' + str(e)
        return item


if __name__ == "__main__":
    data = read_from_json("./meta_data/search_all_uodoo.json")
    print len(data)
    for item in data:
        item = flush_data(item)

    with open('./meta_data/search_all_uodoo_flush.json', 'w') as outfile:
        json.dump(data, outfile)


