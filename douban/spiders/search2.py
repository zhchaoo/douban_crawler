# -*- coding: utf-8 -*-
import logging
import sys

import scrapy
from scrapy_splash import SplashRequest

import douban.utils as utils
from douban.items import DoubanItem
from douban.keywords import *

reload(sys)
sys.setdefaultencoding('utf-8')


class Search2Spider(scrapy.Spider):
    name = 'search2'
    allowed_domains = ['douban.com']
    allowed_types = [u'电影', u'电视剧']
    splash_args = {
        'splash': {
            'args': {
                # set rendering arguments here
                'html': 1,
                'wait': 1,
                # 'url' is prefilled from request url
                # 'http_method' is set to 'POST' for POST requests
                # 'body' is set to request body for POST requests

                # optional parameters
                'dont_send_headers': False,  # optional, default is False
            },
        }
    }
    # search_url = 'https://www.douban.com/search?q='
    search_url = 'https://movie.douban.com/subject_search?search_text='
    search_keywords = keywords_wl2
    # search_keywords = [u'亲爱的客栈']

    def start_requests(self):
        for keyword in self.search_keywords:
            request = SplashRequest(self.search_url + keyword,
                                    self.parse,
                                    args={
                                        # optional; parameters passed to Splash HTTP API
                                        'wait': 0.5,
                                        'html': 1,

                                        # 'url' is prefilled from request url
                                        # 'http_method' is set to 'POST' for POST requests
                                        # 'body' is set to request body for POST requests
                                    })
            request.headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            }

            yield request

    def parse(self, response):
        result_list = response.xpath('//div[@class="detail"]/div[@class="title"]')
        for result in result_list:
            try:
                v_type = result.xpath('span/text()').extract()[0].replace('[', '').replace(']', '')
                v_type = u'剧集' in v_type and '电视剧' or '电影'
                v_title = result.xpath('a/text()').extract()[0]
                url = result.xpath('a/@href').extract()[0]
                url = utils.get_real_url(url)
                if v_type not in self.allowed_types:
                    continue
                # if not v_title.startswith(response.meta['title']):
                #     continue
            except Exception:
                continue

            request = scrapy.Request(response.urljoin(url),
                                     callback=self.parse_video,
                                     errback=self.err_back,
                                     dont_filter=True)
            request.meta['type'] = v_type
            yield request

    def parse_video(self, response):
        item = DoubanItem()
        item['dType'] = 'META_VIDEO_S1'
        try:
            item['url'] = response.url
            item['type'] = response.meta['type']
            item['vTitle'] = response.xpath("//title/text()").extract()[0].replace(u' (豆瓣)', '').strip()
            item['vCoverUrl'] = response.xpath("//div[@id='mainpic']//img/@src").extract()[0]
            info = ''.join(response.xpath("//div[@id='info']//text()").extract())
        except Exception as e:
            logging.error('No primary info:' + response.url + ' except:' + e.message)
            return

        info_map = {
            'vDirector': u'导演: ',
            'vStars': u'主演: ',
            'vType': u'类型: ',
            'vCountry': u'制片国家/地区: ',
            'vLang': u'语言: ',
            'vWriter': u'编剧: ',
            'vAlias': u'又名: '
        }
        for k, v in info_map.items():
            try:
                sub_info = info.split(v)
                item[k] = sub_info and len(sub_info) > 1 and sub_info[1].split('\n')[0].strip() or ''
            except Exception as e:
                logging.error('No set info:' + response.url + ' except:' + e.message)
        # format cast and director as same rule as movie
        try:
            item['vDirector'] = item['vDirector'].split('/')[0].strip()
            item['vStars'] = '/'.join(map(lambda x: x.strip(), item['vStars'].split('/')))
        except Exception as e:
            logging.error('format director and stars error:' + response.url + ' except:' + e.message)

        info_map = {
            'vScore': "//strong[@property='v:average']/text()",
            'vInTheatersDate': "//span[@property='v:initialReleaseDate']/text()",
            'vDesc': "//span[@property='v:summary']/text()",
            'vPageTitle': "//div[@id='content']/h1/span[1]/text()",
        }
        for k, v in info_map.items():
            try:
                item[k] = response.xpath(v).extract()[0].strip()
            except Exception as e:
                item[k] = ''
                logging.error('No other info:' + response.url + ' except:' + e.message)

        try:
            if item['type'] == u'电视剧':
                item['vPlayScript'] = response.xpath("//body/script[contains(@src, 'mixed_static')]/@src").extract()[0]
                sub_info = info.split(u'集数: ')
                item['vEpisodes'] = sub_info and len(sub_info) > 1 and sub_info[1].split('\n')[0].strip() or ''
                sub_info = info.split(u'单集片长: ')
                item['vDuration'] = sub_info and len(sub_info) > 1 and sub_info[1].split('\n')[0].strip() or ''
            else:
                item['vDuration'] = response.xpath("//span[@property='v:runtime']/text()").extract()[0]
        except Exception as e:
            logging.error('No other info:' + response.url + ' except:' + e.message)

        # play list
        try:
            plays = response.xpath("//div[@class='gray_ad']//ul[@class='bs']/li")
            play_list = []
            for play in plays:
                play_item = {}
                pay = play.xpath("span[@class='buylink-price']/span/text()").extract()
                s_name = play.xpath("a/text()").extract()
                url = play.xpath("a/@href").extract()
                if pay and s_name:
                    play_item['pay'] = pay[0].strip()
                    play_item['sName'] = s_name[0].strip()
                    if url and not url[0].startswith('javascript:'):
                        play_item['url'] = url[0]
                    play_list.append(play_item)
            item['vPlayList'] = play_list
        except Exception as e:
            logging.error('No play info:' + response.url + ' except:' + e.message)
        try:
            if item['type'] == u'电视剧':
                play_links = response.xpath("//body/script/text()").re('{play_link:.*}')
                item['vPlayLinks'] = utils.get_link_address(play_links)
                if not item['vPlayLinks'] or len(item['vPlayLinks']) == 0:
                    item['vPlayLinks'] = utils.get_link_address_from_js(item['vPlayScript'])
        except Exception as e:
            logging.error('No play list:' + response.url + ' except:' + e.message)
        yield item

    def err_back(self, failure):
        # log all failures
        self.logger.error(repr(failure))
