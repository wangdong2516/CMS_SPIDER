本项目是一个服务于CMS项目的爬虫，主要是爬取招聘网站的职位信息，将数据作为CMS的上游来源

爬虫主要爬取boss和拉钩两家网站(后期可能增加对其他网站数据的爬取)

> Python版本

3.8

>技术栈

scrapy爬虫框架+httpx(异步请求库)+pymysql(mysql数据库)

> 虚拟环境(Conda)

1. 创建虚拟环境: `conda create -n name python=3.8`
2. 激活虚拟环境: `conda activate name`
3. 退出虚拟环境: `conda deactivate`

> 依赖管理工具(Poetry)

1. 安装依赖: `poetry install`
2. 添加依赖: `poetry add package_name`
3. 卸载依赖: `poetry remove package_name`
4. 锁定版本: `poetry lock`
5. 更多的使用请参考poetry官方文档: `https://python-poetry.org/docs/`

> 运行项目

scrapy crawl boss


`TODO`
1. 爬取免费代理网站，增加代理池
2. 完成boss列表页面数据的爬虫