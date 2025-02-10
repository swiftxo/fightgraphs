from pymongo import MongoClient
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from tapology_scraper.items import TapologyPromotionItem, TapologyEventItem, TapologyInitialFighterItem
import hashlib, logging, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

# Create a dynamic log directory based on timestamp
log_dir = f'/Users/sohanhossain/Documents/fightgraphs/src/tapology_scraper/logs/pipeline_logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
os.makedirs(log_dir, exist_ok=True)

def setup_logger(name, log_file, level=logging.INFO):
    """Creates and configures a logger"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# General log for all pipeline operations
pipeline_logger = setup_logger('pipeline_logger', f'{log_dir}/pipeline.log')

class TapologyScraperPipeline:
    def __init__(self, mongo_uri=MONGO_URI, mongo_db=MONGO_DATABASE):
        self.mongo_uri = mongo_uri
        self.mongo_db_name = mongo_db
        self.collections = {
            TapologyPromotionItem: 'scrapy_tapology_promotions',
            TapologyEventItem: 'scrapy_tapology_events',
            TapologyInitialFighterItem: 'scrapy_tapology_fighters_initial'
        }
        self.buffers = {collection: [] for collection in self.collections.values()}
        self.batch_size = 250
        self.collection_loggers = {}

    def collection_name(self, item):
        return self.collections.get(type(item))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', MONGO_URI),
            mongo_db=crawler.settings.get('MONGO_DATABASE', MONGO_DATABASE)
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db_name]
        spider.db = self.db

        # Create a dedicated log file for each collection
        for collection_name in self.collections.values():
            log_file = f"{log_dir}/{collection_name}.log"
            self.collection_loggers[collection_name] = setup_logger(collection_name, log_file)
            pipeline_logger.info(f"Logger initialized for {collection_name}: {log_file}")

    def close_spider(self, spider):
        for collection, buffer in self.buffers.items():
            if buffer:
                try:
                    pipeline_logger.info(f"Attempting to insert {len(buffer)} items into {collection}.")
                    self.db[collection].insert_many(buffer)
                    pipeline_logger.info(f"Successfully inserted {len(buffer)} items into {collection}.")
                except Exception as e:
                    pipeline_logger.error(f"Error inserting items into {collection}: {e}")
        self.client.close()

    def process_item(self, item, spider):
        collection = self.collection_name(item)
        if not collection:
            pipeline_logger.warning(f"Invalid item type: {type(item)}")
            raise DropItem(f"Invalid item type: {type(item)}")

        adapter = ItemAdapter(item)
        hash_string = ''
        for key, value in sorted(adapter.items()):
            if value is None:
                adapter[key] = 'N/A'
            hash_string += str(value)

        adapter['hash'] = hashlib.sha256(hash_string.encode()).hexdigest()
        collection_logger = self.collection_loggers[collection]

        # Check for duplicates
        if self.db[collection].find_one({'hash': adapter['hash']}):
            collection_logger.info(f"Duplicate item found: {adapter['hash']}")
            raise DropItem(f"Duplicate item found: {adapter['hash']}")
        else:
            self.buffers[collection].append(dict(adapter))
            collection_logger.info(f"Item added to buffer: {adapter['hash']} (Buffer size: {len(self.buffers[collection])})")

            if len(self.buffers[collection]) >= self.batch_size:
                try:
                    self.db[collection].insert_many(self.buffers[collection])
                    collection_logger.info(f"Batch inserted {len(self.buffers[collection])} items into {collection}.")
                    self.buffers[collection] = []
                except Exception as e:
                    collection_logger.error(f"Error inserting items into {collection}: {e}")

        return item
