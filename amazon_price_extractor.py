from requests_html import HTML
from selenium import webdriver
import time
import re
from selenium.webdriver.chrome.options import Options
import os
import pandas as pd

BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
product_category_output = os.path.join(DATA_DIR, "product_category.csv")
products_output = os.path.join(DATA_DIR, "products.csv")
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

categories = [
    {"name": "mobile-phone",
        "url": "https://www.amazon.in/gp/bestsellers/electronics/1805560031"},
    {"name": "laptops", "url": "https://www.amazon.in/gp/bestsellers/computers/1375424031"},
    {"name": "earphones",
        "url": "https://www.amazon.in/gp/bestsellers/electronics/1389434031/"},
]


def search_category_and_find_links(categories):
    print("grabling all links across all categories")
    all_product_links = []
    for category in categories:
        time.sleep(5)
        category_url = category.get("url")
        driver.get(category_url)
        html_body = driver.find_element_by_css_selector("body")
        html_inner_text = html_body.get_attribute("innerHTML")
        html_obj = HTML(html=html_inner_text)
        links = html_obj.links
        products_links = [
            f"https://www.amazon.in{x}" for x in links if x.startswith("/")]
        all_product_links += products_links
    return all_product_links


regex_option = [
    "https://www.amazon.in/(?P<title>[\w-]+)/dp/(?P<product_id>[\w-]+)/",
    "https://www.amazon.in/dp/(?P<product_id>[\w-]+)/",
    "https://www.amazon.in/gp/(?P<sproduct_id>[\w-]+)/"
]


def extract_product_from_id(url):
    product_id = None
    for regex_str in regex_option:
        regex = re.compile(regex_str)
        match = regex.match(str(url))
        if match is not None:
            try:
                product_id = match['product_id']
            except:
                pass
    return product_id


def cleaned_links(links, category=None):
    final_products_links = []
    for link in links:
        product_id = extract_product_from_id(link)
        if product_id != None:
            final_products_links.append(
                {"ID": product_id, "URL": link, "CATEGORY": category})
    return final_products_links


def scrape_and_grab_price(url, title_lookup="#productTitle", price_lookup="#priceblock_ourprice"):
    driver.get(url)
    time.sleep(1.6)
    html_body = driver.find_element_by_css_selector("body")
    html_inner_text = html_body.get_attribute("innerHTML")
    html_obj = HTML(html=html_inner_text)
    title = html_obj.find(title_lookup, first=True)
    price = html_obj.find(price_lookup, first=True)
    return (title.text, price.text)


def perform_scan(cleaned_product_links):
    print("performing scanning")
    data_extracted = []
    for obj in cleaned_product_links:
        link = obj["URL"]
        product_id = obj["ID"]
        title, price = None, None
        try:
            title, price = scrape_and_grab_price(link)
            print(link, title, price)
        except:
            pass
        if title != None and price != None:
            data = {
                "URL": link,
                "ID": product_id,
                "TITLE": title,
                "PRICE": price,
            }
            data_extracted.append(data)
    return data_extracted


def extract_category_and_save(categories=[]):
    print("started")
    all_links = search_category_and_find_links(categories)
    cleaned_product_links = cleaned_links(all_links)
    category_data = perform_scan(cleaned_product_links)
    category_data_df = pd.DataFrame(category_data)
    category_data_df.to_csv(product_category_output, index=False)


extract_category_and_save(categories=categories)
pd.read_csv(product_category_output)
