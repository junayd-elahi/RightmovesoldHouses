# Rightmove Market Analysis

Exploratory data analysis of sold property listings from Rightmove, revealing market patterns, seasonality, geographic segmentation, and capital appreciation trends.

## Overview

This project scrapes and analyses 10,000+ sold property transactions to extract actionable insights:

- Price trends: Long-term market evolution with downturns highlighted
- Seasonality: When buyers transact vs. when prices peak
- Geographic segmentation: Median pricing by postcode district
- Property dynamics: Price scaling by type, size, tenure, and bedrooms
- Capital appreciation: Annalised returns (CAGR) for repeat sales

## Data Collection

scraper.py - Multi-page Rightmove scraper with OCR-based floor area extraction:

- Queries Rightmove house-prices endpoint by postcode
- Extracts: address, property type, tenure, bedrooms, transaction history
- Uses EasyOCR on floorplan images to extract floor area (sqft or m2)
- Outputs CSV with 10,000+ records across multiple years

Requirements:
pip install requests beautifulsoup4 pillow easyocr numpy

Usage:
python scraper.py

Reads postcodes from postcodes.txt (one per line) and writes to rightmove_data.csv.

## Analysis

analysis.py - 12-chart exploratory data analysis:

1. Price trend and volume - Median and mean price over time with transaction count
2. YoY growth - Annual price changes highlighting growth and decline periods
3. Postcode rankings - Top 25 postcodes by median price (min 30 sales)
4. Price distribution - Property types compared on log scale
5. Price per sqft - Unit pricing efficiency across property types
6. Bedrooms vs price - Scaling relationship with uncertainty bands
7. Sqft vs price - Scatter plot with linear regression line
8. Tenure premium - Freehold vs Leasehold pricing over time
9. Postcode-year heatmap - Geographic and temporal price evolution
10. Seasonality - Transaction volume and prices by month
11. Capital appreciation - Distribution of annalised returns (CAGR) across 1,744+ repeat sales
12. Rolling trends - 12-month smoothed median with downturns flagged

Requirements:
pip install pandas numpy matplotlib

Usage:
python analysis.py

Generates 12 high-resolution PNG charts in outputs/ directory.

## Key Findings

- Repeat-sale appreciation: Median CAGR of 2.3 per cent across 1,744 properties resold
- Seasonality effect: Transaction volume peaks March (627 sales), prices peak May-June (GBP620k)
- Geographic variance: Top postcode (SE11 4UF) median GBP800k; significant 2x+ spreads exist
- Property type dynamics: Detached homes command highest absolute prices; flats dominate volume (5,134 sales)
- Tenure premium: Freehold consistently 30-40 per cent above leasehold
- Market cycles: Clear downturns identified in 2008, 2016, 2020; full recovery observed post-2021

## Files

scraper.py - Main scraping logic
analysis.py - EDA and chart generation
postcodes.txt - Input postcode list (user-provided)
rightmove_data.csv - Scraped transaction data (generated)
outputs/ - Charts (generated)

## Technical Stack

Scraping: BeautifulSoup, requests
OCR: EasyOCR
Analysis: Pandas, NumPy
Visualisation: Matplotlib

## Licence

MIT
