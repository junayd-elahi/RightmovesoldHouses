import requests
from bs4 import BeautifulSoup
import re
import csv

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

def helper_function(postcode):
    return postcode.lower().replace(" ", "-")

def total_pages(url):
    try:
        response = session.get(url,timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        select = soup.find("select", attrs={"name": "paginationDropdown"})
        if not select:
            return 1
        options = [opt["value"] for opt in select.find_all("option")]
        return int(options[-1])
    except Exception as e:
        print (f"Error: {e}")
        return 1


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
                h2 = card.find("h2")
                address = h2.get_text(strip=True) if h2 else None

                categories = card.find_all("div", attrs={"aria-label": True})
                property_type = None
                tenure = None
                for cat in categories:
                    label = cat["aria-label"]
                    if label.startswith("Property Type:"):
                        property_type = label.replace("Property Type:", "").strip().rstrip(".")
                    elif label.startswith("Tenure:"):
                        tenure = label.replace("Tenure:", "").strip().rstrip(".")

                rows = card.find_all("tr")
                for row in rows:
                    tds = row.find_all("td")
                    if len(tds) != 2:
                        continue

                    date_td = tds[0].get_text(strip=True)
                    price_div = tds[1].find("div", attrs={"aria-label": True})
                    if not price_div:
                        continue

                    price_str = re.sub(r"[^\d]", "", price_div["aria-label"])
                    price = int(price_str) if price_str else None

                    results.append({
                        "postcode": postcode,
                        "address": address,
                        "property_type": property_type,
                        "tenure": tenure,
                        "date": date_td,
                        "price": price
                    })

    with open("rightmove_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["postcode", "address", "property_type", "tenure", "date", "price"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done — {len(results)} records saved to rightmove_data.csv")



with open("postcodes.txt", "r") as f:
    postcodes = [line.strip() for line in f if line.strip()]

scrape_web_data(postcodes)