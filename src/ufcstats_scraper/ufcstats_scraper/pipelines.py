from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from ufcstats_scraper.items import UfcStatsFighterItem
import logging, os, hashlib
from pymongo import MongoClient
from dotenv import load_dotenv

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

log_path = '/Users/sohanhossain/Documents/fightgraphs/src/ufcstats_scraper/logs/pipeline_logs/'
if not os.path.exists(log_path):
    os.makedirs(log_path)



dupe_logger = logging.getLogger('duplicate_items')
logging.basicConfig(level=logging.DEBUG)
dupe_handler = logging.FileHandler(f'{log_path}duplicate_items.log')
dupe_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
dupe_handler.setFormatter(formatter)
dupe_logger.setLevel(logging.INFO)
dupe_logger.addHandler(dupe_handler)


class UfcstatsScraperPipeline:
    def process_item(self, item, spider):
        return item

class UFCScraperPipeline:
    def __init__(self, mongo_uri=MONGO_URI, mongo_db=MONGO_DATABASE):
        self.mongo_uri = mongo_uri
        self.mongo_db_name = mongo_db
        self.collections = { UfcStatsFighterItem: 'scrapy_ufcstats_fighter'}
        self.buffers = {collection: [] for collection in self.collections.values()}
        self.batch_size = 250

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

    def close_spider(self, spider):
        for collection, buffer in self.buffers.items():
            if buffer:
                try:
                    dupe_logger.info(f"Attempting to insert {len(buffer)} items into {collection}.")
                    self.db[collection].insert_many(buffer)
                    dupe_logger.info(f"Successfully inserted {len(buffer)} items into {collection}.")
                except Exception as e:
                    dupe_logger.error(f"Error inserting items into {collection}: {e}")
        self.client.close()

    
    def process_item(self, item, spider):
        collection = self.collection_name(item)
        if not collection:
            raise DropItem(f"Invalid item type: {type(item)}")
        
        adapter = ItemAdapter(item)
        hash_string = ''
        for key, value in sorted(adapter.items()):
            if value is None:
                adapter[key] = 'N/A'
            elif isinstance(value, list):
                continue
            hash_string += str(value)
        adapter['hash'] = hashlib.sha256(hash_string.encode()).hexdigest()

        if self.db[collection].find_one({'hash': adapter['hash']}):
            dupe_logger.info(f"Duplicate item found of type {type(item)}: {adapter['hash']} in collection {collection}")
            raise DropItem(f"Duplicate item found: {adapter['hash']}")
        else:
            self.buffers[collection].append(dict(adapter))
            if len(self.buffers[collection]) >= self.batch_size:
                try:
                    self.db[collection].insert_many(self.buffers[collection])
                    self.buffers[collection] = [] 
                except Exception as e:
                    dupe_logger.error(f"Error inserting items into {collection}: {e}")
            

                
            
   
        return item
    