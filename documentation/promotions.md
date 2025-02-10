# Pipelines Documentation

## Overview

The `TapologyScraperPipeline` is a Scrapy pipeline designed to process and store scraped items into a MongoDB database. It handles duplicate detection, logging, and bulk insertion of items to ensure efficient and reliable data storage.

## Architecture and Process

### 1. Initialization

The pipeline is initialized with the MongoDB URI and database name, which are loaded from environment variables. It also sets up collections for different item types (`TapologyPromotionItem` and `TapologyEventItem`) and initializes buffers for batch processing.

```python
class TapologyScraperPipeline:
    def __init__(self, mongo_uri=MONGO_URI, mongo_db=MONGO_DATABASE):
        self.mongo_uri = mongo_uri
        self.mongo_db_name = mongo_db
        self.collections = { TapologyPromotionItem: 'scrapy_tapology_promotions', TapologyEventItem: 'scrapy_tapology_events' }
        self.buffers = {collection: [] for collection in self.collections.values()}
        self.batch_size = 250
```

2. Collection Name
The collection_name method returns the collection name for a given item type.

def collection_name(self, item):
    return self.collections.get(type(item))


3. From Crawler
The from_crawler method allows the pipeline to be instantiated with settings from the Scrapy crawler.

@classmethod
def from_crawler(cls, crawler):
    return cls(
        mongo_uri=crawler.settings.get('MONGO_URI', MONGO_URI),
        mongo_db=crawler.settings.get('MONGO_DATABASE', MONGO_DATABASE)
    )


4. Open Spider
The open_spider method establishes a connection to the MongoDB database when the spider is opened.

def open_spider(self, spider):
    self.client = MongoClient(self.mongo_uri)
    self.db = self.client[self.mongo_db_name]
    spider.db = self.db


5. Close Spider
The close_spider method inserts any remaining items in the buffers into the database and closes the MongoDB connection when the spider is closed.

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


    6. Process Item
The process_item method processes each item, checks for duplicates, and adds it to the buffer for bulk insertion. If the buffer reaches the batch size, it inserts the items into the database.

def process_item(self, item, spider):
    collection = self.collection_name(item)
    if not collection:
        raise DropItem(f"Invalid item type: {type(item)}")
    
    adapter = ItemAdapter(item)
    hash_string = ''
    for key, value in sorted(adapter.items()):
        if value is None:
            adapter[key] = 'N/A'
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



    7. Logging
The pipeline sets up logging to track duplicate items and errors during the insertion process. Log files are stored in the logs directory.

