import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def get_html_content(url):
    """
    Function to combine HTML from given URL.
    """
    if url:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            raise requests.HTTPError(f"HTTP Error {response.status_code}")
    else:
        return None

def extract_image_urls(html_content):
    """
    Function that extracts image URLs from HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    image_urls = []

    thumbnail_nav = soup.find('div', class_='ThumbNailNavClip')
    if thumbnail_nav:
        thumbnails = thumbnail_nav.find_all('li')
        for i, thumbnail in enumerate(thumbnails, start=1):
            img_tag = thumbnail.find('img')
            if img_tag:
                image_url = img_tag.get('data-src') or img_tag.get('src')
                if image_url:
                    image_urls.append((f"photo {i}", image_url))
    
    image_info = {}
    for index, (label, url) in enumerate(image_urls, start=1):
        image_info[f"image_{index}_label"] = label
        image_info[f"image_{index}_url"] = url

    return image_info

def extract_default_item_colour(url):
    """
    Function that extracts the default product color from the given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        shot_data_script = soup.find('script', id='shotData')
        if shot_data_script:
            shot_data = shot_data_script.string
            default_item_colour = shot_data.split('"DefaultItemColour":"')[1].split('"')[0]
            return default_item_colour
        else:
            return "Error: shotData script not found"
    except Exception as e:
        return f"Error: {e}"

def extract_script_data(sdata):
    """
    Function that extracts product information from JSON data.
    """
    if sdata:
        try:
            extracted_data = []
            styles = sdata.get("Styles", [])
            for style in styles:
                fits = style.get("Fits", [])
                for fit in fits:
                    items = fit.get("Items", [])
                    for item in items:
                        extracted_item = {
                            "ToneOfVoice": style.get("ToneOfVoice", ""),
                            "IsSoldOut": item.get("IsSoldOut", ""),
                            "IsDiscount": item.get("IsDiscount", ""),
                            "PriceHistory": item.get("PriceHistory", ""),
                            "SalePlainPrice": item.get("SalePlainPrice", ""),
                            "SaleHighlightPrice": item.get("SaleHighlightPrice", ""),
                            "WashingInstructions": item.get("WashingInstructions", ""),
                            "Composition": item.get("Composition", ""),
                            "SearchDescription": item.get("SearchDescription", ""),
                            "Options": [option.get("Nm", "") for option in item.get("Options", [])]
                        }
                        extracted_data.append(extracted_item)
            return extracted_data if extracted_data else None  
        except Exception as e:
            print("An error occurred while processing script data:", e)
            return None
    else:
        return None

def scrape_url(url):
    """
    The main function that extracts data from the given URL.
    """
    try:
        html_content = get_html_content(url)

        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')

            script_tag = soup.find('script', type='application/ld+json')
            script = soup.find('script', id='shotData')

            if script:
                script_content = script.contents[0]
                start_index = script_content.find('{"ShotBasePath"')
                end_index = script_content.rfind('};') + 1
                json_content = script_content[start_index:end_index]
                
                sdata = json.loads(json_content)
                extracted_data = extract_script_data(sdata)
            else:
                print("Script tag with JSON data not found.")
                extracted_data = None

            if script_tag:
                json_data = json.loads(script_tag.string)
                if 'image' in json_data and 'description' in json_data:
                    image_url = json_data['image']
                    description = json_data['description']
                else:
                    print("Image URL or description not found in JSON data.")
                    image_url, description = None, None
            else:
                print("Script tag with JSON data not found.")
                image_url, description = None, None
            
            return html_content, extracted_data, image_url, description
        else:
            print("Failed to retrieve HTML content for URL:", url)
            return None, None, None, None
    except Exception as e:
        print("An error occurred while scraping URL:", e)
        return None, None, None, None

def process_style_info(style_tag, html_content):
    """
    Function that processes style information.
    """
    price_tag = style_tag.find('div', class_='nowPrice')
    price = price_tag.span.text if price_tag else "Price not available"

    colour_chips = style_tag.find('div', class_='colourChipsContainer')
    colours = [chip['data-value'] for chip in colour_chips.find_all('li', class_='chipItem')] if colour_chips else []

    size_chips = style_tag.find('div', class_='sizeChipsContainer')
    sizes = [chip['data-value'] for chip in size_chips.find_all('li', class_='chipItem')] if size_chips else []
    default_color = soup.find("article")["data-colour"]
    
    stock_details = {}
    if size_chips:
        for chip in size_chips.find_all('li', class_='chipItem'):
            size = chip['data-value']
            data_value = chip['data-value']
            data_size = chip['data-size']
            stock_status = chip['data-stockstatus']
            stock_message = chip['data-stockmessage']
            stock_price = chip['data-price']
            stock_details[size] = {
                "stock_status": stock_status,
                "stock_message": stock_message,
                "stock_price": stock_price
            }

    return price, colours, sizes, default_color, stock_details

def process_output_data(style_info, extracted_data, image_url, description, image_info, default_color, url):
    """
    The function that processes the output data.
    """
    output_data = []
    for size, details in style_info["stock_details"].items():
        stock_status = details["stock_status"]
        if stock_status == "INSTOCK":
            stock_message = "In stock"
        elif stock_status == "OUTOFSTOCK":
            stock_message = "Out of stock"
        else:
            stock_message = "Stock status unknown"

        output_item = {
            "Product URL": url,
            "id": style_info.get('id'),
            "styleid": style_info.get('data-styleid'),
            "targetitem": style_info.get('data-targetitem'),
            "stylenumber": style_info.get('data-stylenumber'),
            "itemname": style_info.get('data-itemname'),
            "department": style_info.get('data-department'),
            "gender": style_info.get('data-gender'),
            "colours": style_info.get('colours'),
            "brand": style_info.get('data-brand'),
            "category": style_info.get('data-category'),
            "collection": style_info.get('data-collection'),
            "price": style_info["price"],
            "IsDiscount": extracted_data[0]["IsDiscount"] if extracted_data else None,
            "PriceHistory": extracted_data[0]["PriceHistory"] if extracted_data else None,
            "SalePlainPrice": extracted_data[0]["SalePlainPrice"] if extracted_data else None,
            "SaleHighlightPrice": extracted_data[0]["SaleHighlightPrice"] if extracted_data else None,
            "optionNumber": size,
            "Options": extracted_data[0]["Options"] if extracted_data else None,
            "Data-Size": details["data_size"],
            "Data-Value": details["data_value"],
            "stock_status": stock_status,
            "stock_message": stock_message,
            "stock_price": details["stock_price"],
            "IsSoldOut": extracted_data[0]["IsSoldOut"] if extracted_data else None,
            "tone_of_voice": extracted_data[0]["ToneOfVoice"] if extracted_data else None,
            "composition": extracted_data[0]["Composition"] if extracted_data else None,
            "WashingInstructions": extracted_data[0]["WashingInstructions"] if extracted_data else None,
            "description": description,
            "SearchDescription": extracted_data[0]["SearchDescription"] if extracted_data else None,
            "default image_url": image_url,
            "images": image_info,
            "Color": default_color,
            "DefaultItemColour": extract_default_item_colour(url)
        }
        output_data.append(output_item)
    return output_data

def main():
    """
    Main program flow.
    """
    folder_path = "C:/Users/msı/jupyterNOTEBOOK/.."
    excel_files = [file for file in os.listdir(folder_path) if file.endswith(".xlsx")]

    for excel_file in excel_files:
        df = pd.read_excel(os.path.join(folder_path, excel_file))

        output_data = []

        for index, row in df.iterrows():
            url = row["Product URLs"]  

            if pd.notnull(url) and isinstance(url, str):
                html_content, extracted_data, image_url, description = scrape_url(url)

                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    style_tag = soup.find('article', id='Style2001')

                    if style_tag:
                        style_info = process_style_info(style_tag, html_content)
                        image_info = extract_image_urls(html_content)
                        default_color = soup.find("article")["data-colour"]
                        output_data.extend(process_output_data(style_info, extracted_data, image_url, description, image_info, default_color, url))
                    else:
                        print("Style information not found for URL:", url)
                else:
                    print("Failed to retrieve HTML content for URL:", url)
            else:
                print("Invalid URL or URL missing, line:", index)
                continue  

        output_df = pd.DataFrame(output_data)
        output_excel_file = os.path.join(folder_path, excel_file.split(".xlsx")[0] + "_scraped_data.xlsx")
        output_df.to_excel(output_excel_file, index=False)
        print("Output data saved to file:", output_excel_file)

if __name__ == "__main__":
    main()
