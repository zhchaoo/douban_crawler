# -*- coding: utf-8 -*-
# !/usr/bin/python

import json
import urllib
import shutil
import os
from StringIO import StringIO

import requests
from PIL import Image

dir_path = 'meta_data'


def read_from_json(file_name):
    with open(file_name) as data_file:
        data = json.load(data_file)
        return data


def download_image(url, title, type, director):
    img_type = url.split('.')[-1]
    img_name = type + '_' + title + '_' + director
    img_name = img_name.replace('/', '|s|')
    img_path = os.path.join(dir_path, img_name + '.' + img_type)

    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36',
            'Accept-Encoding': 'deflate',
            'Refer': 'https://movie.douban.com/subject/'
        }, stream=True)
        if response.status_code == 200:
            with open(img_path, 'wb') as f:
                response.raw.decode_content = True
                #f.write(response.content)
                #f.flush()
                shutil.copyfileobj(response.raw, f)
        else:
            print 'pic download ' + response.status_code + ' [' + title + '] url [' + url + ']'
    except Exception as e:
        print 'pic download fail [' + title + '] url [' + url + '] msg:' + e.message
        return False
    print 'pic download success [' + title + ']'
    return True


if __name__ == "__main__":
    data = read_from_json("./meta_data/search_all.json")
    for item in data:
        download_image(item['vCoverUrl'], item['vTitle'], item['type'], item['vDirector'])


