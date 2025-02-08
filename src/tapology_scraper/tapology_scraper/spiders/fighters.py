import scrapy


class FightersSpider(scrapy.Spider):
    name = "fighters"
    allowed_domains = ["tapology.com"]
    start_urls = ["https://tapology.com"]

    def parse(self, response):
        pass
