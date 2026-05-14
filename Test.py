import requests
from bs4 import BeautifulSoup
import re
import io
import numpy as np
from PIL import Image
import easyocr

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

reader = easyocr.Reader(['en'], gpu=False)

postcode_url = "https://www.rightmove.co.uk/house-prices/se1-8st.html?radius=1"
r = session.get(postcode_url, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")
cards = soup.find_all("a", attrs={"data-testid": "propertyCard"})
print(f"Cards found: {len(cards)}")

for i, card in enumerate(cards[:5]):  # test first 5 only
    href = card.get("href", "")
    h2 = card.find("h2")
    address = h2.get_text(strip=True) if h2 else "Unknown"

    r2 = session.get(href, timeout=10)
    floorplans = re.findall(
        r'https://media\.rightmove\.co\.uk/property-floorplan/[^"<>\s]+\.(?:jpe?g|png|webp)',
        r2.text, re.IGNORECASE
    )

    sqft = None
    if floorplans:
        img_data = session.get(floorplans[0], timeout=10).content
        image = Image.open(io.BytesIO(img_data)).convert('RGB')
        results = reader.readtext(np.array(image), detail=0, paragraph=False)
        combined = " ".join(t.lower() for t in results)

        match = re.search(r'(\d[\d,]*\.?\d*)\s*sq\.?\s*(?:ft|feet)', combined, re.IGNORECASE)
        if match:
            sqft = int(float(match.group(1).replace(",", "")))
        else:
            match = re.search(r'(\d[\d,]*\.?\d*)\s*(?:sq\.?\s*m|m²)', combined, re.IGNORECASE)
            if match:
                sqft = int(float(match.group(1).replace(",", "")) * 10.764)

    print(f"[{i+1}] {address}")
    print(f"     floorplans: {len(floorplans)}  →  sqft: {sqft}")