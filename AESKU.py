import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import time
import random

# Headers ekleyelim (User-Agent)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Excel dosyasını oku
try:
    df = pd.read_excel('a.xlsx')
except FileNotFoundError:
    print("Hata: Excel dosyası bulunamadı.")
    exit()

# Her bir URL için işlem yap
for index, row in df.iterrows():
    url = row['URLs']  # URL'ye 'https' şeması ekle
    print(80*"-")
    print("Product URL:", url)
    
    # Verileri saklamak için bir sözlük oluştur
    data = {}
    data['Product URL'] = url
    data['product_title'] = row['Ürün Başlığı']
    data['price'] = row['Fiyatı']
    data['original_price'] = row['Orijinal Fiyatı']
    data['discount_rate'] = row['İndirim Oranı']
    data['shipping_cost'] = row['Kargo Ücreti']
    data['category'] = row['Kategori']
    data['Seo Keyword'] = row['Seo Keyword']
    print("Ürün Başlığı:", data['product_title'])
    print("Fiyatı:", data['price'])
    print("Orijinal Fiyatı:", data['original_price'])
    print("İndirim Oranı:", data['discount_rate'])
    print("Kargo Ücreti:", data['shipping_cost'])
    print("Kategori:", data['category'])
    print("Seo Keyword", data['Seo Keyword'])

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Hata:", e)
        continue
    
    if response.status_code == 200:
        # BeautifulSoup kullanarak HTML içeriğini analiz et
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tüm <script> etiketlerini bul
        scripts = soup.find_all('script')

        # Her bir <script> etiketinin içeriğini kontrol et
        for script in scripts:
            # Eğer içerikte "window.runParams" varsa
            if 'window.runParams' in script.text:
                # Script içeriğini yazdır
                run_params_content = script.text
                
                # imagePathList'den fotoğraf URL'lerini al
                image_urls_match = re.search(r'"imagePathList":(\[.*?\])', run_params_content)
                if image_urls_match:
                    image_urls_str = image_urls_match.group(1)
                    image_urls = json.loads(image_urls_str)
                    # Maksimum 4 URL al
                    image_urls = [url.replace('.png', '.jpg') for url in image_urls[:4]]  # PNG'yi JPG'ye dönüştür
                    data['image_urls'] = image_urls 
                    # URL'leri yazdır
                    for img_url in image_urls:
                        print("Image URL:", img_url)
               
                # Eğer içerikte "productId" varsa
                if 'productId' in script.text:
                    # productId değerini bul
                    product_id_match = re.search(r'"productId":"(.*?)"', run_params_content)
                    if product_id_match:
                        data['product_id'] = product_id_match.group(1)
                        print("Product ID:", data['product_id'])
                        
                # productId değerini kazımak için regex deseni
                pattern = r'\\"productId\\":(\d+)'

                # Deseni kullanarak eşleşmeyi bul
                match = re.search(pattern, run_params_content)

                if match:
                    # productId değerini al
                    product_id = match.group(1)
                    print("productId:", product_id)

                    
                store_name_match = re.search(r'"storeName":"(.*?)"', run_params_content)
                if store_name_match:
                    store_name = store_name_match.group(1)
                    print("Mağaza Adı:", store_name)

                # "ogTitle" değerini bul
                og_title_match = re.search(r'"ogTitle":"(.*?)"', run_params_content)
                if og_title_match:
                    data['og_title'] = og_title_match.group(1)
                    title_parts = data['og_title'].split('|')
                    if len(title_parts) > 1:
                        print("Title:", title_parts[1].strip())
                    
                # "keywords" değerini bul
                keywords_match = re.search(r'"keywords":"(.*?)"', run_params_content)
                if keywords_match:
                    data['keywords'] = keywords_match.group(1)
                    print("Keywords:", data['keywords'])

                # "description" değerini bul
                description_match = re.search(r'"description":"(.*?)"', run_params_content)
                if description_match:
                    data['description'] = description_match.group(1)
                    print("Description:", data['description'])               
                                
                # "formatTradeCount" değerini bul
                format_trade_count_match = re.search(r'"formatTradeCount":"(.*?)"', run_params_content)
                if format_trade_count_match:
                    data['format_trade_count'] = format_trade_count_match.group(1)
                    print("SOLD:", data['format_trade_count'])
                
                # "evarageStar" değerini bul
                evarage_star_match = re.search(r'"evarageStar":"(.*?)"', run_params_content)
                if evarage_star_match:
                    data['evarage_star'] = evarage_star_match.group(1)
                    print("Average Star:", data['evarage_star'])
                
                # Fiyat bilgilerini çek
                price_info = re.search(r'"skuAmount":\{"currency":"(.*?)","formatedAmount":"(.*?)","value":(.*?)\}', run_params_content)
                if price_info:
                    data['currency'] = price_info.group(1)
                    data['formated_price'] = price_info.group(2)
                    data['price'] = price_info.group(3)
                    print("Currency:", data['currency'])
                    print("Formatted Price:", data['formated_price'])
                    print("Price:", data['price'])

                discount_info = re.search(r'"skuActivityAmount":\{"currency":"(.*?)","formatedAmount":"(.*?)","value":(.*?)\}', run_params_content)
                if discount_info:
                    data['discount_currency'] = discount_info.group(1)
                    data['discount_formated_price'] = discount_info.group(2)
                    data['discount_price'] = discount_info.group(3)
                    print("Discount Currency:", data['discount_currency'])
                    print("Discount Formatted Price:", data['discount_formated_price'])
                    print("Discount Price:", data['discount_price'])
                
                discount_rate_match = re.search(r'"discount":"(.*?)"', run_params_content)
                if discount_rate_match:
                    data['discount_rate'] = discount_rate_match.group(1)
                    print("Discount Rate:", data['discount_rate'])
                    
                # "packageComponent" değerlerini bul
                package_component_match = re.search(r'"packageComponent":\{(.*?)\}', run_params_content)
                if package_component_match:
                    package_component_content = package_component_match.group(1)
                    # Virgülle ayrılan JSON değerlerini tek tek işleyerek bir dict'e dönüştürelim
                    package_data = {}
                    for item in package_component_content.split(','):
                        key, value = item.split(':')
                        key = key.strip('"')
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            value = value.strip('"')
                        package_data[key] = value
                    data['package_component'] = package_data
                    for key, value in package_data.items():
                        print(f"{key}: {value}")
                
                # Eğer içerikte "productPropComponent" varsa
                if 'productPropComponent' in script.text:
                    # Script içeriğini yazdır
                    prop_component_content = script.text

                    # "attrValue" ve "propertyValueName" değerlerini bul
                    attr_value_matches = re.findall(r'"attrValue":"(.*?)"', prop_component_content)
                    property_value_name_matches = re.findall(r'"attrValue":"(.*?)".*?"attrName":"(.*?)"', prop_component_content)

                    # Her bir eşleşmeyi yazdır ve sakla
                    attributes = {}
                    for attr_name, attr_value in property_value_name_matches:
                        attributes[attr_value] = attr_name
                        print(attr_value + ":", attr_name)
                    data['attributes'] = attributes
                    
                # JSON içindeki "inventoryComponent" bölümünü bulma
                inventory_component_match = re.search(r'"inventoryComponent":{[^{}]*}', run_params_content)
                if inventory_component_match:
                    inventory_component = inventory_component_match.group(0)

                    # "totalQuantity" değerini bulma
                    total_quantity_match = re.search(r'"totalQuantity":(\d+)', inventory_component)
                    if total_quantity_match:
                        total_quantity = int(total_quantity_match.group(1))
                        print("total quantity:", total_quantity)

                    # "totalAvailQuantity" değerini bulma
                    total_avail_quantity_match = re.search(r'"totalAvailQuantity":(\d+)', inventory_component)
                    if total_avail_quantity_match:
                        total_avail_quantity = int(total_avail_quantity_match.group(1))
                        print("total avail quantity:", total_avail_quantity)

                    
                # Renkler ve fotoğraflar için regex
                color_pattern = re.compile(r'{"skuColorValue":"[^"]+","skuPropertyTips":"[^"]+","propertyValueName":"([^"]+)","propertyValueId":(\d+),"skuPropertyImagePath":"([^"]+)"')
                colors = color_pattern.findall(run_params_content)
                data['colors'] = [{'Property Value Name': color[0], 'Property Value ID': color[1], 'Image Path': color[2]} for color in colors]

                # Bedenler için regex
                size_pattern = re.compile(r'{"skuPropertyTips":"[^"]+","propertyValueName":"([^"]+)","propertyValueId":(\d+)')
                sizes = size_pattern.findall(run_params_content)
                data['sizes'] = [{'Property Value Name': size[0], 'Property Value ID': size[1]} for size in sizes]

                # Varyantlar için regex
                variant_pattern = re.compile(r'"skuPropIds":"(\d+),(\d+)".+?"inventory":(\d+).+?"skuActivityAmount":\{"currency":"[^"]+","formatedAmount":"[^"]+","value":([\d\.]+)')
                variants = variant_pattern.findall(run_params_content)
                data['variants'] = [{'Color ID': variant[0], 'Size ID': variant[1], 'Inventory': variant[2], 'SKU Activity Amount': variant[3]} for variant in variants]

                # Elde edilen verileri yazdır
                
                for color in colors:
                    print(f"Property Value Name: {color[0]}, Property Value ID: {color[1]}, Image Path: {color[2]}")

               
                for size in sizes:
                    print(f"Property Value Name: {size[0]}, Property Value ID: {size[1]}")

              
                for variant in variants:
                    print(f"Color ID: {variant[0]}, Size ID: {variant[1]}, Inventory: {variant[2]}, SKU Activity Amount: {variant[3]}")
                
                # Variantları oluşturmak için skuPropertyJson'ı bul
                sku_property_json_match = re.search(r'"skuPropertyJson":"(\[\[.*?\]\])"', run_params_content)
                if sku_property_json_match:
                    sku_property_json_str = sku_property_json_match.group(1).replace('\\"', '"')
                    sku_property_json = json.loads(sku_property_json_str)

                    data['sku_property_json'] = sku_property_json
                    print("SKU Property JSON:", sku_property_json)
                    
                    # Her varyantı skuPropertyJson'dan kontrol ederek oluştur
                    for variant in variants:
                        color_id = int(variant[0])
                        size_id = int(variant[1])
                        for prop_set in sku_property_json:
                            if color_id in prop_set and size_id in prop_set:
                                variant_data = {
                                    'color_id': color_id,
                                    'size_id': size_id,
                                    'inventory': int(variant[2]),
                                    'price': float(variant[3])
                                }
                                print("Variant Data:", variant_data)

        # Verileri JSON olarak kaydet
        with open('b.json', 'a', encoding='utf-8') as f:  # 'a' append mode to avoid overwriting
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write(',\n')  # JSON objects separated by a comma for multiple entries
    else:
        print("Hata: Sayfa yüklenemedi")

    # Her ürün isteği arasında rastgele bir süre bekle (3 ile 7 saniye arasında)
    sleep_time = random.uniform(1, 4)
    print(f"Bekleme süresi: {sleep_time:.2f} saniye")
    time.sleep(sleep_time)
