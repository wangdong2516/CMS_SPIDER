from scrapy import cmdline

cmdline.execute(['scrapy', 'crawl', 'lagou', '-o', 'test.csv'])