import scrapy,os, logging
from tapology_scraper.items import TapologyInitialFighterItem
from scrapy.exceptions import IgnoreRequest

log_path = '/Users/sohanhossain/Documents/fightgraphs/src/tapology_scraper/logs/InitFighter_logs/'
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



class FightersSpider(scrapy.Spider):
    name = "fighters"
    allowed_domains = ["tapology.com"]
    start_urls = ["https://www.tapology.com/search/mma-fighters-by-weight-class/Atomweight-105-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Strawweight-115-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Flyweight-125-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Bantamweight-135-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Featherweight-145-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Lightweight-155-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Welterweight-170-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Middleweight-185-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Light_Heavyweight-205-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Heavyweight-265-pounds",
                  "https://www.tapology.com/search/mma-fighters-by-weight-class/Super_Heavyweight-over-265-pounds"]
    
    collection = 'scrapy_tapology_fighters_initial'
    fighter_count = {}


    def start_requests(self):
        for url in self.start_urls:
            try:
                weightclass = url.split('/')[-1]
                self.fighter_count[weightclass] = 0
                yield scrapy.Request(url, callback=self.parse, errback=self.errback_proxy, meta= {'weightclass': weightclass, 'page': 1, 'link': url})
                general_logger.info(f"Starting request for fighters for weightclass {url}")
            except Exception as e:
                proxy_logger.error(f"Error in starting request for event {url}: {e} for spider {self.name}")

    def parse(self, response):
        page = response.meta['page']
        url = response.meta['link']
        general_logger.info(f"Scraping fighters for {response.meta['weightclass']} - Page {page}")
        weightclass = response.meta['weightclass']
        next_page = page + 1
        next_page_url = f'{url}?page={next_page}'


        
        fighters_table = response.xpath('//table[@class="siteSearchResults"]//tr')
        if not fighters_table:
            general_logger.info(f"No more fighters found for {weightclass} with page {page}")
            return
        

        for i,fighter in enumerate(fighters_table):
            fighter_item = TapologyInitialFighterItem()
            fighter_item['tapology_link'] = fighter.xpath('.//td[1]/a/@href').get()
            
            if not fighter_item['tapology_link']:
                general_logger.info(f"Skipping row {i} with no link for {weightclass} at page {page}")
                continue

            fighter_item['height'] = fighter.xpath('.//td[3]/text()').get()
            fighter_item['weightclass'] = fighter.xpath('.//td[5]/text()').get()
            fighter_item['record'] = fighter.xpath('.//td[7]/text()').get()
            fighter_item['nationality'] = fighter.xpath('.//td[9]/img/@src').get()
            self.fighter_count[weightclass] += 1
            yield fighter_item
            item_logger.info(f"Processed fighter #{self.fighter_count[weightclass]}: {fighter_item['tapology_link']} for weightclass {weightclass} at page {page}")

        try:
            yield scrapy.Request(next_page_url, callback=self.parse, meta={'weightclass': weightclass, 'page': next_page, 'link': url})
        except Exception as e:
            proxy_logger.error(f"Error in starting request for event {url}: {e} for spider {self.name}")



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
