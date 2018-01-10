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


def uodoo_image(img_url):
    url = uodoo_url + urllib.quote(img_url) + ',' + urllib.quote(refer_url) + uodoo_save_path
    try:
        response = requests.get(url)
        if response.status_code == 200:
            ret = json.loads(response.content)
            if ret['status'] == 200:
                print 'pic uodoo success [' + img_url + ']'
                return ret['url']
        print 'pic uodoo fail [' + img_url + '] msg:' + response.content
        return img_url
    except Exception as e:
        print 'pic uodoo fail [' + img_url + '] msg:' + str(e)
        return img_url


if __name__ == "__main__":
    data = read_from_json("./meta_all/tv2.json")
    for item in data:
        new_url = uodoo_image(item['vCoverUrl'])
        item['vCoverUrl'] = new_url

    with open('./meta_all/tv2_uodoo.json', 'w') as outfile:
        json.dump(data, outfile)


