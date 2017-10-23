# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from . import config


class preHandleData(object):
    def process_item(self, item, spider):
        if spider.name == 'article':
            # 标记是否原创
            item['original'] = item['author'] == item['editor']

            # 处理时间
            import time
            times = dict(
                zip(['tm_year', 'tm_mon', 'tm_mday', 'tm_hour', 'tm_min', 'time_sec', 'tm_wday', 'tm_yday', 'tm_isdst'],
                    list(time.strptime(item['time'], '%Y-%m-%d %H:%M:%S'))))
            item = {**item, **times}

            # 拆分文章 URL , ['http:', '', 'www.ithome.com', 'html', 'digi', '266330.htm']
            url_array = item['article_url'].split('/')

            # 提取文章 ID
            item['article_id'] = int(url_array[-1].split('.')[0])

            # 拆分导航 URL
            breadcrumb_array = item['last_nav'].split('/')

            # 板块 ID
            item['forum_id'] = breadcrumb_array[2].split('.')[0]

            # 话题 ID
            item['topic_id'] = breadcrumb_array[-2]

            # 处理正文
            item['content_text'] = "\n".join(item['content_paragraphs'])
            item['content_length'] = len(item['content_text'])

            return item
        return item


class saveArticleToMongo(object):
    def open_spider(self, spider):
        if spider.name=='article':
            self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
            self.db = self.client[config.db_name]
            self.collection = self.db[config.article_collection_name]

    def process_item(self, item, spider):
        if spider.name =='article':
            if not self.collection.insert(item):
                print('失败')
        return item


class saveCommentCountToMongo(object):
    def open_spider(self, spider):
        if spider.name == 'commentCount':
            self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
            self.db = self.client[config.db_name]
            self.collection = self.db[config.article_collection_name]

    def process_item(self, item, spider):
        if spider.name == 'commentCount':
            print(item)
            self.collection.find_one_and_update({'article_id': str(item['article_id'])},
                                                    {'$inc': {'comment_count': item['comment_count']}})
        return item


class saveGradeToMongo(object):
    def open_spider(self, spider):
        if spider.name == 'grade':
            self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
            self.db = self.client[config.db_name]
            self.collection = self.db[config.article_collection_name]

    def process_item(self, item, spider):
        if spider.name == 'grade':
            print(item)
            self.collection.find_one_and_update({'article_id': str(item['article_id'])},
                                                    {'$inc': {'grade': item['grade'],
                                                              'grade_people_count': item['grade_people_count']}})
