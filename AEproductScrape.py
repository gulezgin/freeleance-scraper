import requests
from bs4 import BeautifulSoup
import re
import json

url = 'https://tr.aliexpress.com/item/1005005955004075.html?spm=a2g0o.categorymp.prodcutlist.8.7651KPRgKPRgBc&pdp_ext_f=%7B%22sku_id%22%3A%2212000035013164683%22%7D&utparam-url=scene%3Asearch%7Cquery_from%3A'

print("product url : "+ url)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print ("HTTP Error:", errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    print ("OOps: Something Else", err)
else:

    if response.status_code == 200:
      
        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script')

        data = {}

        for script in scripts:

            if 'window.runParams' in script.text:
                run_params_content = script.text

                image_urls_match = re.search(r'"imagePathList":(\[.*?\])', run_params_content)
                if image_urls_match:
                    image_urls_str = image_urls_match.group(1)
                    image_urls = json.loads(image_urls_str)                   
                    image_urls = image_urls[:4]
                    for url in image_urls:
                        print("image url : " + url)
                
                
                format_trade_count_match = re.search(r'"formatTradeCount":"(.*?)"', run_params_content)
                if format_trade_count_match:
                    data['format_trade_count'] = format_trade_count_match.group(1)
                    print("SOLD:", data['format_trade_count'])
                
                evarage_star_match = re.search(r'"evarageStar":"(.*?)"', run_params_content)
                if evarage_star_match:
                    data['evarage_star'] = evarage_star_match.group(1)
                    print("Average Star:", data['evarage_star'])

                keywords_match = re.search(r'"keywords":"(.*?)"', run_params_content)
                if keywords_match:
                    data['keywords'] = keywords_match.group(1)
                    print("Keywords:", data['keywords'])

                og_title_match = re.search(r'"ogTitle":"(.*?)"', run_params_content)
                if og_title_match:
                    data['og_title'] = og_title_match.group(1)
                    print("Title:", data['og_title'])

               
                description_match = re.search(r'"description":"(.*?)"', run_params_content)
                if description_match:
                    data['description'] = description_match.group(1)
                    print("Description:", data['description'])

                
                if 'productPropComponent' in script.text:
                   
                    prop_component_content = script.text

                   
                    property_value_name_matches = re.findall(r'"propertyValueName":"(.*?)".*?"propertyValueDisplayName":"(.*?)"', prop_component_content)

                    
                    attributes = {}
                    for attr_name, attr_value in property_value_name_matches:
                        attributes[attr_value] = attr_name
                        print(f"{attr_value}: {attr_name}")
                    data['attributes'] = attributes

                    
                    colors = re.findall(r'"skuPropertyName":"Renk".*?"skuPropertyValues":\[(.*?)\]', prop_component_content, re.DOTALL)
                    sizes = re.findall(r'"skuPropertyName":"Boyut".*?"skuPropertyValues":\[(.*?)\]', prop_component_content, re.DOTALL)

                    if colors:
                        color_list = re.findall(r'"propertyValueName":"(.*?)"', colors[0])
                        data['colors'] = color_list
                        print("Colors:", color_list)

                    if sizes:
                        size_list = re.findall(r'"propertyValueName":"(.*?)"', sizes[0])
                        data['sizes'] = size_list
                        print("Sizes:", size_list)

                break  

        
        with open('product_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        print("Hata: Sayfa yüklenemedi")
