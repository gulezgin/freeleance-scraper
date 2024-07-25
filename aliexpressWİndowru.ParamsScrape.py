import requests
from bs4 import BeautifulSoup

# Web sayfasının URL'si
url = 'https://tr.aliexpress.com/item/1005004790316589.html?spm=a2g0o.categorymp.prodcutlist.19.22ffXxIDXxIDsD&pdp_ext_f=%7B%22sku_id%22%3A%2212000030496963750%22%7D&utparam-url=scene%3Asearch%7Cquery_from%3A'

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7',
    'Cookie': 'uid=dbe08f3a-8eb2-481f-ae45-0549f34f0698; receive-cookie-deprecation=1; cto_bundle=_DHpVV9kQzB5ZE0xVmdkcEM1NExCQmZhVHpmMk9pZTN5QjBEem1jQU9jSTB3UnUwaDI1Y2NsSDlOaWE1JTJCdHdBSnoxZTc',
    'Referer': 'https://tr.aliexpress.com/',
    'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}


# Web sayfasının kaynak kodunu indir
response = requests.get(url, headers=headers)

# Response başarılıysa devam et
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
                print(script.text)
                break  # İlk eşleşmeyi bulduktan sonra döngüden çık
else:
    print("Hata: Sayfa yüklenemedi")
