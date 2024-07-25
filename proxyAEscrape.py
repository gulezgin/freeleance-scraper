import pandas as pd
import requests
import re
import json
from bs4 import BeautifulSoup
from time import sleep

# Proxy bilgileri
proxy_host = "brd.superproxy.io"
proxy_port = "9222"
proxy_username = "brd-customer-hl_74ea092b-zone-scraping_browser2"
proxy_password = "a8jj7of3deav"

# Yeni kullanıcı ajanı
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

# HTML içeriğini bir URL'den çekme fonksiyonu
def get_html_from_url(url):
    # Proxy bilgisini ayarla
    proxy = {
        "http": f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}",
        "https": f"https://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    }
    
    # Kullanıcı ajanını ayarla
    headers = {'User-Agent': user_agent}
    
    # İstek gönder
    response = requests.get(url, headers=headers, proxies=proxy)
    
    # Yanıt kodunu kontrol et
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch HTML content: {response.status_code}")

# Description çekme fonksiyonu
def extract_description(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    description_tag = soup.find("meta", attrs={"name": "description"})
    if description_tag:
        return description_tag["content"]
    else:
        return None

# Excel dosyasından URL'leri al ve işlem yap
def process_urls_from_excel(excel_file):
    # Excel dosyasını yükle
    df = pd.read_excel(excel_file)

    # URL sütununu al
    urls = df["URLs"].tolist()

    # Her bir URL için işlem yap
    for url in urls:
        print("-" * 50)
        url = url.strip()  # Boşlukları temizle
        html_content = get_html_from_url(url)  # HTML içeriğini al

        # Description çıkar
        description = extract_description(html_content)
        print(f"Description: {description}")

        script = html_content

        # title, attrValue ve attrName değerlerini bulmak için regex deseni
        title_pattern = r'"title":"(.*?)\s*\|\s*- AliExpress"'
        attr_pattern = r'"attrValue":"(.*?)","attrName":"(.*?)"'
        price_pattern = r'"formatedAmount":"(.*?)".*?"discountTips":"(.*?)".*?"skuAmountLocal":"(.*?)"'
        patternR = r'"evarageStar":"(.*?)"'
        patternsold = r'"formatTradeCount":"(.*?)"'
        patterncol = r'"propertyValueName":"(.*?)"'
        patternsize = r'"propertyValueName":"(S|M|L|XL|XXL|XXXL)"'
        patternimg = r'"(https://[^"]+.jpg)"'

        # Metindeki tüm eşleşmeleri bul
        title_match = re.search(title_pattern, script)
        attr_matches = re.findall(attr_pattern, script)
        price_match = re.search(price_pattern, script)
        match = re.search(patternR, script)
        sold_count_match = re.search(patternsold, script)
        property_values = re.findall(patterncol, script)
        size_values = re.findall(patternsize, script)
        image_urls = re.findall(patternimg, script)

        # title değerini yazdır
        if title_match:
            title = title_match.group(1).strip()

        # Metindeki eşleşmeleri yazdır
        for attr_match in attr_matches:
            print(f"{attr_match[1]} = {attr_match[0]}")

        # Metindeki eşleşmeyi bul
        price = None
        discounted_price = None
        discount_tip = None
        if price_match:
            price = price_match.group(1)
            discount_tip = price_match.group(2)
            discounted_price_match = re.search(r'"skuActivityAmountLocal":"(.*?)\|', script)
            if discounted_price_match:
                discounted_price = discounted_price_match.group(1)

        rating = None
        if match:
            rating = match.group(1)

        sold_count = None
        if sold_count_match:
            sold_count = sold_count_match.group(1)

        renkler = [value for value in property_values if value not in ['S', 'M', 'L', 'XL', 'XXL', 'XXXL']]

        # İlk dört URL'yi al
        first_four_urls = image_urls[:4]

        # JSON veri yapısını oluştur
        data = {
            "Ürün Adı": title,
            "Açıklama": description,
            "Fiyat": price,
            "İndirimli Fiyat": discounted_price,
            "İndirim": discount_tip,
            "Rating": rating,
            "Satıldı": sold_count,
            "Renk Değerleri": renkler,
            "Beden Değerleri": size_values,
            "Fotoğraf URL'leri": first_four_urls,
            "URL": url  # URL'yi ekle
        }

        # JSON formatına dönüştür ve yazdır
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        print(json_data)

        # Yavaşlatma ekleyin
        sleep(5)  # Örneğin, her istek arasında 5 saniye bekleme ekleyin

# Kullanım
excel_file_path = "C:/Users/msı/jupyterNOTEBOOK/webscrapingALİEXPRESS/url2.xlsx"  # Excel dosyanızın adını ve yolunu buraya yazın
process_urls_from_excel(excel_file_path)
