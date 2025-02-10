# Pipeline

## Overview

The Scrapy pipeline in the FightGraphs project is responsible for processing and storing scraped data from the Tapology website. The pipeline ensures data integrity, prevents duplication, and stores fight-related information in MongoDB. The two primary spiders that feed data into the pipeline are `PromotionsSpider` and `EventsSpider`.

## Architecture and Process

### 1. Data Flow Overview
The pipeline processes data from Scrapy spiders in the following sequence:
1. **PromotionsSpider** scrapes promotions from the Tapology promotions page.
2. Extracted promotions are sent as `TapologyPromotionItem` objects to the pipeline.
3. The pipeline checks for duplicates and inserts new promotion records into MongoDB (`scrapy_tapology_promotions` collection).
4. **EventsSpider** retrieves stored promotions from MongoDB and scrapes event data for each promotion.
5. Extracted events are sent as `TapologyEventItem` objects to the pipeline.
6. The pipeline checks for duplicates and inserts new event records into MongoDB (`scrapy_tapology_events` collection).

### 2. Pipeline Initialization
The pipeline is defined in [`TapologyScraperPipeline`](src/tapology_scraper/tapology_scraper/pipelines.py). It initializes the MongoDB connection using the `MONGO_URI` and `MONGO_DATABASE` environment variables.

### 3. Handling Items
Each item that passes through the pipeline undergoes the following steps:

- **Hash Generation**: A SHA-256 hash is generated from the item's field values to prevent duplicate entries.
- **Duplicate Check**: The hash is checked against existing records in MongoDB.
- **Batch Processing**: Items are buffered and inserted in batches to optimize database performance.

### 4. Promotions Processing
For each promotion scraped:
- **Promotion Name**: Extracted from the Tapology page.
- **Promotion Link**: URL of the promotion's Tapology page.
- **Headquarters**: Location of the promotion.
- **Social Media Links**: Extracted social links.
- If the promotion is not already in `scrapy_tapology_promotions`, it is stored in MongoDB.

### 5. Events Processing
For each event scraped:
- **Event Name**: Name of the event.
- **Event Link**: URL of the event’s Tapology page.
- **Associated Fights & Fighters**: Links to fights and fighters.
- **Event Date**: Extracted from the event page.
- **Event Location**: Venue of the event.
- **Event Details**: Additional metadata related to the event.
- If the event is not already in `scrapy_tapology_events`, it is stored in MongoDB.

### 6. Error Handling
The pipeline includes robust error handling mechanisms:
- **Duplicate Entries**: Logs and skips already-existing records.
- **MongoDB Connection Issues**: Logs errors when MongoDB is unreachable.
- **Invalid Data**: Ensures essential fields are present before inserting data.

### 7. Logging
Three loggers are used to track different aspects of data processing:
- **General Logger** (`general.log`): Logs pipeline initialization and data insertion steps.
- **Item Logger** (`item_processing.log`): Logs successful processing of items.
- **Duplicate Logger** (`duplicate_items.log`): Logs skipped items due to duplication.

Log files are stored in the `logs` directory.

## Conclusion

The Scrapy pipeline plays a crucial role in ensuring that scraped data from the Tapology website is efficiently processed, deduplicated, and stored in MongoDB. By implementing robust logging, batch processing, and error handling, it ensures smooth and reliable data ingestion for the FightGraphs project.

