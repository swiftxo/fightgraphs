# Promotions Spider Documentation

## Overview

The Promotions Spider is a Scrapy spider designed to scrape promotion data from the Tapology website. It collects information about various MMA promotions, including their names, links, headquarters, and social media links. The spider is part of the FightGraphs project, which aims to aggregate and analyze comprehensive fight data.

## Architecture and Process

### 1. Spider Initialization

The spider is defined in the [`PromotionsSpider`](src/tapology_scraper/tapology_scraper/spiders/promotions.py) class. It sets the allowed domains to `tapology.com` and starts scraping from the URL `https://www.tapology.com/fightcenter/promotions`.

### 2. Start Requests

The `start_requests` method generates requests for each page of promotions. It iterates through a known range of pages (1 to 59) and constructs the appropriate URL for each page. Before making a request, it checks if the page already exists in the MongoDB database to avoid redundant scraping.

### 3. Parsing Responses

The `parse` method processes the response from each request. It extracts the list of promotions using XPath selectors and iterates through each promotion item. For each promotion, it extracts the following details:
- `promotion_name`: The name of the promotion.
- `promotion_link`: The link to the promotion's page.
- `promotion_headquarters`: The headquarters of the promotion.
- `social_media_links`: A list of social media links associated with the promotion.

These details are stored in a `TapologyPromotionItem` object, which is then yielded for further processing.

### 4. Error Handling

The `errback_proxy` method handles errors that occur during the request process. It logs proxy errors and retries the request if necessary.

### 5. Logging

The spider uses three loggers to track different aspects of the scraping process:
- `general_logger`: Logs general information about the scraping process.
- `item_logger`: Logs details about the items being processed.
- `proxy_logger`: Logs errors related to proxy usage.

Log files are stored in the `logs` directory.

### 6. Item Pipeline

The scraped items are processed by the [`TapologyScraperPipeline`](src/tapology_scraper/tapology_scraper/pipelines.py). The pipeline inserts the items into the MongoDB database, ensuring that all fields are populated with valid data.

## Conclusion

The Promotions Spider is a crucial component of the FightGraphs project, enabling the collection of detailed promotion data from the Tapology website. Its architecture ensures efficient, traceable, and reliable scraping with it's error handling and logging mechanisms.