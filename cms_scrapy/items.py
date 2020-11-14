# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = Field()
    job_type = Field()
    url = Field()
    source = Field()
    work_experience = Field()
    degree = Field()
    salary = Field()
