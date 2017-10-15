import scrapy


class ArticleSpider(scrapy.Spider):
    name = 'article'

    start_page = 1000
    current_page = start_page
    max_page = 1001

    start_urls = [
        'https://www.ithome.com/ithome/getajaxdata.aspx?page='+str(start_page)+'&type=indexpage',
    ]

    def parse(self, response):
        # follow links to article pages
        article_links = response.css('.block h2 a::attr(href)')
        for href in article_links:
            yield response.follow(href, self.parse_article)
        if len(article_links) > 0 and self.current_page < self.max_page:
            print('当前连接数 >>> ', len(article_links))
            next_url = self.next_page_url()
            print('下一页 >>> ', next_url)
            yield response.follow(next_url, self.parse)

    def parse_article(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        data = {
            'response_info': {
                'url': response.url,
                'status': response.status,
            },
            'article_url': response.url,                                                            # 文章链接
            'http_code': response.status,                                                           # 请求状态码
            'title': extract_with_css('.post_title h1::text'),                                      # 文章标题
            'editor': response.xpath('id("editor_baidu")/strong/text()').extract_first(),           # 责编
            'source': response.xpath('id("source_baidu")/a[1]/text()').extract_first(),             # 来源
            'source_url': response.xpath('id("source_baidu")/a[1]/@href').extract_first(),          # 来源地址
            'author': response.xpath('id("author_baidu")/strong/text()').extract_first(),           # 作者
            'tags': response.xpath('id("wrapper")/div[1]/div[8]/div[1]/div[1]/span[1]/a/text()').extract(),     # 关键词
            'time': response.xpath('id("pubtime_baidu")/text()').extract_first(),                   # 发布时间
        }

        if data['source'] is None:
            data['source'] = response.xpath('id("source_baidu")/text()').extract_first()[3:]

        yield data

    def next_page_url(self):
        self.current_page += 1
        return 'https://www.ithome.com/ithome/getajaxdata.aspx?page='+str(self.current_page)+'&type=indexpage'


class CommentCountSpider(scrapy.Spider):

    name = 'commentCount'

    def parse(self, response):
        yield {

        }