import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def fetch_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error: Response status code {response.status_code} for URL: {url}")
            return None
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def parse_product_urls(html_content):
    product_urls = set()
    if html_content:
        soup = BeautifulSoup(html_content, 'lxml')
        product_container = soup.find('div', class_='MuiGrid-container')
        if product_container:
            products = product_container.find_all('div', class_='MuiGrid-item')
            for product in products:
                a_element = product.find('a', class_='MuiCardMedia-root')
                if a_element and 'href' in a_element.attrs:
                    href = a_element['href']
                    product_urls.add(href)
    return product_urls

def get_product_urls(base_url, max_pages=300, max_workers=80):
    all_product_urls = set()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for page_number in range(1, max_pages + 1):
            url = f"{base_url}?p={page_number}"
            futures.append(executor.submit(fetch_page, url))
        for future in futures:
            html_content = future.result()
            product_urls = parse_product_urls(html_content)
            all_product_urls.update(product_urls)
    return list(all_product_urls)

base_url = "https://www.next.co.uk/shop/gender-women-productaffiliation-sportswear/feat-newin"
product_urls = get_product_urls(base_url)

if product_urls:
    df = pd.DataFrame(product_urls, columns=["Product URLs"])
    df.to_excel("sports-WomansSPORTSWEAR-New In-product_urls.xlsx", index=False)
    print("Product URLs saved to product_urls.xlsx")
else:
    print("No product URLs found.")
