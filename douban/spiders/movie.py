# -*- coding: utf-8 -*-
import scrapy
import logging
import json
import douban.utils as utils

from douban.items import DoubanItem

logging.basicConfig(filename='tv.log', level=logging.INFO)


class MovieSpider(scrapy.Spider):
    name = 'movie'
    allowed_domains = ['douban.com']
    start_urls = {
        #'https://movie.douban.com/j/new_search_subjects?sort=R&range=0,5.5&tags=%E7%94%B5%E5%BD%B1': 8400,
        #'https://movie.douban.com/j/new_search_subjects?sort=R&range=5.6,6.3&tags=%E7%94%B5%E5%BD%B1': 8900,
        #'https://movie.douban.com/j/new_search_subjects?sort=R&range=6.4,6.8&tags=%E7%94%B5%E5%BD%B1': 9100,
        #'https://movie.douban.com/j/new_search_subjects?sort=R&range=6.9,7.3&tags=%E7%94%B5%E5%BD%B1': 9800,
        'https://movie.douban.com/j/new_search_subjects?sort=R&range=7.4,7.7&tags=%E7%94%B5%E5%BD%B1': 8300,
        'https://movie.douban.com/j/new_search_subjects?sort=R&range=7.8,8.4&tags=%E7%94%B5%E5%BD%B1': 9500,
        'https://movie.douban.com/j/new_search_subjects?sort=R&range=8.5,10.0&tags=%E7%94%B5%E5%BD%B1': 5200
    }

    def start_requests(self):
        return [scrapy.Request("https://accounts.douban.com/login", meta={'cookiejar': 1}, callback=self.post_login)]

    def post_login(self, response):
        return [scrapy.FormRequest.from_response(response,
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 formdata={
                                                     'form_email': utils.login_name,
                                                     'form_password': utils.login_passwd
                                                 },
                                                 callback=self.check_login,
                                                 dont_filter=True)]

    def check_login(self, response):
        print response.url
        try:
            image = response.xpath('//*[@id="captcha_image"]/@src')[0].extract()
            print 'use check pic: '+image
            captchaid = response.xpath('//*[@id="lzform"]/div[6]/div/div/input[2]/@value')[0].extract()
            print captchaid
            if utils.get_captcha_image(image):
                print 'input check num'
                checkup = raw_input('Please input:')
                print 'get:'+str(checkup)
                return [scrapy.FormRequest(response.url,
                                           meta={'cookiejar': 1},
                                           formdata={
                                               'form_email': utils.login_name,
                                               'form_password': utils.login_passwd,
                                               'captcha-id': captchaid,
                                               'captcha-solution': checkup
                                           },
                                           callback=self.check_login,
                                           dont_filter=True)]
            else:
                return None

        except IndexError, e:
            print response.url
            print 'seem load success'
            return [scrapy.Request('https://movie.douban.com/chart',
                                   meta={'cookiejar': response.meta['cookiejar']},
                                   callback=self.get_list,
                                   dont_filter=True)]

    def get_list(self, response):
        for k, v in self.start_urls.items():
            for i in range(0, v, 20):
                request = scrapy.Request(k + '&start=' + str(i),
                                         meta={'cookiejar': response.meta['cookiejar']},
                                         callback=self.parse,
                                         errback=self.err_back,
                                         dont_filter=True)
                request.meta['type'] = u'电影'
                yield request

    def parse(self, response):
        json_obj = json.loads(response.text)
        if 'data' not in response.text:
            logging.error('No data in json api:' + response.url)
        result_list = json_obj['data']
        for result in result_list:
            try:
                item = DoubanItem()
                url = result['url']
                url = utils.get_real_url(url)
                item['url'] = url
                item['dType'] = 'META_VIDEO_S1'
                item['type'] = response.meta['type']
                item['vTitle'] = result['title']
                item['vScore'] = result['rate']
                item['vCoverUrl'] = result['cover']
                item['vDirector'] = result['directors'] and result['directors'][0] or ''
                item['vStars'] = '/'.join(result['casts'])

                # request
                request = scrapy.Request(response.urljoin(url),
                                         meta={'cookiejar': response.meta['cookiejar']},
                                         callback=self.parse_video,
                                         errback=self.err_back)
                request.meta['item'] = item
                yield request
            except Exception as e:
                logging.error('Item in json api error:' + response.url + ' item url:' + url)
                continue

    def parse_video(self, response):
        item = response.meta['item']
        try:
            info = ''.join(response.xpath("//div[@id='info']//text()").extract())
        except Exception as e:
            logging.error('No primary info:' + response.url + ' except:' + e.message)
            return

        info_map = {
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
                item['vEpisodes'] = sub_info and len(sub_info) > 1 and sub_info[1].split('\n')[0].strip()
                sub_info = info.split(u'单集片长: ')
                item['vDuration'] = sub_info and len(sub_info) > 1 and sub_info[1].split('\n')[0].strip()
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
                sName = play.xpath("a/text()").extract()
                url = play.xpath("a/@href").extract()
                if pay and sName:
                    play_item['pay'] = pay[0].strip()
                    play_item['sName'] = sName[0].strip()
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
