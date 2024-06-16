import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import logging
import time

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Headers for the requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Read the Excel file
try:
    df = pd.read_excel('a.xlsx')
except FileNotFoundError:
    logging.error("Excel file not found.")
    exit()

all_data = []

# Function to extract image URLs
def extract_image_urls(script_content):
    image_urls_match = re.search(r'"imagePathList":(\[.*?\])', script_content)
    if image_urls_match:
        image_urls_str = image_urls_match.group(1)
        image_urls = json.loads(image_urls_str)
        return [url.replace('.png', '.jpg') for url in image_urls[:4]]  # Convert PNG to JPG and limit to 4 URLs
    return []

# Function to extract product info from script
def extract_product_info(script_content, base_data):
    base_data['image_urls'] = extract_image_urls(script_content)
    for img_url in base_data['image_urls']:
        logging.info(f"Image URL: {img_url}")

    product_id_match = re.search(r'"productId":"(.*?)"', script_content)
    if product_id_match:
        base_data['product_id'] = product_id_match.group(1)
        logging.info(f"Product ID: {base_data['product_id']}")
    
    product_id2_match = re.search( r'\\"productId\\":(\d+)', script_content)
    if product_id2_match:
        product_id = product_id2_match.group(1)
        base_data['product_id'] = product_id
        logging.info(f"Product ID: {base_data['product_id']}")

    store_name_match = re.search(r'"storeName":"(.*?)"', script_content)
    if store_name_match:
        base_data['store_name'] = store_name_match.group(1)
        logging.info(f"Store Name: {base_data['store_name']}")

    og_title_match = re.search(r'"ogTitle":"(.*?)"', script_content)
    if og_title_match:
        base_data['og_title'] = og_title_match.group(1)
        title_parts = base_data['og_title'].split('|')
        if len(title_parts) > 1:
            logging.info(f"Title: {title_parts[1].strip()}")

    keywords_match = re.search(r'"keywords":"(.*?)"', script_content)
    if keywords_match:
        base_data['keywords'] = keywords_match.group(1)
        logging.info(f"Keywords: {base_data['keywords']}")

    description_match = re.search(r'"description":"(.*?)"', script_content)
    if description_match:
        base_data['description'] = description_match.group(1)
        logging.info(f"Description: {base_data['description']}")

    format_trade_count_match = re.search(r'"formatTradeCount":"(.*?)"', script_content)
    if format_trade_count_match:
        base_data['format_trade_count'] = format_trade_count_match.group(1)
        logging.info(f"SOLD: {base_data['format_trade_count']}")

    evarage_star_match = re.search(r'"evarageStar":"(.*?)"', script_content)
    if evarage_star_match:
        base_data['evarage_star'] = evarage_star_match.group(1)
        logging.info(f"Average Star: {base_data['evarage_star']}")

    price_info = re.search(r'"skuAmount":\{"currency":"(.*?)","formatedAmount":"(.*?)","value":(.*?)\}', script_content)
    if price_info:
        base_data['currency'] = price_info.group(1)
        base_data['formated_price'] = price_info.group(2)
        base_data['price'] = price_info.group(3)
        logging.info(f"Currency: {base_data['currency']}")
        logging.info(f"Formatted Price: {base_data['formated_price']}")
        logging.info(f"Price: {base_data['price']}")

    discount_info = re.search(r'"skuActivityAmount":\{"currency":"(.*?)","formatedAmount":"(.*?)","value":(.*?)\}', script_content)
    if discount_info:
        base_data['discount_currency'] = discount_info.group(1)
        base_data['discount_formated_price'] = discount_info.group(2)
        base_data['discount_price'] = discount_info.group(3)
        logging.info(f"Discount Currency: {base_data['discount_currency']}")
        logging.info(f"Discount Formatted Price: {base_data['discount_formated_price']}")
        logging.info(f"Discount Price: {base_data['discount_price']}")

    discount_rate_match = re.search(r'"discount":"(.*?)"', script_content)
    if discount_rate_match:
        base_data['discount_rate'] = discount_rate_match.group(1)
        logging.info(f"Discount Rate: {base_data['discount_rate']}")

    package_component_match = re.search(r'"packageComponent":\{(.*?)\}', script_content)
    if package_component_match:
        package_component_content = package_component_match.group(1)
        package_data = {}
        for item in package_component_content.split(','):
            key, value = item.split(':')
            key = key.strip('"')
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = value.strip('"')
            package_data[key] = value
        base_data['package_component'] = package_data
        for key, value in package_data.items():
            logging.info(f"{key}: {value}")

    property_value_name_matches = re.findall(r'"attrValue":"(.*?)"\s*,"attrName":"(.*?)"', script_content)
    attributes = [{"attrValue": attr_value, "attrName": attr_name} for attr_value, attr_name in property_value_name_matches]
    base_data['attributes'] = attributes
    for attribute in attributes:
        logging.info(attribute)

    inventory_component_match = re.search(r'"inventoryComponent":\{(.*?)\}', script_content)
    if inventory_component_match:
        inventory_component = inventory_component_match.group(1)
        sku_tag_match = re.search(r'"skuTag":"(.*?)"', inventory_component)
        if sku_tag_match:
            base_data['sku_tag'] = sku_tag_match.group(1)
            logging.info(f"SKU Tag: {base_data['sku_tag']}")

        total_quantity_match = re.search(r'"totalQuantity":(\d+)', inventory_component)
        if total_quantity_match:
            base_data['total_quantity'] = int(total_quantity_match.group(1))
            logging.info(f"Total Quantity: {base_data['total_quantity']}")

        total_avail_quantity_match = re.search(r'"totalAvailQuantity":(\d+)', inventory_component)
        if total_avail_quantity_match:
            base_data['total_avail_quantity'] = int(total_avail_quantity_match.group(1))
            logging.info(f"Total Avail Quantity: {base_data['total_avail_quantity']}")
    else:
        logging.info("inventoryComponent not found.")

# Process each URL
for index, row in df.iterrows():
    url = row['URLs']
    logging.info(f"Processing URL: {url}")

    base_data = {
        'Product URL': url,
        'product_title': row['Ürün Başlığı'],
        'price': row['Fiyatı'],
        'original_price': row['Orijinal Fiyatı'],
        'discount_rate': row['İndirim Oranı'],
        'shipping_cost': row['Kargo Ücreti'],
        'category': row['Kategori'],
        'Seo Keyword': row['Seo Keyword']
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script')
        for script in scripts:
            if 'window.runParams' in script.text:
                extract_product_info(script.text, base_data)
                break

        all_data.append(base_data)
        time.sleep(1)  # Add delay between requests

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        continue
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")
        continue

# Save all data to JSON file
with open('output.json', 'w', encoding='utf-8') as file:
    json.dump(all_data, file, ensure_ascii=False, indent=4)

logging.info("Data extraction complete. Output saved to output.json.")

