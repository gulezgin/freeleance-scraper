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
   
    
    # Genel ürün bilgilerini saklamak için bir sözlük oluştur
    base_data = {}
    base_data['Product URL'] = url
    base_data['product_title'] = row['Ürün Başlığı']
    base_data['price'] = row['Fiyatı']
    base_data['original_price'] = row['Orijinal Fiyatı']
    base_data['discount_rate'] = row['İndirim Oranı']
    base_data['shipping_cost'] = row['Kargo Ücreti']
    base_data['category'] = row['Kategori']
    base_data['Seo Keyword'] = row['Seo Keyword']
    print("Ürün Başlığı:", base_data['product_title'])
    print("Fiyatı:", base_data['price'])
    print("Orijinal Fiyatı:", base_data['original_price'])
    print("İndirim Oranı:", base_data['discount_rate'])
    print("Kargo Ücreti:", base_data['shipping_cost'])
    print("Kategori:", base_data['category'])
    print("Seo Keyword", base_data['Seo Keyword'])
    
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
                    base_data['image_urls'] = image_urls 
                    # URL'leri yazdır
                    for img_url in image_urls:
                        print("Image URL:", img_url)
               
                # Eğer içerikte "productId" varsa
                if 'productId' in script.text:
                    # productId değerini bul
                    product_id_match = re.search(r'"productId":"(.*?)"', run_params_content)
                    if product_id_match:
                        base_data['product_id'] = product_id_match.group(1)
                        print("Product ID:", base_data['product_id'])
                        
                # productId değerini kazımak için regex deseni
                pattern = r'\\"productId\\":(\d+)'
                match = re.search(pattern, run_params_content)
                if match:
                    product_id = match.group(1)
                    print("productId:", product_id)
                    base_data['product_id'] = product_id
                else:
                    print("productId bulunamadı.")
                    
                store_name_match = re.search(r'"storeName":"(.*?)"', run_params_content)
                if store_name_match:
                    store_name = store_name_match.group(1)
                    base_data['store_name'] = store_name
                    print("Mağaza Adı:", store_name)
                else:
                    print("storeName bulunamadı.")

                # "ogTitle" değerini bul
                og_title_match = re.search(r'"ogTitle":"(.*?)"', run_params_content)
                if og_title_match:
                    base_data['og_title'] = og_title_match.group(1)
                    title_parts = base_data['og_title'].split('|')
                    if len(title_parts) > 1:
                        print("Title:", title_parts[1].strip())
                    
                # "keywords" değerini bul
                keywords_match = re.search(r'"keywords":"(.*?)"', run_params_content)
                if keywords_match:
                    base_data['keywords'] = keywords_match.group(1)
                    print("Keywords:", base_data['keywords'])

                # "description" değerini bul
                description_match = re.search(r'"description":"(.*?)"', run_params_content)
                if description_match:
                    base_data['description'] = description_match.group(1)
                    print("Description:", base_data['description'])               
                                
                # "formatTradeCount" değerini bul
                format_trade_count_match = re.search(r'"formatTradeCount":"(.*?)"', run_params_content)
                if format_trade_count_match:
                    base_data['format_trade_count'] = format_trade_count_match.group(1)
                    print("SOLD:", base_data['format_trade_count'])
                
                # "evarageStar" değerini bul
                evarage_star_match = re.search(r'"evarageStar":"(.*?)"', run_params_content)
                if evarage_star_match:
                    base_data['evarage_star'] = evarage_star_match.group(1)
                    print("Average Star:", base_data['evarage_star'])
                
                # Fiyat bilgilerini çek
                price_info = re.search(r'"skuAmount":\{"currency":"(.*?)","formatedAmount":"(.*?)","value":(.*?)\}', run_params_content)
                if price_info:
                    base_data['currency'] = price_info.group(1)
                    base_data['formated_price'] = price_info.group(2)
                    base_data['price'] = price_info.group(3)
                    print("Currency:", base_data['currency'])
                    print("Formatted Price:", base_data['formated_price'])
                    print("Price:", base_data['price'])

                discount_info = re.search(r'"skuActivityAmount":\{"currency":"(.*?)","formatedAmount":"(.*?)","value":(.*?)\}', run_params_content)
                if discount_info:
                    base_data['discount_currency'] = discount_info.group(1)
                    base_data['discount_formated_price'] = discount_info.group(2)
                    base_data['discount_price'] = discount_info.group(3)
                    print("Discount Currency:", base_data['discount_currency'])
                    print("Discount Formatted Price:", base_data['discount_formated_price'])
                    print("Discount Price:", base_data['discount_price'])
                
                discount_rate_match = re.search(r'"discount":"(.*?)"', run_params_content)
                if discount_rate_match:
                    base_data['discount_rate'] = discount_rate_match.group(1)
                    print("Discount Rate:", base_data['discount_rate'])
                    
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
                    base_data['package_component'] = package_data
                    for key, value in package_data.items():
                        print(f"{key}: {value}")
                
                # Eğer içerikte "productPropComponent" varsa
                if 'productPropComponent' in script.text:
                    # Script içeriğini yazdır
                    prop_component_content = script.text

                    # "attrValue" ve "attrName" değerlerini bul
                    attr_value_matches = re.findall(r'"attrValue":"(.*?)"', prop_component_content)
                    property_value_name_matches = re.findall(r'"attrValue":"(.*?)".*?"attrName":"(.*?)"', prop_component_content)

                    # Her bir eşleşmeyi yazdır ve sakla
                    attributes = []
                    for attr_value, attr_name in property_value_name_matches:
                        attribute = {"attrValue": attr_value, "attrName": attr_name}
                        attributes.append(attribute)
                        print(attribute)
                    
                    base_data['attributes'] = attributes
                
                # "inventoryComponent" değerini bul
                inventory_component_match = re.search(r'"inventoryComponent":\{(.*?)\}', run_params_content)
                if inventory_component_match:
                    inventory_component = inventory_component_match.group(1)

                    # "skuTag" değerini bulma
                    sku_tag_match = re.search(r'"skuTag":"(.*?)"', inventory_component)
                    if sku_tag_match:
                        base_data['sku_tag'] = sku_tag_match.group(1)
                        print("SKU Tag:", base_data['sku_tag'])

                    # "totalQuantity" değerini bulma
                    total_quantity_match = re.search(r'"totalQuantity":(\d+)', inventory_component)
                    if total_quantity_match:
                        base_data['total_quantity'] = int(total_quantity_match.group(1))
                        print("total quantity:", base_data['total_quantity'])

                    # "totalAvailQuantity" değerini bulma
                    total_avail_quantity_match = re.search(r'"totalAvailQuantity":(\d+)', inventory_component)
                    if total_avail_quantity_match:
                        base_data['total_avail_quantity'] = int(total_avail_quantity_match.group(1))
                        print("total avail quantity:", base_data['total_avail_quantity'])
                else:
                    print("inventoryComponent bulunamadı.")
                    
                    
        # Renkler ve fotoğraflar için regex
                detail1_pattern = re.compile(r'{"skuColorValue":"[^"]+","skuPropertyTips":"[^"]+","propertyValueName":"([^"]+)","propertyValueId":(\d+),"skuPropertyImagePath":"([^"]+)"')
                details1 = detail1_pattern.findall(run_params_content)
                print(details1)

                # Bedenler için regex
                detail2_pattern = re.compile(r'{"skuPropertyTips":"[^"]*","propertyValueName":"([^"]*)","propertyValueId":(\d+),"skuPropertyValueTips":"[^"]*","skuPropertyValueShowOrder":\d+,"propertyValueIdLong":\d+,"propertyValueDisplayName":"[^"]*"}')
                details2 = detail2_pattern.findall(run_params_content)
                print(details2)

                # Varyantlar için regex
                variant_pattern = re.compile(r'"skuPropIds":"(\d+),(\d+)".+?"inventory":(\d+).+?"skuActivityAmount":\{"currency":"[^"]+","formatedAmount":"[^"]+","value":([\d\.]+)')
                variants = variant_pattern.findall(run_params_content)
                print("Variants:", variants)

                # İki boyutlu varyantları işleme
                for variant in variants:
                    variant_data = base_data.copy()
                    variant_data['detail1_id'] = variant[0]
                    variant_data['detail2_id'] = variant[1]
                    variant_data['inventory'] = variant[2]
                    variant_data['sku_activity_amount'] = variant[3]

                    # Her varyant için ilgili renk ve beden bilgilerini ekle
                    for detail1 in details1:
                        if detail1[2] == variant[0]:
                            variant_data['detail1'] = detail1[0]
                            variant_data['image_path'] = detail1[2]
                            break

                    for detail2 in details2:
                        if detail2[1] == variant[1]:
                            variant_data['detail2'] = detail2[0]
                            break

                    # Varyant verilerini JSON olarak yazdır
                    print(json.dumps(variant_data, ensure_ascii=False, indent=4))

                    # Varyant verilerini dosyaya yaz
                    with open('a.json', 'a', encoding='utf-8') as f:
                        json.dump(variant_data, f, ensure_ascii=False, indent=4)
                        f.write(',\n')

                # Tek boyutlu varyantlarda envanter kontrolü
                single_dimension_inventory_pattern = re.compile(r'"inventory":(\d+).+?"skuActivityAmount":\{"currency":"[^"]+","formatedAmount":"[^"]+","value":([\d\.]+)')

                # Sadece renk bilgisi olan varyantlar
                if details1:
                    for detail1 in details1:
                        variant_data = base_data.copy()
                        variant_data['detail1_id'] = detail1[1]
                        variant_data['detail1'] = detail1[0]
                        variant_data['image_path'] = detail1[2]

                        inventory_match = single_dimension_inventory_pattern.search(run_params_content)
                        if inventory_match:
                            variant_data['inventory'] = inventory_match.group(1)
                            variant_data['sku_activity_amount'] = inventory_match.group(2)

                        print(json.dumps(variant_data, ensure_ascii=False, indent=4))

                        with open('a', 'a', encoding='utf-8') as f:
                            json.dump(variant_data, f, ensure_ascii=False, indent=4)
                            f.write(',\n')

                # Sadece beden bilgisi olan varyantlar
                if details2:
                    for detail2 in details2:
                        variant_data = base_data.copy()
                        variant_data['detail2_id'] = detail2[1]
                        variant_data['detail2'] = detail2[0]

                        # Genel bir image_path bulmak için renklerin listesini kontrol et
                        if details1:
                            variant_data['image_path'] = details1[0][2]  # İlk rengin image_path'i

                        inventory_match = single_dimension_inventory_pattern.search(run_params_content)
                        if inventory_match:
                            variant_data['inventory'] = inventory_match.group(1)
                            variant_data['sku_activity_amount'] = inventory_match.group(2)

                        print(json.dumps(variant_data, ensure_ascii=False, indent=4))

                        with open('a.json', 'a', encoding='utf-8') as f:
                            json.dump(variant_data, f, ensure_ascii=False, indent=4)
                            f.write(',\n')
                else:
                    print("Hata: Sayfa yüklenemedi")

    # Her ürün isteği arasında rastgele bir süre bekle (1 ile 4 saniye arasında)
    sleep_time = random.uniform(1, 4)
    print(f"Bekleme süresi: {sleep_time:.2f} saniye")
    time.sleep(sleep_time)
