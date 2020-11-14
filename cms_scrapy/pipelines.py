# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from dbutils.pooled_db import PooledDB


# 5为连接池里的最少连接数，setsession=['SET AUTOCOMMIT = 1']是用来设置线程池是否打开自动更新的配置，0为False，1为True
pool = PooledDB(
    pymysql, host='127.0.0.1', user='root',
    passwd='1277431229', db='CMS_SPIDER', port=3306,
    mincached=3, setsession=['SET AUTOCOMMIT = 1']
)


class BossItemPipeline:

    def __init__(self):
        # 建立连接
        self.conn = pool.connection()
        # 获取游标对象
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        """
            处理数据
        """
        # 插入数据
        sql = """
            INSERT INTO `position` (
                `name`, `job_type`, `url`, `source`,
                `work_experience`, `degree`, `salary`,
                `create_time`, `update_time`
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        self.cursor.execute(
            sql, [item['name'], item['job_type'], item['url'], item['source'], item['work_experience'], item['degree'], item['salary']]
        )
        self.conn.commit()
        return item

    def close_spider(self, spider):
        """
            Spider关闭时（处理数据后）回调该方法，通常该方法用于在处理完所有数据之后完成某些清理工作，如关闭数据库
        """
        self.cursor.close()
        self.conn.close()