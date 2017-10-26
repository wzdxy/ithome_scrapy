import scrapy
import pymongo
import re
from .. import config


class ArticleSpider(scrapy.Spider):
    name = 'article'

    start_page = 1
    current_page = start_page
    max_page = 6000

    start_urls = [
        'https://www.ithome.com/ithome/getajaxdata.aspx?page=' + str(start_page) + '&type=indexpage',
    ]

    def parse(self, response):
        # follow links to article pages
        article_links = response.css('.block h2 a::attr(href)')
        for href in article_links:
            yield response.follow(href, self.parse_article)
        if len(article_links) > 0 and self.current_page < self.max_page:
            print(response.status, ' 当前页 >>> ', self.current_page, ' 本页连接数 >>> ', len(article_links))
            next_url = self.next_page_url()
            print('下一页 >>> ', next_url)
            yield response.follow(next_url, self.parse)

    def parse_article(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        data = {
            'article_url': response.url,  # 文章链接
            'http_code': response.status,  # 请求状态码
            'title': extract_with_css('.post_title h1::text'),  # 文章标题
            'editor': response.xpath('id("editor_baidu")/strong/text()').extract_first(),  # 责编
            'source': response.xpath('id("source_baidu")/a[1]/text()').extract_first(),  # 来源
            'source_url': response.xpath('id("source_baidu")/a[1]/@href').extract_first(),  # 来源地址
            'author': response.xpath('id("author_baidu")/strong/text()').extract_first(),  # 作者
            'tags': response.xpath('id("wrapper")/div[1]/div[8]/div[1]/div[1]/span[1]/a/text()').extract(),  # 关键词
            'time': response.xpath('id("pubtime_baidu")/text()').extract_first(),  # 发布时间
            'last_nav': response.xpath('id("wrapper")/div[1]/div[1]/a[3]/@href').extract_first(),  # 最后一级导航
            'content_paragraphs': response.xpath('id("paragraph")/p/text()').extract()  # 正文段落
        }

        if data['source'] is None:
            data['source'] = response.xpath('id("source_baidu")/text()').extract_first()[3:]

        yield data

    def next_page_url(self):
        self.current_page += 1
        return 'https://www.ithome.com/ithome/getajaxdata.aspx?page=' + str(self.current_page) + '&type=indexpage'


class CommentCountSpider(scrapy.Spider):
    name = 'commentCount'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.db = self.client[config.db_name]
        self.collection = self.db[config.article_collection_name]
        self.all_article()

    start_urls = []

    def parse(self, response):
        article_id = int(re.findall(r"\d+", response.url)[0])
        comment_count = int(re.findall(r"\d+", response.body_as_unicode())[0])
        yield {
            'article_id': article_id, 'comment_count': comment_count
        }

    def all_article(self):
        articles = self.collection.find() #{'article_id': {'$gt': '311000', '$lt': '311111'}}
        for article in articles:
            self.start_urls.append('https://dyn.ithome.com/api/comment/count?newsid=' + str(article['article_id']))
        print(len(self.start_urls))


class GradeSpider(scrapy.Spider):
    name = 'grade'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.db = self.client[config.db_name]
        self.collection = self.db[config.article_collection_name]
        self.all_article()

    start_urls = []

    def parse(self, response):
        article_id = int(re.findall(r"\d+", response.url)[0])
        print(article_id)
        grade = float(response.xpath('/html[1]/body[1]/div[1]/div[1]/span[1]/span[1]/text()').extract_first())
        grade_people_count = int(re.findall(r"\d+", response.xpath('/html[1]/body[1]/div[1]/div[1]/span[3]/text()').extract_first())[0])
        print({
            'article_id': article_id,
            'grade': grade,
            'grade_people_count': grade_people_count
        })
        yield {
            'article_id': article_id,
            'grade': grade,
            'grade_people_count': grade_people_count
        }

    def all_article(self):
        articles = self.collection.find() #{'article_id': {'$gt': '2400', '$lt': '2600'}}
        for article in articles:
            self.start_urls.append('https://dyn.ithome.com/grade/' + str(article['article_id']))
        print(self.start_urls)
