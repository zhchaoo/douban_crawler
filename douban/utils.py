# -*- coding: utf-8 -*-
import json
import logging
import urllib
import re

from PIL import Image

play_link_pattern = re.compile('{play_link:.*}', re.MULTILINE)
login_name = ''
login_passwd = ''


def get_link_address(play_links):
    link_addrs = []
    for link in play_links:
        try:
            json_obj = json.loads(link.replace('play_link', '"play_link"').replace('ep', '"ep"'))
            if 'play_link' in json_obj and 'ep' in json_obj:
                link_addrs.append({'ep': json_obj['ep'], 'url': json_obj['play_link']});
        except Exception as e:
            logging.error("extract play list err:" + e.message)
    return link_addrs


def get_link_address_from_js(js_url):
    if not js_url:
        return []

    content = urllib.urlopen(js_url).read()
    play_links = play_link_pattern.findall(content)
    return get_link_address(play_links)


def get_real_url(url):
    if 'url=' in url:
        start_pos = url.find('url=') + 4
        end_pos = url.find('&query', start_pos)
        url = urllib.unquote(url[start_pos:end_pos])
        return url
    elif 'b?r=' in url:
        start_pos = url.find('b?r=') + 4
        url = urllib.unquote(url[start_pos:])
        return url

    return url


def get_captcha_image(url):
    img_url = url+'.jpeg'
    img_name = 'check.jpeg'
    try:
        urllib.urlretrieve(img_url, img_name)
        img = Image.open(img_name)
        img.show()
    except Exception as e:
        logging.error('check pic download fail...:' + e.message)
        return False
    print 'check pic download success'
    return True
