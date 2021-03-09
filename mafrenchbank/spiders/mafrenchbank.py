import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from mafrenchbank.items import Article


class MafrenchbankSpider(scrapy.Spider):
    name = 'mafrenchbank'
    start_urls = ['https://www.mafrenchbank.fr/mon-french-mag.html']

    def parse(self, response):
        links = response.xpath('//a[@class="cmp-push__link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_pages = response.xpath('//ul[@class="cmp-pagination desktop"]/li/a/@href').getall()
        yield from response.follow_all(next_pages, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="cmp-articledefaultcontent__date"]/span/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="responsivegrid js-tagging"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
