import httpx
import random
from scrapy.http import Response, HtmlResponse


class Crawl(object):

    def __init__(self):
        self.start_url = 'https://www.lagou.com/'



    def crwal_lagou(self):
        response = httpx.get(url=self.start_url, headers=self.make_headers())
        scarpy_response = HtmlResponse(url=str(response.url), body=response.text, encoding='utf8')
        jobs = scarpy_response.xpath('//div[@class="menu_main job_hopping"]//a/h3/text()').extract()
        print(jobs)








if __name__ == '__main__':
    crawl = Crawl()
    crawl.crwal_lagou()
