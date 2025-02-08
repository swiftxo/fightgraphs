import scrapy, os, logging
from tapology_scraper.items import TapologyEventItem
from scrapy.exceptions import IgnoreRequest

log_path = '/Users/sohanhossain/Documents/fightgraphs/src/tapology_scraper/logs/events_log/'
if not os.path.exists(log_path):
    os.makedirs(log_path)

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

class EventsSpider(scrapy.Spider):
    name = "events"
    collection = 'scrapy_tapology_events'
    allowed_domains = ["tapology.com"]
    start_urls = []
    
    def start_requests(self):
        promotions = self.db['scrapy_tapology_promotions'].distinct('promotion_link')
        self.start_urls = promotions
        for link in self.start_urls:
            url = 'https://www.tapology.com' + link
            general_logger.info(f"Starting request for events for promotion {url}")
            try:
                
                yield scrapy.Request(url, callback=self.parse, meta={'promotion_link': url, 'page': 1}, errback=self.errback_proxy)
            except Exception as e:
                proxy_logger.error(f"Error in starting request for promotion {url}: {e} for spider {self.name}")
            

    def parse(self, response):
        promotion_link = response.meta['promotion_link']
        general_logger.info(f"Scraping events for {response.meta['promotion_link']} - Page {response.meta['page']}")
        page = response.meta['page']
        next_page = page + 1
        next_page_url = f'{promotion_link}?page={next_page}'
        yield scrapy.Request(next_page_url, callback=self.parse, meta={'promotion_link': promotion_link, 'page': next_page})

        events = response.xpath("//div[@data-controller='bout-toggler']")
        if not events:
            general_logger.info(f"No more events found for {promotion_link} with page {page}")
            return

        for event in events:
            event_link = event.xpath('.//a[contains(@href, "/fightcenter/events/")]/@href').get()
            if not event_link:
                general_logger.info(f"Event link not found for {response.url}")
                continue

            event_link = 'https://www.tapology.com' + event_link
            if self.db[self.collection].find_one({'event_link': event_link}):
                general_logger.info(f"Event {event_link} already exists in the database. Skipping...")
                continue
                
            event_item = TapologyEventItem()
            event_item['promotion_link'] = promotion_link
            event_item['event_link']=  event_link
            event_item['event_name'] = event.xpath('.//a[contains(@href, "/fightcenter/events/")]/text()').get()

            event_item['fights'], event_item['fighters'] = [], []
            fights_container = event.xpath('.//div[@data-bout-toggler-target="content"]//a/@href').getall()
            for link in fights_container:
                if link:
                    if '/fightcenter/fighters/' in link and 'fightcenter/fighters/' not in event_item['fighters']:
                        event_item['fighters'].append(link)
                    elif '/fightcenter/bouts/' in link and 'fightcenter/bouts/' not in event_item['fights']:
                        event_item['fights'].append(link)
            yield scrapy.Request(event_item['event_link'], callback=self.parse_event_details, meta={'event_item': event_item})
            general_logger.info(f"Scraping event details for {['event_name']} - {event_item['event_link']}")
        

    def parse_event_details(self, response):
        event_item = response.meta['event_item']

        date_container = response.xpath('//div[@class="div flex items-center justify-between text-xs uppercase font-bold text-tap_7f leading-none"]')
        event_item['event_date'] = date_container.xpath('.//span[@class="hidden md:inline"]/text()').get()
        location_container = response.xpath('//div[@class="div flex items-center justify-end gap-1.5"]')
        event_item['event_location'] = location_container.xpath('.//a/text()').get()
        details = {}
        details_container = response.xpath('//div[contains(@class, "hidden") and contains(@class, "md:flex")]/ul/li')
        for detail in details_container:
            detail_key = detail.xpath('.//span[contains(@class, "font-bold")]/text()').get()
            detail_value = detail.xpath('.//span[contains(@class, "text-neutral-700")]/text()').get()
            
            if detail_key and detail_value:
                details[detail_key.strip()] = detail_value.strip()
        event_item['event_details'] = details
        yield event_item
        item_logger.info(f"Item yielded:{event_item['event_link']} to pipeline for spider {self.name}")

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
