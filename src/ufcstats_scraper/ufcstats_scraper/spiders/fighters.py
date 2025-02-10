import scrapy, json, logging, os
from scrapy.exceptions import IgnoreRequest
from ufcstats_scraper.items import UfcStatsFighterItem

log_path = '/Users/sohanhossain/Documents/fightgraphs/src/ufcstats_scraper/logs/fighters_log/'
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
    allowed_domains = ["ufcstats.com"]
    collection = 'scrapy_ufcstats_fighter'

    start_urls = ["http://www.ufcstats.com/statistics/fighters?char=*&page=all"]

    def start_requests(self):
        for url in self.start_urls:
            general_logger.info(f"Starting request for fighters at {url}")
            try:
                yield scrapy.Request(url, callback=self.parse, errback=self.errback_proxy)
            except Exception as e:
                proxy_logger.error(f"Error in starting request for fighters at {url}: {e} for spider {self.name}")

    def parse(self, response):
        fighters = response.xpath('//table[@class="b-statistics__table"]/tbody/tr')
        for i, fighter in enumerate(fighters):
            fighter_item = UfcStatsFighterItem()
            general_logger.info(f"Scraping fighter {i+1} of {len(fighters)} at {response.url}")
            fighter_item['fighter_link'] = fighter.xpath('.//td[1]/a/@href').get()
            fighter_item['first_name'] = fighter.xpath('.//td[1]/a/text()').get()
            fighter_item['last_name'] = fighter.xpath('.//td[2]/a/text()').get()
            fighter_item['nickname'] = fighter.xpath('.//td[3]/a/text()').get()
            fighter_item['height'] = fighter.xpath('.//td[4]/text()').get()
            fighter_item['weight'] = fighter.xpath('.//td[5]/text()').get()
            fighter_item['reach'] = fighter.xpath('.//td[6]/text()').get()
            fighter_item['stance'] = fighter.xpath('.//td[7]/text()').get()
            fighter_item['wins'] = fighter.xpath('.//td[8]/text()').get()
            fighter_item['losses'] = fighter.xpath('.//td[9]/text()').get()
            fighter_item['draws'] = fighter.xpath('.//td[10]/text()').get()
            for key, value in fighter_item.items():
                if value and isinstance(value, str):
                    fighter_item[key] = value.strip()
            champ = fighter.xpath('.//td[11]/img/@src').get()
            if champ:
                fighter_item['champ'] = True
            else:
                fighter_item['champ'] = False
            if fighter_item['fighter_link']:
                if self.db[self.collection].find_one({'fighter_link': fighter_item['fighter_link']}):
                    general_logger.info(f"Fighter {fighter_item['fighter_link']} already exists in the database. Skipping...")
                    continue

            try:
                yield response.follow(fighter_item['fighter_link'], callback=self.parse_details, meta={'fighter_item': fighter_item}, errback=self.errback_proxy)
                general_logger.info(f"Requesting details for {fighter_item['fighter_link']}")
            except Exception as e:
                proxy_logger.error(f"Error in starting request for promotion {fighter_item['fighter_link']}: {e} for spider {self.name}")

            

    def parse_details(self, response):
        fighter_item = response.meta['fighter_item']
        general_logger.info(f"Scraping details for {fighter_item['fighter_link']}")
        fighter_item['fights'] = []
        fights = []
        fights_table = response.xpath('//table[@class="b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table"]/tbody/tr[position()>1]')
        for fight in fights_table:
            fight_link = fight.xpath('.//td[1]/p/a/@href').get()   
            fight_outcome = fight.xpath('.//td[1]/p/a/i/i/text()').get()
            fighters_involved = fight.xpath('.//td[2]//a/@href').getall()
            event_link = fight.xpath('.//td[7]/p[1]/a/@href').get()
            event_date = fight.xpath('.//td[7]/p[2]/text()').get()
            title_fight = fight.xpath('.//td[7]/p[2]/img/@src').get()
            if title_fight:
                title_fight = True
            else:
                title_fight = False
            finish_method = fight.xpath('.//td[8]/p[1]/text()').get()
            finish_details = fight.xpath('.//td[8]/p[2]/text()').get()
            bonuses = fight.xpath('.//td[8]/p[1]/img/@src').getall()
            round_ended = fight.xpath('.//td[9]/p/text()').get()
            time_ended = fight.xpath('.//td[10]/p/text()').get()
            data = {
                'fight_link': fight_link,
                'fight_outcome': fight_outcome,
                'fighters_involved': fighters_involved,
                'event_link': event_link,
                'event_date': event_date,
                'title_fight': title_fight,
                'finish_method': finish_method,
                'finish_details': finish_details,
                'bonuses': bonuses,
                'round_ended': round_ended,
                'time_ended': time_ended
            }
            for key, value in data.items():
                if value and isinstance(value, list):
                    data[key] = [item.strip() for item in value]
                elif isinstance(value, str):
                    data[key] = value.strip()
            fights.append(data)
        fighter_item['fights'] = fights
        yield fighter_item
        item_logger.info(f"Yielded item {fighter_item['fighter_link']} for processing")
            

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
