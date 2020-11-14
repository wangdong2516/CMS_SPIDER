import random

import httpx
import scrapy
import time
from scrapy import Request
from scrapy.http import TextResponse

from cms_scrapy.items import JobItem

# 代理池
PROXY_http = [
    '153.180.102.104:80',
    '195.208.131.189:56055',
]
PROXY_https = [
    '120.83.49.90:9000',
    '95.189.112.214:35508',
]


class BossSpider(scrapy.Spider):
    """
        腾讯视频爬虫
    """

    # 定义爬虫的名称，必须是唯一的
    name = 'boss'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    }

    def make_headers(self):
        """构造请求头"""
        USER_AGENT_LIST = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
            "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        headers = {
            "user-agent": random.choice(USER_AGENT_LIST)
        }
        return headers

    def start_requests(self):

        # 定义起始的url，作为爬取点
        urls = [
            'https://www.zhipin.com/beijing/',
            'http://www.zhipin.com/'
        ]

        for url in urls:
            self.headers['proxy'] = random.choice(PROXY_http)
            time.sleep(5)
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, **kwargs):
        """
            页面解析函数
        :param response:
        :param kwargs:
        :return:
        """
        # 提取综艺标签的href属性
        jobs = response.xpath('//div[@class="job-menu"]//a/text()')
        jobs_link = response.xpath('//div[@class="job-menu"]//a/@href')
        # 提取数据,extra获取的是列表，extra_first获取的是字符串
        job_list = jobs.extract()

        # 职位链接
        links = jobs_link.extract()
        job_item = JobItem()
        for job, link in zip(job_list, links):
            job_item['name'] = job
            job_item['url'] = response.urljoin(link)
            job_item['source'] = 'boss'
            yield job_item

        for url in links:
            # 这里因为爬虫速度太快可能会导致IP被封，所以手动使用httpx发起请求
            self.headers['proxy'] = random.choice(PROXY_http)
            httpx_response = httpx.get(url=response.urljoin(url), headers=self.make_headers())
            scarpy_response = TextResponse(url=str(response.urljoin(url)), body=httpx_response.text, encoding='utf8')
            jobs = scarpy_response.xpath('//div[@class="job-limit clearfix"]//p/text()[1]').extract()

    def parse_position(self, response, **kwargs):
        # 职位薪资
        salary = response.xpath('//div[@class="job-limit clearfix"]/span/text()')
        # 工作经验
        work_experience = response.xpath('//div[@class="job-limit clearfix"]/p/text()[1]')
        # 学历要求
        education_background = response.xpath('//div[@class="job-limit clearfix"]//p/text()[2]')
        print(work_experience, education_background)



