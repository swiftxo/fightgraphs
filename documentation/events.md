# Events Spider Documentation

## Overview

The Events Spider is a Scrapy spider designed to scrape event data from the Tapology website. It collects information about various MMA events, including event names, links, dates, locations, and details. The spider is part of the FightGraphs project, which aims to aggregate and analyze comprehensive fight data.

## Architecture and Process

### 1. Spider Initialization

The spider is defined in the [`EventsSpider`](src/tapology_scraper/tapology_scraper/spiders/events.py) class. It sets the allowed domains to `tapology.com` and starts scraping from the URLs of promotions stored in the MongoDB database.

### 2. Start Requests

The `start_requests` method generates requests for each promotion link stored in the MongoDB database. It constructs the appropriate URL for each promotion and initiates the scraping process.

### 3. Parsing Responses

The `parse` method processes the response from each request. It extracts the list of events using XPath selectors and iterates through each event item. For each event, it extracts the following details:
- `event_name`: The name of the event.
- `event_link`: The link to the event's page.
- `fights`: A list of fight links associated with the event.
- `fighters`: A list of fighter links associated with the event.

These details are stored in a `TapologyEventItem` object, which is then yielded for further processing.

### 4. Parsing Event Details

The `parse_event_details` method processes the response from each event link. It extracts additional details such as:
- `event_date`: The date of the event.
- `event_location`: The location of the event.
- `event_details`: A dictionary of additional event details.

These details are added to the `TapologyEventItem` object and yielded for further processing. This method ensures that all relevant information about the event is captured. The spider crawls through two links to generate the event item, first collecting the basic event details and then further crawling into the event link to gather additional information.

### 5. Error Handling

The `errback_proxy` method handles errors that occur during the request process. It logs proxy errors and retries the request if necessary.

### 6. Logging

The spider uses three loggers to track different aspects of the scraping process:
- `general_logger`: Logs general information about the scraping process.
- `item_logger`: Logs details about the items being processed.
- `proxy_logger`: Logs errors related to proxy usage.

Log files are stored in the `logs` directory.

### 7. Item Pipeline

The scraped items are processed by the [`TapologyScraperPipeline`](src/tapology_scraper/tapology_scraper/pipelines.py). The pipeline inserts the items into the MongoDB database, ensuring that all fields are populated with valid data.

## Conclusion

The Events Spider is a crucial component of the FightGraphs project, enabling the collection of detailed event data from the Tapology website. Its architecture ensures efficient, traceable, and reliable scraping with its error handling and logging mechanisms.