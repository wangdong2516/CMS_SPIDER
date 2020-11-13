from scrapy import cmdline

cmdline.execute(['scrapy', 'crawl', 'boss', '-o', 'test.csv'])