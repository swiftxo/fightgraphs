# FightGraphs

![FightGraphs Logo](assets/logo.png)

FightGraphs is an MMA analytics platform designed to collect, organize, and analyze comprehensive fight data. The platform aggregates data on fights, fighters, events, and betting information from various MMA organizations, providing a centralized database for detailed analysis. By offering tools for data exploration and predictive modeling, FightGraphs helps uncover patterns and insights within the sport.

---

## Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Future Plans](#future-plans)
- [Disclaimer](#disclaimer)

---

## About the Project

FightGraphs aggregates data from over **850,000 fights**, **300,000 fighters**, and **40,000 events** across multiple MMA organizations. The platform utilizes an end-to-end data pipeline for scraping, cleaning, and structuring data, making it easier to analyze fight outcomes, fighter performance, and event history. Users can explore correlations between fight factors and gain insights into trends and performance patterns over time.

## Features

- **Comprehensive Data Aggregation**: Collects fight data, fighter statistics, event details, and betting information from various MMA organizations.
- **Centralized Database**: Structures and stores data for efficient access and analysis.
- **Customizable Search Capabilities**: Analyze fights based on parameters such as time range, fighter styles, betting odds, and physical attributes.
- **Predictive Analytics (In Progress)**: Developing machine learning models to predict fight outcomes and identify correlations.
- **Performance Trend Analysis**: Tools to explore fighters' performance trajectories over time.

## Tech Stack

- **Languages**: Python
- **Web Scraping**: Scrapy
- **API Development**: FastAPI
- **Database**: MongoDB
- **Data Analysis**: Pandas, Numpy
- **Visualization**: Matplotlib

## Project Structure

```
fightgraphs/
|-- assets/               # Project assets (logos, images)
|-- data/                 # Datasets (raw, cleaned, processed)
|-- notebooks/            # Jupyter notebooks for data exploration
|-- src/
|   |-- scraping/         # Web scraping scripts (partial code)
|   |-- cleaning/         # Data cleaning and preprocessing scripts
|   |-- ml/               # Machine learning models (in progress)
|   |-- utils/            # Utility functions (e.g., database connections)
|-- config/               # Configuration files for database and scraping
|-- tests/                # Unit tests
|-- .env                  # Environment variables (excluded in .gitignore)
|-- requirements.txt      # Python dependencies
|-- README.md             # Project documentation
```

## Future Plans

- **Advanced Predictive Models**: Develop machine learning models to improve fight outcome predictions and analyze betting market inefficiencies.
- **Interactive Visualizations**: Create dynamic graphs and charts for better data interpretation.
- **Web Interface Development**: Build a user-friendly web platform for easy access to fight data and analytics.
- **Cloud Database Hosting**: Host the database in a cloud environment to provide broader accessibility.

## Disclaimer

This project is intended for educational and analytical purposes. Data collection follows ethical guidelines, and the repository includes partial code to ensure compliance with website terms of service. Full scraping scripts and sensitive configurations are excluded.

