import scrapy
from tapology_scraper.items import TapologyPromotionItem
import logging
from scrapy.exceptions import IgnoreRequest
import os

log_path = '/Users/sohanhossain/Documents/fightgraphs/src/tapology_scraper/logs/promotions_log/'
if not os.path.exists(log_path):
    os.makedirs(log_path)
# Setup loggers
general_logger = logging.getLogger('general')
item_logger = logging.getLogger('item_processing')
proxy_logger = logging.getLogger('proxy_errors')

# Configure loggers
logging.basicConfig(level=logging.DEBUG)
general_handler = logging.FileHandler(f'{log_path}general.log')
item_handler = logging.FileHandler(f'{log_path}item_processing.log')
proxy_handler = logging.FileHandler(f'{log_path}proxy_errors.log')
proxy_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
general_handler.setFormatter(formatter)
item_handler.setFormatter(formatter)
proxy_handler.setFormatter(formatter)

general_logger.setLevel(logging.DEBUG)  
item_logger.setLevel(logging.INFO)     
proxy_logger.setLevel(logging.ERROR)  

general_logger.addHandler(general_handler)
item_logger.addHandler(item_handler)
proxy_logger.addHandler(proxy_handler)




class PromotionsSpider(scrapy.Spider):
    name = "promotions"
    collection = 'scrapy_tapology_promotions'
    allowed_domains = ["tapology.com"]
    start_urls = ["https://www.tapology.com/fightcenter/promotions"]
    page = 1

    def start_requests(self):
        for page in range(1,60): # Already known that there are 59 pages of promotions
            if page == 1:
                url = 'https://www.tapology.com/fightcenter/promotions/'
            else:
                url = f'https://www.tapology.com/fightcenter/promotions?page={page}'
                general_logger.info(f"Starting request for page {page}: {url}")
            try:
                if self.db[self.collection].find_one({'promotion_link': url}):
                    general_logger.info(f"Promotions page {page} already exists in the database. Skipping...")
                    continue
                else:
                    yield scrapy.Request(url, callback=self.parse, errback=self.errback_proxy)
            except Exception as e:
                proxy_logger.error(f"Error in starting request for page {page}: {e} for spider {self.name}")


    
    def parse(self, response):
        promotions_list = response.xpath("//ul[@class='promotions']/li")
        general_logger.info(f"Parsing {len(promotions_list)} promotions from {response.url}")
        
        for li in promotions_list:
            promotion_name = li.xpath(".//div[@class='name']//a/text()").get()
            promotion_link = li.xpath(".//div[@class='name']//a/@href").get()
            promotion_headquarters = li.xpath(".//div[@class='headquarters']//img/@src").get()
            social_media_links = li.xpath(".//div[@class='links']//a/@href").getall()
            
            promotion = TapologyPromotionItem()
            promotion['promotion_name'] = promotion_name
            promotion['promotion_link'] = promotion_link
            promotion['headquarters'] = promotion_headquarters
            promotion['social_media_links'] = social_media_links
            
            # Log item processing
            item_logger.info(f"Item scraped: {promotion_name}, Link: {promotion_link} at {response.url} for spider {self.name}")
            
            yield promotion
            item_logger.info(f"Item yielded:{promotion_link} to pipeline for spider {self.name}")



    def errback_proxy(self, failure):
        # Log proxy errors
        proxy = failure.request.meta.get('proxy')
        proxy_logger.error(f"Proxy {proxy} encountered an error for URL: {failure.request.url} for spider {self.name}")
        proxy_logger.error(f"Error details: {repr(failure)} for spider {self.name}")
        
        # Retry on failure
        if failure.check(IgnoreRequest):
            return None
        else:
            request = failure.request.copy()
            request.dont_filter = True  # To avoid getting filtered by duplicate filter
            return request
