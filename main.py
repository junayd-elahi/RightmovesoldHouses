import requests
from bs4 import BeautifulSoup
import re
import csv
import io
import time
import numpy as np
from PIL import Image
import easyocr

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

reader = easyocr.Reader(['en'], gpu=False)

def helper_function(postcode):
    return postcode.lower().replace(" ", "-")

def total_pages(url):
    try:
        response = session.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        select = soup.find("select", attrs={"name": "paginationDropdown"})
        if not select:
            return 1
        options = [opt["value"] for opt in select.find_all("option")]
        return int(options[-1])
    except Exception as e:
        print(f"Error: {e}")
        return 1

def extract_floorplans(html):
    matches = re.findall(
        r'https://media\.rightmove\.co\.uk/property-floorplan/[^"<>\s]+\.(?:jpe?g|png|webp)',
        html, re.IGNORECASE
    )
    return list(set(matches))

def get_sqft(detail_url):
    try:
        r = session.get(detail_url, timeout=10)
        floorplans = extract_floorplans(r.text)
        if not floorplans:
            return None

        img_data = session.get(floorplans[0], timeout=10).content
        image = Image.open(io.BytesIO(img_data)).convert('RGB')
        results = reader.readtext(np.array(image), detail=0, paragraph=False)
        combined = " ".join(t.lower() for t in results)

        match = re.search(r'(\d[\d,]*\.?\d*)\s*sq\.?\s*(?:ft|feet)', combined, re.IGNORECASE)
        if match:
            sqft = int(float(match.group(1).replace(",", "")))
            if 100 < sqft < 10000:
                return sqft

        match = re.search(r'(\d[\d,]*\.?\d*)\s*(?:sq\.?\s*m|m²)', combined, re.IGNORECASE)
        if match:
            sqft = int(float(match.group(1).replace(",", "")) * 10.764)
            if 100 < sqft < 10000:
                return sqft

    except Exception as e:
        print(f"sqft failed for {detail_url}: {e}")

    return None

def parse_card(card):
    """Extract all static fields from a card element."""
    h2 = card.find("h2")
    address = h2.get_text(strip=True) if h2 else None
    href = card.get("href", "")

    property_type = None
    tenure = None
    bedrooms = None
    for cat in card.find_all("div", attrs={"aria-label": True}):
        label = cat["aria-label"]
        if label.startswith("Property Type:"):
            property_type = label.replace("Property Type:", "").strip().rstrip(".")
        elif label.startswith("Tenure:"):
            tenure = label.replace("Tenure:", "").strip().rstrip(".")
        elif label.startswith("Bedrooms:"):
            bedrooms = label.replace("Bedrooms:", "").strip().rstrip(".")

    return address, href, property_type, tenure, bedrooms

def parse_rows(card):
    """Extract all transaction rows from a card."""
    transactions = []
    for row in card.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) != 2:
            continue
        date = tds[0].get_text(strip=True)
        price_div = tds[1].find("div", attrs={"aria-label": True})
        if not price_div:
            continue
        price_str = re.sub(r"[^\d]", "", price_div["aria-label"])
        price = int(price_str) if price_str else None
        transactions.append((date, price))
    return transactions

def scrape_web_data(postcodes):
    results = []

    for postcode in postcodes:
        base_url = f"https://www.rightmove.co.uk/house-prices/{helper_function(postcode)}.html?radius=1"
        pages = total_pages(base_url)

        for page_num in range(1, pages + 1):
            url = f"{base_url}&pageNumber={page_num}"
            response = session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            cards = soup.find_all("a", attrs={"data-testid": "propertyCard"})

            if not cards:
                break

            for card in cards:
                address, href, property_type, tenure, bedrooms = parse_card(card)
                sqft = get_sqft(href) if href else None
                print(f"{address} | beds: {bedrooms} | sqft: {sqft}")

                for date, price in parse_rows(card):
                    results.append({
                        "postcode": postcode,
                        "address": address,
                        "property_type": property_type,
                        "tenure": tenure,
                        "bedrooms": bedrooms,
                        "date": date,
                        "price": price,
                        "sqft": sqft
                    })

                time.sleep(1)

    with open("rightmove_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["postcode", "address", "property_type", "tenure", "bedrooms", "date", "price", "sqft"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done — {len(results)} records saved to rightmove_data.csv")

with open("postcodes.txt", "r") as f:
    postcodes = [line.strip() for line in f if line.strip()]

scrape_web_data(postcodes)