
import os
from dotenv import load_dotenv


load_dotenv()

BOT_NAME = "tapology_scraper"
SPIDER_MODULES = ["tapology_scraper.spiders"]
NEWSPIDER_MODULE = "tapology_scraper.spiders"



#General
ROBOTSTXT_OBEY = True
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# DB Settings
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

# Middleware and Pipeline settings
DOWNLOADER_MIDDLEWARES = {
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

ITEM_PIPELINES = {
    "tapology_scraper.pipelines.TapologyScraperPipeline": 300,
}

#Proxy, Headers, and Conccurrency settings
ROTATING_PROXY_LIST_PATH = '/Users/sohanhossain/Documents/fightgraphs/src/tapology_scraper/proxies.txt'
ROTATING_PROXY_BAN_POLICY = "rotating_proxies.policy.BanDetectionPolicy"
ROTATING_PROXY_CHECK_PERIOD = 5 
RETRY_ENABLED = True
ROTATING_PROXY_PAGE_RETRY_TIMES = 15
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504]

CONCURRENT_REQUESTS = 1024
CONCURRENT_REQUESTS_PER_DOMAIN = 128
CONCURRENT_REQUESTS_PER_IP = 256
AUTOTHROTTLE_ENABLED = True  
AUTOTHROTTLE_START_DELAY = 0.5  
AUTOTHROTTLE_MAX_DELAY = 30.0  
AUTOTHROTTLE_TARGET_CONCURRENCY = 128  #
AUTOTHROTTLE_DEBUG = True  

CONCURRENT_ITEMS = 1000



DEFAULT_REQUEST_HEADERS = {
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}
