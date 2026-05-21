Rightmove Market Analysis
Exploratory data analysis of sold property listings from Rightmove, revealing market patterns, seasonality, geographic segmentation, and capital appreciation trends.
Overview
This project scrapes and analyses sold property transactions to extract actionable insights:

Price trends: Long-term market evolution with downturns highlighted
Seasonality: When buyers transact vs. when prices peak
Geographic segmentation: Median pricing by postcode district
Property dynamics: Price scaling by type, size, tenure, and bedrooms
Capital appreciation: Annualized returns (CAGR) for repeat sales

Requirements:
requests beautifulsoup4 pillow easyocr numpy

Usage:
python scraper.py

Reads postcodes from postcodes.txt (one per line) and writes to rightmove_data.csv.

Analysis
analysis.py — 12-chart exploratory data analysis:

Price trend & volume — Median/mean price over time with transaction count
YoY growth — Annual price changes highlighting growth/decline periods
Postcode rankings — Top 25 postcodes by median price (min 30 sales)
Price distribution — Property types compared on log scale
Price per sqft — Unit pricing efficiency across property types
Bedrooms vs price — Scaling relationship with uncertainty bands
Sqft vs price — Scatter plot with linear regression line
Tenure premium — Freehold vs Leasehold pricing over time
Postcode-year heatmap — Geographic and temporal price evolution
Seasonality — Transaction volume and prices by month
Capital appreciation — Distribution of annualized returns (CAGR) across 1,744+ repeat sales
Rolling trends — 12-month smoothed median with downturns flagged


├── scraper.py              # Main scraping logic
├── analysis.py             # EDA and chart generation
├── postcodes.txt           # Input postcode list (user-provided)
├── rightmove_data.csv      # Scraped transaction data (generated)
└── outputs/                # Charts (generated)
    ├── 01_price_trend_volume.png
    ├── 02_yoy_growth.png
    ├── 03_postcode_ranking.png
    ├── 04_price_by_proptype.png
    ├── 05_ppsf_by_proptype.png
    ├── 06_bedrooms_vs_price.png
    ├── 07_sqft_vs_price.png
    ├── 08_tenure_trend.png
    ├── 09_heatmap_postcode_year.png
    ├── 10_seasonality.png
    ├── 11_repeat_sale_returns.png
    └── 12_rolling_trend_downturns.png
    
Technical Stack

Scraping: BeautifulSoup, requests
OCR: EasyOCR
Analysis: Pandas, NumPy
Visualisation: Matplotlib
