#site used:https://www.amazon.co.uk


#scarping the title,brand,storage ,model,availabilty and price of mobile phones

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

import time
import random

# Headers to mimic a browser request (Amazon blocks bots otherwise)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

BASE_URL = "https://www.amazon.co.uk"

def extract_urls_from_page(page_num):

    #Extract all product URLs from a given Amazon search results page.
    #Returns a list of full product URLs.

    url = f"https://www.amazon.co.uk/s?k=mobile+phones&page={page_num}"
    r = requests.get(url, headers=HEADERS)

    soup = BeautifulSoup(r.text, "html.parser")

    # Find all product containers
    cards = soup.find_all("div", {"data-component-type": "s-search-result"})
    product_urls = []

    for card in cards:
        # Flexible way to find links containing "/dp/"
        a_tags = card.find_all("a", href=True)
        for a in a_tags:
            href = a["href"]
            if "/dp/" in href:# from chat gpt ,Amazon’s standard product page format
                full_url = BASE_URL + href.split("?")[0]  # remove query params
                product_urls.append(full_url)

    # Remove duplicates
    return list(set(product_urls))

def get_title(soup):# to get title
    tag = soup.select_one("span#productTitle")
    return tag.text.strip() if tag else None

def get_brand(soup):# to get brand from title
    tag = soup.find("a", id="bylineInfo")
    if tag:
        return tag.text.strip().replace("Visit the", "").replace("Store", "").replace("Brand:", "").strip()
    return None

def get_price(soup):
    # Extracts price from Amazon product page

    # Common price selectors on Amazon
    selectors = [
        "#priceblock_dealprice",
        "#priceblock_ourprice",
        "#price_inside_buybox",
        ".a-price .a-offscreen"
    ]

    # Try main selectors first
    for sel in selectors:
        tag = soup.select_one(sel)
        if tag:
            text = tag.get_text(strip=True)
            if text in {"", ".", "—"}:
                continue
            # Handle European style numbers
            match = re.search(r"[\d.,]+", text)
            if match:
                num = match.group()
                # Convert European format if needed
                if num.count(",") == 1 and num.count(".") > 1:
                    num = num.replace(".", "").replace(",", ".")
                else:
                    num = num.replace(",", "")
                try:
                    return float(num)
                except ValueError:
                    continue

    # Try combining whole + fraction spans (common in .a-price)
    whole = soup.select_one(".a-price-whole")
    fraction = soup.select_one(".a-price-fraction")
    if whole and fraction:
        num = whole.get_text(strip=True) + "." + fraction.get_text(strip=True)
        num = num.replace(",", "")
        try:
            return float(num)
        except ValueError:
            pass

    # Fallback: search all spans for currency symbols
    for tag in soup.find_all("span"):
        text = tag.get_text(strip=True)
        if any(c in text for c in ["£", "$", "€"]):
            if text in {"", ".", "—"}:
                continue
            match = re.search(r"[\d.,]+", text)#extract the numeric part of the price
            if match:
                num = match.group()
                if num.count(",") == 1 and num.count(".") > 1:
                    num = num.replace(".", "").replace(",", ".")
                else:
                    num = num.replace(",", "")
                try:
                    return float(num)
                except ValueError:
                    continue

    # Price not found
    return None
def get_rating(soup):# to get rating
    tag = soup.select_one("span[data-hook='rating-out-of-text']")
    return tag.text.strip() if tag else None
def get_review_count(soup):# to get review count
    tag = soup.select_one("span#acrCustomerReviewText")
    return tag.text.strip() if tag else None

def get_color(soup):# to get color of the phone
    selectors = [
        "#variation_color_name .selection",
        "#inline-twister-expanded-dimension-text-color_name"
    ]
    for sel in selectors:
        tag = soup.select_one(sel)
        if tag:
            return tag.text.strip()
    # Fallback from title
    title = get_title(soup)
    if title:
        match = re.search(r"(Black|Blue|Green|Silver|White|Red|Pink|Grey|Gold|Bronze|Cyan|Obsidian|Porcelain)", title, re.I)# searching the color
        if match:
            return match.group(1)
    return None
def get_specs(soup):# to get specifications
    specs = {}# to store specifications
    table_ids = [
        "productDetails_techSpec_section_1",
        "productDetails_techSpec_section_2",
        "productDetails_detailBullets_sections1"
    ]
    for table_id in table_ids:
        table = soup.find("table", {"id": table_id})# finding the table ids
        if table:
            rows = table.find_all("tr")#finding rows in table. each row has specifications
            for row in rows:
                th = row.find("th")# contains name of spec
                td = row.find("td")# contains data
                if th and td:
                    specs[th.get_text(strip=True)] = td.get_text(strip=True)

    bullets = soup.select("#feature-bullets ul li span.a-list-item")# amazon also store features as bullet points
    for bullet in bullets:
        text = bullet.get_text(strip=True)
        if ":" in text:#Some bullet points are formatted as Key: Value
            k, v = text.split(":", 1)#splits the bullet into key and value.
            specs[k.strip()] = v.strip()#splits the string at the first colon
    return specs

def extract_storage(title, specs):
    # From title: pick numbers followed by GB/TB or if none, any number >32
    if title:
        match = re.findall(r"(\d+)\s*(GB|TB)?", title, re.I)
        if match:
            # Prefer GB/TB if mentioned
            for n, unit in match:
                if unit:  # if GB/TB found
                    return f"{n} {unit.upper()}"
            # fallback: pick largest number >32 as storage (avoid small RAM numbers)
            nums = [int(n) for n, _ in match if int(n) > 32]
            if nums:
                return f"{max(nums)} GB"

    # From specs: pick largest number in GB/TB
    storage_keys = ["storage", "memory", "internal memory", "rom",
                    "built-in storage", "flash memory", "capacity",
                    "internal", "internal storage"]
    for key, val in specs.items():
        if any(k in key.lower() for k in storage_keys):
            matches = re.findall(r"(\d+)\s*(GB|TB)", val, re.I)
            if matches:
                matches = [(int(n), u.upper()) for n, u in matches]
                largest = max(matches, key=lambda x: x[0])# picking up the largest number
                return f"{largest[0]} {largest[1]}"

    #  Fallback: check all spec values
    all_specs = " ".join(specs.values())
    match = re.findall(r"(\d+)\s*(GB|TB)", all_specs, re.I)
    if match:
        matches = [(int(n), u.upper()) for n, u in match]
        largest = max(matches, key=lambda x: x[0])
        return f"{largest[0]} {largest[1]}"

    return None

def extract_model(title, brand, max_words=4):# to extract the model name of the phone
    if not title:
        return None

    t = title.lower()
    brand_stripped = brand.lower() if brand else None #Converts everything to lowercase

    # Remove brand from title
    if brand_stripped and brand_stripped in t:#Remove brand from title
        t = t.split(brand_stripped, 1)[1]

    # Remove punctuation
    t = re.sub(r"[\(\)–,|]", " ", t)

    # Split words and filter unwanted
    words = t.split()
    model_words = []
    skip_words = ["gb", "ram", "smartphone", "sim", "android", "5g", 
                  "dual", "lte"]

    for w in words:
        if any(skip in w for skip in skip_words):
            continue
        model_words.append(w)
        if len(model_words) == max_words:
            break

    return " ".join(model_words).title() if model_words else None
def parse_phone_details(title, specs, brand):# to extract the model and
    model = extract_model(title, brand)#gets model
    storage = extract_storage(title, specs)#gets storage
    return model, storage

def scrape_multiple_pages(num_pages=1):# main scrapping funtion to scrape multiple pages
    data = {
        "Title": [], "Model": [], "Storage": [], "Price": [],
        "Rating": [], "Review_Count": [],
        "Color": [], "Brand": [], "URL": []
    }

    all_product_urls = []
    for page in range(1, num_pages + 1):
        try:
            urls = extract_urls_from_page(page)
            all_product_urls.extend(urls)
        except Exception as e:
            print(f"Failed page {page}:", e)
        time.sleep(random.uniform(2, 4))

    all_product_urls = list(set(all_product_urls))
    print(f"Total products found: {len(all_product_urls)}")

    for url in all_product_urls:
        try:
            r = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(r.text, "html.parser")

            title = get_title(soup)
            brand = get_brand(soup)
            specs = get_specs(soup)
            model, storage = parse_phone_details(title, specs, brand)
            price = get_price(soup)

            raw_rating = get_rating(soup)
            raw_review = get_review_count(soup)
            color = get_color(soup)

            data["Title"].append(title)
            data["Brand"].append(brand)
            data["Model"].append(model)
            data["Storage"].append(storage)
            data["Price"].append(price)
            data["Rating"].append(raw_rating)
            data["Review_Count"].append(raw_review)
            data["Color"].append(color)
            data["URL"].append(url)

        except Exception as e:
            print("Error:", e)

        time.sleep(random.uniform(1, 2))

    return pd.DataFrame(data)
df = scrape_multiple_pages(num_pages=1)

from IPython.display import display
display(df)


# Clean Price: convert to float, ignore invalid entries
def clean_price(p):
    if p is None:
        return None
    try:
        # Remove any non-digit/non-dot/comma characters
        text = str(p).replace(",", "").strip()
        # Skip if empty or just "."
        if not re.search(r"\d", text):
            return None
        return float(text)
    except:
        return None

# Clean Rating: convert "4.3 out of 5" -> 4.3
def clean_rating(r):
    if not r:
        return None
    match = re.search(r"[\d.]+", str(r))
    return float(match.group()) if match else None

# Clean Review Count: convert "(1,201)" -> 1201
def clean_review_count(rc):
    if not rc:
        return None
    text = str(rc).replace(",", "").replace("(", "").replace(")", "").strip()
    return int(text) if text.isdigit() else None

# Apply cleaning to your DataFrame
df["Price"] = df["Price"].apply(clean_price)
df["Rating"] = df["Rating"].apply(clean_rating)
df["Review_Count"] = df["Review_Count"].apply(clean_review_count)

# Check result
display(df)
from unittest.mock import patch

# -------------------------
# UNIT TESTS
# -------------------------

assert extract_storage("Phone 128GB", {}) == "128 GB"
assert extract_storage("Phone", {"Internal Storage": "64 GB"}) == "64 GB"
assert extract_storage("Phone", {}) is None
print("extract_storage passed")

assert extract_model("Apple iPhone 14 Pro 256GB", "Apple") == "Iphone 14 Pro"
assert extract_model(None, "Samsung") is None
print(" extract_model passed")

html_price = """
<span class="a-price">
    <span class="a-offscreen">£599.99</span>
</span>
"""
soup_price = BeautifulSoup(html_price, "html.parser")
assert get_price(soup_price) == 599.99
print("get_price passed")

model, storage = parse_phone_details(
    "Google Pixel 7 128GB",
    {"Internal Storage": "128 GB"},
    "Google"
)
assert model == "Pixel 7"
assert storage == "128 GB"
print(" parse_phone_details passed")

# -------------------------
# INTEGRATION TEST
# -------------------------

@patch("requests.get")
def integration_test(mock_get):
    search_html = """
    <div data-component-type="s-search-result">
        <a class="a-link-normal s-no-outline" href="/dp/TEST123"></a>
    </div>
    """

    product_html = """
    <span id="productTitle">Test Phone 128GB Black</span>
    <a id="bylineInfo">Brand: TestBrand</a>
    <span class="a-price">
        <span class="a-offscreen">£399.99</span>
    </span>
    <span data-hook="rating-out-of-text">4.4 out of 5 stars</span>
    <span id="acrCustomerReviewText">100 reviews</span>
    """

    mock_get.side_effect = [
        type("Response", (), {"text": search_html}),
        type("Response", (), {"text": product_html})
    ]

    df = scrape_multiple_pages(num_pages=1)

    assert len(df) == 1
    assert df.iloc[0]["Brand"] == "TestBrand"
    assert df.iloc[0]["Storage"] == "128 GB"
    assert df.iloc[0]["Price"] == 399.99

    print(" integration test passed")

integration_test()

print("All tests passed ")


import sqlite3
# Connect (creates file if it doesn't exist)
conn = sqlite3.connect("amazon_phones.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS phones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    model TEXT,
    storage TEXT,
    price TEXT,
    rating TEXT,
    review_count TEXT,
    url TEXT,
    color TEXT
)
""")

# Insert DataFrame into the table
df.to_sql("phones", conn, if_exists="replace", index=False)

# Verify
cursor.execute("SELECT COUNT(*) FROM phones")
print("Rows inserted:", cursor.fetchone()[0])

conn.commit()
conn.close()


