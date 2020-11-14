import random

import httpx
import scrapy
import time
import re
from scrapy import Request
from scrapy.http import TextResponse

from cms_scrapy.items import JobItem

# 代理池
PROXY_HTTP = [
    '153.180.102.104:80',
    '195.208.131.189:56055',
]
PROXY_HTTPS = [
    '120.83.49.90:9000',
    '95.189.112.214:35508',
]


class BossSpider(scrapy.Spider):
    """
        拉钩网站爬虫
    """

    # 定义爬虫的名称，必须是唯一的
    name = 'lagou'

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
            'https://www.lagou.com/'
        ]

        for url in urls:
            self.headers['proxy'] = random.choice(PROXY_HTTP)
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, **kwargs):
        """
            页面解析函数
        :param response:
        :param kwargs:
        :return:
        """
        # 提取职位种类(分类)以及没个分类的链接地址
        positions = response.xpath('//div[@class="menu_sub dn"]//a/h3/text()').extract()
        jobs_link = response.xpath('//div[@class="menu_sub dn"]//a/@href').extract()
        job_item = JobItem()
        for job, link in zip(positions, jobs_link):
            url = response.urljoin(link)
            job_item['url'] = url
            job_item['job_type'] = job
            # 这里因为爬虫速度太快可能会导致IP被封，所以手动使用httpx发起请求
            self.headers['proxy'] = random.choice(PROXY_HTTPS)

            # 请求列表页面
            response = self.get_response(url)
            # TODO：这里的xpath表达式不是很精简，导致爬出来的数据有空格和换行符，需要做一些特殊的处理
            experience_salary = response.xpath('//div[@class="li_b_l"]/text()').extract()
            positions = response.xpath('//a[@class="position_link"]/h3/text()').extract()
            salaries = response.xpath('//div[@class="li_b_l"]/span[@class="money"]/text()').extract()

            # 包含下一页的链接
            next_url = response.xpath('//a[@class="page_no"][last()]/@href').extract_first()
            # 对experience_salary进行处理
            work_experience_list, degree_list = self.handle_experience_salary(experience_salary)

            for p, w, d, s in zip(positions, work_experience_list, degree_list, salaries):
                job_item['name'] = p
                job_item['work_experience'] = w
                job_item['degree'] = d
                job_item['salary'] = s
                job_item['source'] = 'lagou'
                yield job_item
            yield Request(url=response.urljoin(next_url), callback=self.parse_next, headers=self.make_headers(), cb_kwargs={'job_type': job})

    def handle_experience_salary(self, experience_salary):
        """处理爬取到的工作经验和薪资"""
        work_experience_list = []
        degree_list = []
        obj = re.compile(r'\n\s*')
        for item in experience_salary:
            if not obj.match(item):
                temp = re.sub(obj, '', item)
                work_experience, *other, degree = temp.split('/')
                work_experience = re.sub(obj, '', work_experience)
                degree = re.sub(obj, '', degree)
                degree = degree.strip(' ')
                work_experience = work_experience.strip(' ')
                work_experience_list.append(work_experience)
                degree_list.append(degree)
        return work_experience_list, degree_list

    def get_response(self, url):
        """获取响应并且构造为scrapy的响应对象"""
        # 职位分类列表页面
        httpx_response = httpx.get(url=url, headers=self.make_headers())
        scarpy_response = TextResponse(url=url, body=httpx_response.text, encoding='utf8')
        return scarpy_response

    def parse_next(self, response, *args, **kwargs):
        """解析下一页"""
        job_item = JobItem()
        self.headers['proxy'] = random.choice(PROXY_HTTPS)
        # TODO：这里的xpath表达式不是很精简，导致爬出来的数据有空格和换行符，需要做一些特殊的处理
        experience_salary = response.xpath('//div[@class="li_b_l"]/text()').extract()
        positions = response.xpath('//a[@class="position_link"]/h3/text()').extract()
        salaries = response.xpath('//div[@class="li_b_l"]/span[@class="money"]/text()').extract()

        # 包含下一页的链接
        next_url = response.xpath('//a[@class="page_no"][last()]/@href').extract_first()
        # 对experience_salary进行处理
        work_experience_list, degree_list = self.handle_experience_salary(experience_salary)

        for p, w, d, s in zip(positions, work_experience_list, degree_list, salaries):
            job_item['name'] = p
            job_item['job_type'] = kwargs['job_type'] if kwargs['job_type'] else 'Unknown'
            job_item['work_experience'] = w
            job_item['degree'] = d
            job_item['salary'] = s
            job_item['source'] = 'lagou'
            job_item['url'] = response.url
            yield job_item
        yield Request(url=response.urljoin(next_url), callback=self.parse_next, headers=self.make_headers(), cb_kwargs={'job_type':  kwargs['job_type']})


    # def crawl_list(self, url, job_item):
    #
    #     response = self.get_response(url)
    #
    #     # TODO：这里的xpath表达式不是很精简，导致爬出来的数据有空格和换行符，需要做一些特殊的处理
    #     experience_salary = response.xpath('//div[@class="li_b_l"]/text()').extract()
    #     positions = response.xpath('//a[@class="position_link"]/h3/text()').extract()
    #     salaries = response.xpath('//div[@class="li_b_l"]/span[@class="money"]/text()').extract()
    #
    #     # 包含下一页的链接
    #     next_url = response.xpath('//a[@class="page_no"][last()]/@href').extract_first()
    #     # 对experience_salary进行处理
    #     work_experience_list, degree_list = self.handle_experience_salary(experience_salary)
    #
    #     for p, w, d, s in zip(positions, work_experience_list, degree_list, salaries):
    #         job_item['name'] = p
    #         job_item['work_experience'] = w
    #         job_item['degree'] = d
    #         job_item['salary'] = s
    #         job_item['source'] = 'lagou'
    #         yield job_item
